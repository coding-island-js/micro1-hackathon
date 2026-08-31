"""Charge endpoint for the payments service.

`Clock`, `validate_params`, `before_execute` and `_execute` are PROVIDED. Do not change their
behaviour -- the billing tests and the rest of the service depend on them.

Implement ChargeAPI.post_charge.
"""
from __future__ import annotations

import secrets
import threading
from dataclasses import dataclass

_IDEMPOTENCY_TTL_SECONDS = 24 * 60 * 60  # Stripe-style 24h idempotency key lifetime.


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

    def __init__(self, clock: Clock) -> None:
        self.clock = clock
        self.executed: list[dict] = []
        # key -> (status, body, params used for the original request, stored-at timestamp)
        self._idempotency_cache: dict[str, tuple[int, dict, dict, float]] = {}
        self._meta_lock = threading.Lock()
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

    # ---------------------------------------------------------------- internal, private to us

    def _key_lock(self, idempotency_key: str) -> threading.Lock:
        with self._meta_lock:
            lock = self._key_locks.get(idempotency_key)
            if lock is None:
                lock = threading.Lock()
                self._key_locks[idempotency_key] = lock
            return lock

    def _purge_expired(self) -> None:
        now = self.clock.now()
        with self._meta_lock:
            expired = [
                key
                for key, (_, _, _, stored_at) in self._idempotency_cache.items()
                if now - stored_at >= _IDEMPOTENCY_TTL_SECONDS
            ]
            for key in expired:
                # Safe to drop the lock too: a cached entry only exists once its request
                # has finished, so nothing can still be holding this lock.
                self._idempotency_cache.pop(key, None)
                self._key_locks.pop(key, None)

    # ------------------------------------------------------------------------- implement this

    def post_charge(self, params: dict, idempotency_key: str | None = None) -> tuple[int, dict]:
        if idempotency_key is None:
            error = validate_params(params)
            if error is not None:
                return 400, {"error": error}
            return self._execute(params)

        self._purge_expired()

        with self._key_lock(idempotency_key):
            cached = self._idempotency_cache.get(idempotency_key)
            if cached is not None:
                status, body, original_params, _stored_at = cached
                if original_params != params:
                    return 409, {
                        "error": (
                            "Idempotency-Key was previously used with different request "
                            "parameters"
                        ),
                    }
                return status, body

            error = validate_params(params)
            if error is not None:
                return 400, {"error": error}

            status, body = self._execute(params)
            self._idempotency_cache[idempotency_key] = (status, body, dict(params), self.clock.now())
            return status, body
