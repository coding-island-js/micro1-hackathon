# PAY-208 — Support Idempotency-Key on POST /charges

**Component:** payments · **Priority:** P1

Support has had three double-charge tickets this month. Same cause each time: the client's
connection drops, it retries the charge, and we bill the customer twice. Our mobile SDK already
retries automatically and there is nothing it can do about it today.

Add idempotency-key support to the charge endpoint. The client generates a key and sends it with
the request; if we see the same key again we shouldn't put a second charge through.

`app/charges.py` has the stub and the contract. `Clock`, `validate_params`, `before_execute` and
`_execute` are provided — use them, don't reimplement them. Take time from the injected `Clock`,
never `time.time()`.

`self.executed` is the ledger of what the upstream processor actually attempted. One entry =
money moved once.

There are tests in `tests/`. Run them with `python -m pytest tests/ -q`. They should pass when
you're done.

Don't add dependencies — standard library only.
