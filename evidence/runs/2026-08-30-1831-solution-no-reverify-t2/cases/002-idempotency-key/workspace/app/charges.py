"""Charge endpoint for the payments service.

`Clock`, `validate_params`, `before_execute` and `_execute` are PROVIDED. Do not change their
behaviour -- the billing tests and the rest of the service depend on them.

Implement ChargeAPI.post_charge.
"""
from __future__ import annotations

import secrets
import threading
from dataclasses import dataclass

# Idempotency keys are honoured for a bounded retention window, after which they may be
# reused for a new request (mirrors the documented behaviour of e.g. Stripe's 24h window).
IDEMPOTENCY_KEY_TTL_SECONDS = 24 * 60 * 60
MAX_IDEMPOTENCY_KEY_LENGTH = 255


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
        # key -> {"params": dict, "status": "in_progress" | "done", "result": tuple | None,
        #         "created_at": float}
        self._idempotency_cache: dict[str, dict] = {}
        self._lock = threading.Lock()

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

    def post_charge(self, params: dict, idempotency_key: str | None = None) -> tuple[int, dict]:
        outcome = self._begin(params, idempotency_key)
        if outcome is not None:
            # Either a cached success, a conflict, an in-progress rejection, or a
            # validation error -- nothing left to do, and nothing to execute.
            return outcome

        result = self._execute(params)
        self._finish(idempotency_key, result)
        return result

    # ------------------------------------------------------------------------ internal helpers

    def _evict_expired(self, now: float) -> None:
        expired = [
            key
            for key, entry in self._idempotency_cache.items()
            if now - entry["created_at"] > IDEMPOTENCY_KEY_TTL_SECONDS
        ]
        for key in expired:
            del self._idempotency_cache[key]

    def _begin(self, params: dict, idempotency_key: str | None) -> tuple[int, dict] | None:
        """Runs under lock. Returns a response to short-circuit with, or None to proceed.

        When it returns None, an "in_progress" marker has been placed in the cache (if a
        key was given), so any concurrent call with the same key sees it immediately.
        """
        with self._lock:
            now = self.clock.now()
            self._evict_expired(now)

            if idempotency_key is not None:
                entry = self._idempotency_cache.get(idempotency_key)
                if entry is not None:
                    if entry["params"] != params:
                        return 409, {"error": "idempotency key already used with different parameters"}
                    if entry["status"] == "in_progress":
                        return 409, {"error": "request in progress for this idempotency key"}
                    return entry["result"]

            error = validate_params(params)
            if error is not None:
                return 400, {"error": error}

            if idempotency_key is not None:
                if len(idempotency_key) > MAX_IDEMPOTENCY_KEY_LENGTH:
                    return 400, {"error": "idempotency key too long"}
                self._idempotency_cache[idempotency_key] = {
                    "params": dict(params),
                    "status": "in_progress",
                    "result": None,
                    "created_at": now,
                }

            return None

    def _finish(self, idempotency_key: str | None, result: tuple[int, dict]) -> None:
        if idempotency_key is None:
            return
        with self._lock:
            entry = self._idempotency_cache.get(idempotency_key)
            if entry is None:
                return
            status, _ = result
            if 200 <= status < 300:
                entry["status"] = "done"
                entry["result"] = result
            else:
                # Transient/errored attempts (5xx, processor down, ...) are not memoized --
                # the same key must be retryable and actually re-attempted.
                del self._idempotency_cache[idempotency_key]
