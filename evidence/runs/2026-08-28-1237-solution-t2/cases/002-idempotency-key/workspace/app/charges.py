"""Charge endpoint for the payments service.

`Clock`, `validate_params`, `before_execute` and `_execute` are PROVIDED. Do not change their
behaviour -- the billing tests and the rest of the service depend on them.

Implement ChargeAPI.post_charge.
"""
from __future__ import annotations

import secrets
import threading
from dataclasses import dataclass
from collections.abc import MutableMapping

# Stripe-style 24h idempotency key lifetime: bounds storage and lets a client
# legitimately reuse a key after the window instead of being 409'd forever.
IDEMPOTENCY_KEY_TTL_SECONDS = 24 * 60 * 60


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

    def __init__(self, clock: Clock, store: MutableMapping[str, dict] | None = None) -> None:
        self.clock = clock
        self.executed: list[dict] = []
        # In-memory by default. Pass a durable MutableMapping (e.g. a shelve.Shelf)
        # to survive process restarts/deploys -- a plain dict does not.
        self._idempotency_keys: MutableMapping[str, dict] = {} if store is None else store
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
        error = validate_params(params)
        if error is not None:
            return 400, {"error": error}

        # An empty string is not a meaningful key -- treat it like no key was supplied.
        key = idempotency_key or None

        if key is not None:
            with self._lock:
                record = self._idempotency_keys.get(key)
                if record is not None and record["status"] != "in_progress":
                    if self.clock.now() - record["at"] > IDEMPOTENCY_KEY_TTL_SECONDS:
                        del self._idempotency_keys[key]
                        record = None
                if record is not None:
                    if record["status"] == "in_progress":
                        return 409, {
                            "error": "a request with this idempotency key is already in progress",
                        }
                    if record["params"] != params:
                        return 409, {
                            "error": "idempotency key already used with different parameters",
                        }
                    return record["status"], record["body"]
                # Claim the key before releasing the lock so a concurrent request
                # with the same key sees "in_progress" instead of racing us to _execute.
                self._idempotency_keys[key] = {
                    "status": "in_progress",
                    "params": dict(params),
                    "body": None,
                    "at": self.clock.now(),
                }

        try:
            status, body = self._execute(params)
        except Exception:
            # The attempt is on the ledger, but we don't know the outcome -- release the
            # key rather than caching a false result, so a later retry can safely proceed.
            if key is not None:
                with self._lock:
                    self._idempotency_keys.pop(key, None)
            raise

        if key is not None:
            with self._lock:
                if status >= 500:
                    # Transient processor failure: not a durable result, don't lock the
                    # key to it -- let a retry (even with corrected params) go through.
                    self._idempotency_keys.pop(key, None)
                else:
                    self._idempotency_keys[key] = {
                        "status": status,
                        "params": dict(params),
                        "body": body,
                        "at": self.clock.now(),
                    }

        return status, body
