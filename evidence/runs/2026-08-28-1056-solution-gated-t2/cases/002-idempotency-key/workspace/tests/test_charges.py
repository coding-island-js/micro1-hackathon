"""The tests that shipped with the ticket."""
from app.charges import ChargeAPI, Clock

PARAMS = {"amount": 2500, "currency": "usd"}


def build():
    clock = Clock()
    return clock, ChargeAPI(clock)


def test_charge_succeeds():
    clock, api = build()
    status, body = api.post_charge(dict(PARAMS))
    assert status == 200
    assert body["amount"] == 2500
    assert len(api.executed) == 1


def test_invalid_amount_is_rejected():
    clock, api = build()
    status, body = api.post_charge({"amount": -5, "currency": "usd"})
    assert status == 400
    assert api.executed == []


def test_retry_with_the_same_key_does_not_charge_twice():
    clock, api = build()
    first = api.post_charge(dict(PARAMS), idempotency_key="key_abc")
    second = api.post_charge(dict(PARAMS), idempotency_key="key_abc")
    assert first[0] == 200
    assert second[0] == 200
    assert len(api.executed) == 1, "the customer was charged twice"


def test_different_keys_are_separate_charges():
    clock, api = build()
    api.post_charge(dict(PARAMS), idempotency_key="key_one")
    api.post_charge(dict(PARAMS), idempotency_key="key_two")
    assert len(api.executed) == 2
