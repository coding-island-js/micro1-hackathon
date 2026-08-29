"""Charge endpoint for the payments service.

`Clock`, `validate_params`, `before_execute` and `_execute` are PROVIDED. Do not change their
behaviour -- the billing tests and the rest of the service depend on them.

Implement ChargeAPI.post_charge.
"""
from __future__ import annotations

import json
import secrets
import threading
from dataclasses import dataclass


class Clock:
    """PROVIDED. The service's only source of time. Do not call time.time() directly."""

    def __init__(self, now: float = 1_700_000_000.0) -> None:
        self._now = now

    def now(self) -> float:
        return self._now

    def advance(self, seconds: float) -> None:
        self._now += seconds


def validate_params(params: dict) -> str | None:
    """PROVIDED. Returns an error message, or None if the request is well formed.

    This runs before the charge is attempted -- nothing has happened yet when it fails.
    """
    amount = params.get("amount")
    if not isinstance(amount, int) or isinstance(amount, bool) or amount <= 0:
        return "amount must be a positive integer number of cents"
    if not isinstance(params.get("currency"), str):
        return "currency is required"
    return None


@dataclass
class _IdempotencyRecord:
    """One stored outcome for an idempotency key: what it was called with, what it returned,
    and when it stops being valid."""

    fingerprint: str
    result: tuple[int, dict]
    expires_at: float


class ChargeAPI:
    """The charge endpoint.

    Contract (fixed -- clients call it this way):

        api = ChargeAPI(clock)
        status, body = api.post_charge(params, idempotency_key=None)

    `params` is the request body, e.g. {"amount": 2500, "currency": "usd"}.
    `status` is an HTTP status code, `body` is a JSON-serialisable dict.

    `self.executed` is the ledger of charges the upstream processor actually attempted.
    Money moves once per entry.
    """

    # Idempotency keys are honoured for this long after first use, matching the documented
    # 24-hour window (e.g. Stripe). After that a reused key starts a fresh charge.
    _KEY_TTL_SECONDS = 24 * 60 * 60
    _MAX_KEY_LENGTH = 255

    def __init__(self, clock: Clock) -> None:
        self.clock = clock
        self.executed: list[dict] = []
        self._idempotent_results: dict[str, _IdempotencyRecord] = {}
        # Guards creation of per-key locks below.
        self._locks_guard = threading.Lock()
        # One lock per idempotency key: a second request with the same key blocks here for
        # the duration of the first request's processing, instead of racing it into _execute.
        self._key_locks: dict[str, threading.Lock] = {}

    # ---------------------------------------------------------------- provided, do not change

    def before_execute(self) -> None:
        """PROVIDED extension point, called at the moment the charge starts.

        Operations monkey-patches this in staging to inject latency and to replay traffic.
        `_execute` calls it for you -- just don't remove the call to `_execute`.
        """

    def _execute(self, params: dict) -> tuple[int, dict]:
        """PROVIDED. Hands the charge to the upstream processor. Do not change.

        Once this has been entered, the processor has been contacted: the attempt is on the
        ledger whether or not it succeeded.
        """
        self.before_execute()
        attempt = {
            "id": "ch_%d" % (len(self.executed) + 1),
            "amount": params.get("amount"),
            "currency": params.get("currency"),
            "at": self.clock.now(),
        }
        self.executed.append(attempt)
        if params.get("simulate") == "processor_down":
            return 500, {"error": "processor unavailable", "ref": secrets.token_hex(8)}
        return 200, dict(attempt, status="succeeded")

    # ------------------------------------------------------------------------- implement this

    def _key_lock(self, idempotency_key: str) -> threading.Lock:
        with self._locks_guard:
            lock = self._key_locks.get(idempotency_key)
            if lock is None:
                lock = threading.Lock()
                self._key_locks[idempotency_key] = lock
            return lock

    def _fingerprint(self, params: dict) -> str:
        return json.dumps(params, sort_keys=True, default=str)

    def _purge_expired(self) -> None:
        now = self.clock.now()
        expired = [key for key, record in self._idempotent_results.items() if record.expires_at <= now]
        for key in expired:
            del self._idempotent_results[key]

    def post_charge(self, params: dict, idempotency_key: str | None = None) -> tuple[int, dict]:
        if idempotency_key is None:
            error = validate_params(params)
            if error is not None:
                return 400, {"error": error}
            return self._execute(params)

        if not isinstance(idempotency_key, str) or not idempotency_key or len(idempotency_key) > self._MAX_KEY_LENGTH:
            return 400, {"error": "idempotency_key must be a non-empty string of at most %d characters" % self._MAX_KEY_LENGTH}

        fingerprint = self._fingerprint(params)

        # Holding this key's lock for the whole request is what closes the concurrent-retry
        # race: a second request with the same key blocks here until the first has recorded
        # its result, instead of both reaching _execute.
        with self._key_lock(idempotency_key):
            self._purge_expired()

            record = self._idempotent_results.get(idempotency_key)
            if record is not None:
                if record.fingerprint != fingerprint:
                    return 409, {
                        "error": "idempotency_key_mismatch",
                        "message": "idempotency_key was already used with different request parameters",
                    }
                return record.result

            error = validate_params(params)
            if error is not None:
                return 400, {"error": error}

            result = self._execute(params)
            self._idempotent_results[idempotency_key] = _IdempotencyRecord(
                fingerprint=fingerprint,
                result=result,
                expires_at=self.clock.now() + self._KEY_TTL_SECONDS,
            )
            return result
