"""Charge endpoint for the payments service.

`Clock`, `validate_params`, `before_execute` and `_execute` are PROVIDED. Do not change their
behaviour -- the billing tests and the rest of the service depend on them.

Implement ChargeAPI.post_charge.
"""
from __future__ import annotations

import secrets
import threading
from dataclasses import dataclass

# How long a completed idempotency key's response is memoized before the key can be reused,
# mirroring Stripe's documented 24-hour idempotency-key window.
_IDEMPOTENCY_KEY_TTL_SECONDS = 24 * 60 * 60


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
        # key -> {"status": "in_progress" | "done", "params": dict, "created_at": float,
        #         "response": tuple[int, dict] | None}
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

    def _entry_expired(self, entry: dict) -> bool:
        return self.clock.now() - entry["created_at"] >= _IDEMPOTENCY_KEY_TTL_SECONDS

    def _prune_expired(self) -> None:
        expired = [key for key, entry in self._idempotency_cache.items() if self._entry_expired(entry)]
        for key in expired:
            del self._idempotency_cache[key]

    def post_charge(self, params: dict, idempotency_key: str | None = None) -> tuple[int, dict]:
        if idempotency_key is None:
            error = validate_params(params)
            if error is not None:
                return 400, {"error": error}
            return self._execute(params)

        with self._lock:
            self._prune_expired()
            entry = self._idempotency_cache.get(idempotency_key)
            if entry is not None:
                if entry["status"] == "in_progress":
                    return 409, {
                        "error": "a request with this idempotency key is already in progress",
                    }
                if entry["params"] != params:
                    return 409, {
                        "error": "Idempotency-Key has already been used with different "
                        "request parameters",
                    }
                return entry["response"]

            # Claim the key before releasing the lock so a concurrent request with the same
            # key sees "in_progress" instead of racing us to _execute.
            self._idempotency_cache[idempotency_key] = {
                "status": "in_progress",
                "params": params,
                "created_at": self.clock.now(),
                "response": None,
            }

        error = validate_params(params)
        if error is not None:
            # Nothing was attempted -- release the claim so a corrected retry isn't blocked.
            with self._lock:
                del self._idempotency_cache[idempotency_key]
            return 400, {"error": error}

        status, body = self._execute(params)

        with self._lock:
            if status < 500:
                # Only a definitive, completed outcome is memoized against the key -- a
                # processor-side (5xx) error must not permanently lock the key to that error.
                self._idempotency_cache[idempotency_key] = {
                    "status": "done",
                    "params": params,
                    "created_at": self.clock.now(),
                    "response": (status, body),
                }
            else:
                # Processor-side failure: don't poison the key, let a future retry try again.
                del self._idempotency_cache[idempotency_key]

        return status, body
