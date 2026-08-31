"""Charge endpoint for the payments service.

`Clock`, `validate_params`, `before_execute` and `_execute` are PROVIDED. Do not change their
behaviour -- the billing tests and the rest of the service depend on them.

Implement ChargeAPI.post_charge.
"""
from __future__ import annotations

import secrets
import threading
from dataclasses import dataclass

_IDEMPOTENCY_KEY_TTL_SECONDS = 24 * 60 * 60  # Stripe expires idempotency keys after 24h.


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
        # key -> {"params": dict, "event": threading.Event, "result": tuple|None, "created_at": float}
        self._idempotency_store: dict[str, dict] = {}
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

    def _evict_expired_locked(self) -> None:
        """Drop completed records past their TTL. Must be called while holding `self._lock`."""
        cutoff = self.clock.now() - _IDEMPOTENCY_KEY_TTL_SECONDS
        expired = [
            key
            for key, record in self._idempotency_store.items()
            if record["result"] is not None and record["created_at"] < cutoff
        ]
        for key in expired:
            del self._idempotency_store[key]

    def post_charge(self, params: dict, idempotency_key: str | None = None) -> tuple[int, dict]:
        if idempotency_key is None:
            error = validate_params(params)
            if error is not None:
                return 400, {"error": error}
            return self._execute(params)

        # Reserve the key up front (under the lock) so a second, near-simultaneous request
        # with the same key finds a placeholder instead of racing us into `_execute`.
        owns_execution = False
        with self._lock:
            self._evict_expired_locked()
            record = self._idempotency_store.get(idempotency_key)
            if record is None:
                record = {
                    "params": dict(params),
                    "event": threading.Event(),
                    "result": None,
                    "created_at": self.clock.now(),
                }
                self._idempotency_store[idempotency_key] = record
                owns_execution = True
            elif record["params"] != params:
                return 409, {
                    "error": "Idempotency key has already been used with different request parameters",
                }

        if not owns_execution:
            # Someone else is already handling this key -- wait for their result and replay it.
            record["event"].wait()
            return record["result"]

        error = validate_params(params)
        if error is not None:
            # Nothing was attempted, so don't hold the key hostage to a bad request -- release
            # the reservation so a corrected retry with the same key can go through.
            result = (400, {"error": error})
            record["result"] = result
            record["event"].set()
            with self._lock:
                if self._idempotency_store.get(idempotency_key) is record:
                    del self._idempotency_store[idempotency_key]
            return result

        result = self._execute(params)
        record["result"] = result
        record["event"].set()
        return result
