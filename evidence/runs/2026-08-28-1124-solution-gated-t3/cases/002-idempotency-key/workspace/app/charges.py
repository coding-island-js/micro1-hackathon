"""Charge endpoint for the payments service.

`Clock`, `validate_params`, `before_execute` and `_execute` are PROVIDED. Do not change their
behaviour -- the billing tests and the rest of the service depend on them.

Implement ChargeAPI.post_charge.
"""
from __future__ import annotations

import secrets
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
    """Tracks the state of a request made under a given idempotency key."""

    params: dict
    in_progress: bool
    result: tuple[int, dict] | None = None


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
        self._idempotency_cache: dict[str, _IdempotencyRecord] = {}

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
        error = validate_params(params)
        if error is not None:
            return 400, {"error": error}

        if idempotency_key is not None:
            record = self._idempotency_cache.get(idempotency_key)
            if record is not None:
                if record.params != params:
                    return 409, {
                        "error": "idempotency key already used with different request parameters",
                    }
                if record.in_progress:
                    return 409, {
                        "error": "a request with this idempotency key is already in progress",
                    }
                return record.result

            # Reserve the key before contacting the processor so a retry that arrives
            # while this attempt is still in flight is rejected instead of executed.
            self._idempotency_cache[idempotency_key] = _IdempotencyRecord(
                params=dict(params), in_progress=True,
            )

        result = self._execute(params)

        if idempotency_key is not None:
            if result[0] >= 500:
                # Transient processor failure -- don't pin the key to this response,
                # let a retry with the same key actually re-attempt the charge.
                del self._idempotency_cache[idempotency_key]
            else:
                record = self._idempotency_cache[idempotency_key]
                record.in_progress = False
                record.result = result

        return result
