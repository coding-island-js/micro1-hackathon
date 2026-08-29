"""Charge endpoint for the payments service.

`Clock`, `validate_params`, `before_execute` and `_execute` are PROVIDED. Do not change their
behaviour -- the billing tests and the rest of the service depend on them.

Implement ChargeAPI.post_charge.
"""
from __future__ import annotations

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
        self._idempotency_cache: dict[str, tuple[dict, tuple[int, dict]]] = {}
        self._cache_guard = threading.Lock()
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

    def post_charge(self, params: dict, idempotency_key: str | None = None) -> tuple[int, dict]:
        if idempotency_key is None:
            error = validate_params(params)
            if error is not None:
                return 400, {"error": error}
            return self._execute(params)

        while True:
            with self._cache_guard:
                cached = self._idempotency_cache.get(idempotency_key)
                if cached is not None:
                    cached_params, cached_result = cached
                    if cached_params != params:
                        return 409, {
                            "error": "idempotency key already used with different parameters",
                        }
                    return cached_result

                key_lock = self._key_locks.setdefault(idempotency_key, threading.Lock())
                is_owner = key_lock.acquire(blocking=False)

            if is_owner:
                try:
                    error = validate_params(params)
                    if error is not None:
                        return 400, {"error": error}

                    result = self._execute(params)
                    with self._cache_guard:
                        self._idempotency_cache[idempotency_key] = (dict(params), result)
                    return result
                finally:
                    key_lock.release()

            # A request with this key is already in flight. Our own attempt starts now
            # too, but instead of independently reaching the processor we wait for the
            # in-flight attempt to finish and reuse its outcome.
            self.before_execute()
            with key_lock:
                pass
            # Loop around: either the in-flight attempt cached a result (common case),
            # or it failed validation and left nothing behind, in which case we retry
            # and may become the new owner ourselves.
