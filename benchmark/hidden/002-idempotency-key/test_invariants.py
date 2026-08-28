"""Hidden evaluator tests for case 002.

Every assertion traces to documented behaviour of Stripe's idempotency layer
(docs.stripe.com/api/idempotent_requests), quoted in each test's docstring and recorded in
benchmark/MANIFEST.md. This is a published API contract, not our opinion.

NEVER shown to an implementation agent.
"""
import pytest

from app.charges import ChargeAPI, Clock

PARAMS = {"amount": 2500, "currency": "usd"}
KEY = "key_retry_1"


def build():
    clock = Clock()
    return clock, ChargeAPI(clock)


def test_first_result_is_replayed_verbatim():
    """"saving the resulting status code and body of the first request made for any given
    idempotency key ... Subsequent requests with the same key return the same result"."""
    clock, api = build()
    first = api.post_charge(dict(PARAMS), idempotency_key=KEY)
    second = api.post_charge(dict(PARAMS), idempotency_key=KEY)

    assert second == first, (
        "the replayed response differed from the original: %r vs %r" % (second, first)
    )
    assert len(api.executed) == 1


def test_failed_results_are_replayed_not_retried():
    """"regardless of whether it succeeds or fails ... return the same result, including
    500 errors".

    Caching only successes is the bug that double-charges a customer whose first attempt
    timed out inside the processor.
    """
    clock, api = build()
    params = dict(PARAMS, simulate="processor_down")

    first = api.post_charge(dict(params), idempotency_key=KEY)
    assert first[0] == 500, "expected the simulated processor failure to surface as a 500"

    second = api.post_charge(dict(params), idempotency_key=KEY)

    assert len(api.executed) == 1, (
        "a retry after a 500 hit the processor a second time -- the customer can be charged "
        "twice for one intent"
    )
    assert second == first, "the 500 response was not replayed verbatim"


def test_same_key_with_different_params_is_an_error():
    """"The idempotency layer compares incoming parameters to those of the original request
    and errors if they're not the same to prevent accidental misuse"."""
    clock, api = build()
    first = api.post_charge(dict(PARAMS), idempotency_key=KEY)
    assert first[0] == 200

    status, body = api.post_charge(
        {"amount": 9900, "currency": "usd"}, idempotency_key=KEY
    )

    assert status >= 400, (
        "reusing an idempotency key with different parameters returned %d; it must be an "
        "error, not a silent replay of the original charge" % status
    )
    assert len(api.executed) == 1, "the mismatched retry put a second charge through"


def test_an_in_flight_key_is_not_served_the_cached_result():
    """"if ... the request conflicts with another request that's executing concurrently, we
    don't save the idempotent result because no API endpoint initiates the execution. You can
    retry these requests."

    Modelled deterministically: a second request with the same key arrives while the first is
    inside `_execute`, via the provided `before_execute` hook. It must not be handed the
    (not yet existing) result, and it must not put a second charge through.
    """
    clock, api = build()
    inner = {}

    def second_request_arrives():
        api.before_execute = lambda: None  # the nested call must not re-enter
        inner["result"] = api.post_charge(dict(PARAMS), idempotency_key=KEY)

    api.before_execute = second_request_arrives
    outer = api.post_charge(dict(PARAMS), idempotency_key=KEY)

    assert "result" in inner, "the provided before_execute hook was never called"
    assert len(api.executed) == 1, (
        "a request arriving while the same key was still executing put a second charge through"
    )
    assert inner["result"][0] != 200, (
        "a request arriving mid-flight was served a success for a charge that had not "
        "completed yet"
    )

    # "You can retry these requests" -- once the original finishes, the key resolves to it.
    assert api.post_charge(dict(PARAMS), idempotency_key=KEY) == outer
    assert len(api.executed) == 1


def test_keys_expire_after_a_day():
    """"You can remove keys from the system automatically after they're at least 24 hours
    old. We generate a new request if a key is reused after the original is pruned"."""
    clock, api = build()
    api.post_charge(dict(PARAMS), idempotency_key=KEY)

    clock.advance(25 * 60 * 60)
    status, _ = api.post_charge(dict(PARAMS), idempotency_key=KEY)

    assert status == 200
    assert len(api.executed) == 2, (
        "a key reused more than 24 hours later was still replayed from cache; keys are "
        "retained forever"
    )


def test_validation_failures_are_not_cached():
    """"If incoming parameters fail validation ... we don't save the idempotent result
    because no API endpoint initiates the execution. You can retry these requests"."""
    clock, api = build()

    bad = api.post_charge({"amount": -5, "currency": "usd"}, idempotency_key=KEY)
    assert bad[0] == 400
    assert api.executed == []

    status, body = api.post_charge(dict(PARAMS), idempotency_key=KEY)

    assert status == 200, (
        "a key whose first use failed validation was burned; the client can never "
        "successfully retry with it (got %d)" % status
    )
    assert len(api.executed) == 1
