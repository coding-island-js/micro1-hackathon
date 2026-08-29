# 2026-08-28-1202-solution-t3 — `002-idempotency-key` — the `reverify` agent

Runs the verifier a second time on the repaired code, to catch repairs that introduced new problems.

| | |
|---|---|
| Run | `2026-08-28-1202-solution-t3` |
| Case | `002-idempotency-key` |
| Model | `claude-sonnet-5` |
| Turns | 10 |
| Wall clock | 162 s |
| Cost (API-rate equivalent) | $0.2254 |
| Tools available | `Bash`, `Edit`, `Glob`, `Grep`, `Read`, `TaskCreate`, `TaskGet`, `TaskList`, `TaskUpdate`, `Write` |
| Human checkpoints | none — see note at the end |

## The instructions this agent was given

Source: [`solution/prompts/verify.md`](../solution/prompts/verify.md)

```
You are an adversarial reviewer. An implementation has just been written from the ticket below.
Your job is to find the ways it will fail in production.

The ticket is what the engineer was told. It is underspecified, the way tickets are. Real
features carry requirements the ticket does not state: published standards for this kind of
feature, documented behaviour of the systems it imitates, lifecycle rules, retry and concurrency
semantics, boundary and encoding rules.

Read the implementation. Then ask, for this specific feature:

- What does the relevant published standard or specification require that this does not do?
- What happens on the second attempt? On a retry after a failure? On two attempts at once?
- What happens at the boundary -- expiry, reuse, zero, empty, malformed, oversized?
- What state outlives a single call, and what happens when it is stale?
- What would a security or payments reviewer refuse to sign off, and by which rule?

Rules for you:

- **Do not modify any file.** You are reviewing, not fixing. Read only.
- Do not report style, naming, typing or test-coverage opinions. Only report behaviour that is
  wrong or missing against a requirement a competent reviewer would hold this feature to.
- Every finding must name the requirement it violates, not just the symptom.
- If the implementation genuinely satisfies a requirement, do not invent a finding. An empty
  findings list is an acceptable answer.

Your entire final message must be a single JSON object and nothing else:

{
  "findings": [
    {
      "id": "short-kebab-slug",
      "title": "one line, what is wrong",
      "requirement": "the rule or standard this violates, named as specifically as you can",
      "evidence": "file and what the code does that breaks it",
      "failure": "the concrete production consequence -- who is harmed and how",
      "severity": "high" | "medium" | "low"
    }
  ]
}
```

## What happened, in order

> **Reasoning.** 

**1. Uses `Bash`** on `find . -type f -not -path "./.git/*" | head -100`

> `Bash` responded:
>
> ```
> ./.pytest_cache/.gitignore
> ./.pytest_cache/CACHEDIR.TAG
> ./.pytest_cache/README.md
> ./.pytest_cache/v/cache/nodeids
> ./app/charges.py
> ./app/__pycache__/charges.cpython-312.pyc
> ./tests/test_charges.py
> ./tests/__pycache__/test_charges.cpython-312-pytest-9.1.1.pyc
> ```

**2. Uses `Read`** on `<workspace>\app\charges.py`

> `Read` responded:
>
> ```
> 1	"""Charge endpoint for the payments service.
> 2	
> 3	`Clock`, `validate_params`, `before_execute` and `_execute` are PROVIDED. Do not change their
> 4	behaviour -- the billing tests and the rest of the service depend on them.
> 5	
> 6	Implement ChargeAPI.post_charge.
> 7	"""
> 8	from __future__ import annotations
> 9	
> 10	import json
> 11	import secrets
> 12	import threading
> 13	from dataclasses import dataclass
> 14	
> 15	
> 16	class Clock:
> 17	    """PROVIDED. The service's only source of time. Do not call time.time() directly."""
> 18	
> 19	    def __init__(self, now: float = 1_700_000_000.0) -> None:
> 20	        self._now = now
> 21	
> 22	    def now(self) -> float:
> 23	        return self._now
> 24	
> 25	    def advance(self, seconds: float) -> None:
> 26	        self._now += seconds
> 27	
> 28	
> 29	def validate_params(params: dict) -> str | None:
> 30	    """PROVIDED. Returns an error message, or None if the request is well formed.
> 31	
> 32	    This runs before the charge is attempted -- nothing has happened yet when it fails.
> 33	    """
> 34	    amount = params.get("amount")
> 35	    if not isinstance(amount, int) or isinstance(amount, bool) or amount <= 0:
> 36	        return "amount must be a positive integer number of cents"
> 37
> 
> *[... 5716 more characters in the raw stream]*
> ```

**3. Uses `Read`** on `<workspace>\tests\test_charges.py`

> `Read` responded:
>
> ```
> 1	"""The tests that shipped with the ticket."""
> 2	from app.charges import ChargeAPI, Clock
> 3	
> 4	PARAMS = {"amount": 2500, "currency": "usd"}
> 5	
> 6	
> 7	def build():
> 8	    clock = Clock()
> 9	    return clock, ChargeAPI(clock)
> 10	
> 11	
> 12	def test_charge_succeeds():
> 13	    clock, api = build()
> 14	    status, body = api.post_charge(dict(PARAMS))
> 15	    assert status == 200
> 16	    assert body["amount"] == 2500
> 17	    assert len(api.executed) == 1
> 18	
> 19	
> 20	def test_invalid_amount_is_rejected():
> 21	    clock, api = build()
> 22	    status, body = api.post_charge({"amount": -5, "currency": "usd"})
> 23	    assert status == 400
> 24	    assert api.executed == []
> 25	
> 26	
> 27	def test_retry_with_the_same_key_does_not_charge_twice():
> 28	    clock, api = build()
> 29	    first = api.post_charge(dict(PARAMS), idempotency_key="key_abc")
> 30	    second = api.post_charge(dict(PARAMS), idempotency_key="key_abc")
> 31	    assert first[0] == 200
> 32	    assert second[0] == 200
> 33	    assert len(api.executed) == 1, "the customer was charged twice"
> 34	
> 35	
> 36	def test_different_keys_are_separate_charges():
> 37	    clock, api = build()
> 38	    api.post_charge(dict(PARAMS), idempotency_key="key_one")
> 39	    api.post_charg
> 
> *[... 82 more characters in the raw stream]*
> ```

> **Reasoning.** 

**4. Uses `Bash`** on `cd "<workspace>" && python -m pytest tests/ -q 2>&1 | tail -30`

> `Bash` responded:
>
> ```
> ....                                                                     [100%]
> 4 passed in 0.01s
> ```

> **Reasoning.** 

**5. Uses `Bash`** on `cd "<workspace>" && python3 - <<'EOF' from app.charges import ChargeAPI, Clock  class FlakyChargeAPI(ChargeAPI):     def __init__(self, clock):         super().__init__(clock)         self.calls = 0     def _execute(self, params):         self.calls += 1         if self.calls == 1:             # sim  *[... 651 more characters in the raw stream]*`

> `Bash` responded — **reported an error**:
>
> ```
> Exit code 127
> /usr/bin/bash: line 26: python3: command not found
> ```

**6. Uses `Bash`** on `cd "<workspace>" && python - <<'EOF' from app.charges import ChargeAPI, Clock  class FlakyChargeAPI(ChargeAPI):     def __init__(self, clock):         super().__init__(clock)         self.calls = 0     def _execute(self, params):         self.calls += 1         if self.calls == 1:             self.e  *[... 562 more characters in the raw stream]*`

> `Bash` responded:
>
> ```
> first call raised, retrying...
> 200 {'id': 'ch_2', 'amount': 2500, 'currency': 'usd', 'at': 1700000000.0, 'status': 'succeeded'}
> executed entries: 2
> ```

> **Reasoning.** 

**7. Uses `Bash`** on `cd "<workspace>" && python - <<'EOF' from app.charges import ChargeAPI, Clock  clock = Clock() api = ChargeAPI(clock)  # first attempt: processor is down (5xx) status, body = api.post_charge({"amount": 2500, "currency": "usd", "simulate": "processor_down"}, idempotency_key="k1") print("attempt1", st  *[... 457 more characters in the raw stream]*`

> `Bash` responded:
>
> ```
> attempt1 500 {'error': 'processor unavailable', 'ref': '57e67f7ca10e2f55'}
> attempt2 (retry within TTL) 500 {'error': 'processor unavailable', 'ref': '57e67f7ca10e2f55'}
> executed: [{'id': 'ch_1', 'amount': 2500, 'currency': 'usd', 'at': 1700000000.0}]
> ```

> **Reasoning.** 

**8. Uses `Bash`** on `cd "<workspace>" && python - <<'EOF' import threading from app.charges import ChargeAPI, Clock  clock = Clock() api = ChargeAPI(clock)  # seed many keys that will all expire "now" for i in range(500):     api.post_charge({"amount": 100, "currency": "usd"}, idempotency_key=f"seed{i}")  clock.advance(  *[... 406 more characters in the raw stream]*`

> `Bash` responded:
>
> ```
> errors: 0
> []
> ```

> **Reasoning.** 

**9. Uses `Bash`** on `rm -f /tmp/nonexistent 2>/dev/null; echo done`

> `Bash` responded:
>
> ```
> done
> ```

{
  "findings": [
    {
      "id": "unprotected-execute-window-double-charge",
      "title": "A dropped connection/exception during _execute() leaves the idempotency key unrecorded, so the retry re-charges",
      "requirement": "The ticket's core requirement: 'if we see the same key again we shouldn't put a second charge through', specifically for the case of a dropped client connection followed by a retry",
      "evidence": "app/charges.py:159-165 — self._execute(params) is called and, only if it returns normally, the result is stored in self._idempotent_results. If _execute (or before_execute, which Operations monkey-patches to inject latency/replay traffic) raises or the process is killed/times out mid-call — the exact 'connection drops' scenario in the ticket — the code jumps straight past the record-write and the per-key lock is released via the `with` block having recorded nothing.",
      "failure": "Reproduced directly: a first call that appends to self.executed (processor contacted) and then raises produces a second, distinct entry in self.executed on retry with the identical idempotency key — a genuine double charge, which is precisely the bug PAY-208 was filed to eliminate.",
      "severity": "high"
    },
    {
      "id": "processor-error-permanently-cached",
      "title": "A transient upstream 5xx is cached under the idempotency key for the full 24h TTL, blocking all legitimate retries",
      "requirement": "Idempotency layers (this ticket cites the Stripe 24h window as the model) must let a client recover from a transient processor/network failure by retrying — they must not turn a temporary outage into a guaranteed failure for the entire key lifetime.",
      "evidence": "app/charges.py:159-164 stores the _execute() result unconditionally, including a 500 'processor unavailable' response, into self._idempotent_results with a fresh 24h expiry. Reproduced: after one 500 response, an identical retry with the same key returns the exact same cached 500 (same ref) instead of re-attempting the charge, for up to 24 hours.",
      "failure": "A customer whose card was never actually charged (processor down) cannot complete the payment for up to a day unless the client fabricates a brand-new idempotency key — which reintroduces the double-charge risk the feature exists to prevent, since the client can't safely know whether the original attempt actually succeeded downstream.",
      "severity": "high"
    },
    {
      "id": "in-process-only-i

*[... 2920 more characters in the raw stream]*

## What the agent finished with

```
{
  "findings": [
    {
      "id": "unprotected-execute-window-double-charge",
      "title": "A dropped connection/exception during _execute() leaves the idempotency key unrecorded, so the retry re-charges",
      "requirement": "The ticket's core requirement: 'if we see the same key again we shouldn't put a second charge through', specifically for the case of a dropped client connection followed by a retry",
      "evidence": "app/charges.py:159-165 — self._execute(params) is called and, only if it returns normally, the result is stored in self._idempotent_results. If _execute (or before_execute, which Operations monkey-patches to inject latency/replay traffic) raises or the process is killed/times out mid-call — the exact 'connection drops' scenario in the ticket — the code jumps straight past the record-write and the per-key lock is released via the `with` block having recorded nothing.",
      "failure": "Reproduced directly: a first call that appends to self.executed (processor contacted) and then raises produces a second, distinct entry in self.executed on retry with the identical idempotency key — a genuine double charge, which is precisely the bug PAY-208 was filed to eliminate.",
      "severity": "high"
    },
    {
      "id": "processor-error-permanently-cached",
      "title": "A transient upstream 5xx is cached under the idempotency key for the full 24h TTL, blocking all legitimate retries",
      "requirement": "Idempotency layers (this ticket cites the Stripe 24h window as the model) must let a client recover from a transient processor/network failure by retrying — they must not turn a temporary outage into a guaranteed failure for the entire key lifetime.",
      "evidence": "app/charges.py:159-164 stores the _execute() result unconditionally, including a 500 'processor unavailable' response, into self._idempotent_results with a fresh 24h expiry. Reproduced: after one 500 response, an identical retry with the same key returns the exact same cached 500 (same ref) instead of re-attempting the charge, for up to 24 hours.",
      "failure": "A customer whose card was never actually charged (processor down) cannot complete the payment for up to a day unless the client fabricates a brand-new idempotency key — which reintroduces the double-charge risk the feature exists to prevent, since the client can't safely know whether the original attempt actually succeeded downstream.",
      "severity": "high"
    },
    {
      "id": "in-process-only-idempotency-store",
      "title": "Idempotency records and locks live only in one process's memory, not a shared/persistent store",
      "requirement": "For a retry to be caught, the second attempt must be visible to whichever instance handles it. A payments API deployed with multiple workers/processes/pods (the normal topology for a P1 payments endpoint) must share idempotency state across instances and survive restarts/deploys.",
      "evidence": "app/charges.py:74-80 — self._idempotent_results and self._key_locks are plain in-memory dicts on the ChargeAPI instance, with no persistence or cross-process coordination (e.g. a database unique constraint or shared cache).",
      "failure": "A mobile client's automatic retry (the ticket's stated trigger) that lands on a different worker process, or arrives after a deploy/restart, will find no record of the key and will be charged again — the exact double-charge failure mode from the support tickets, un-fixed for any multi-instance deployment.",
      "severity": "high"
    },
    {
      "id": "unsynchronized-shared-dict-purge",
      "title": "_purge_expired mutates the shared results dict under only a per-key lock, not a lock guarding the dict itself",
      "requirement": "Concurrent requests using different idempotency keys must not corrupt shared idempotency state ('two attempts at once' safety, which the per-key lock design otherwise aims for).",
      "evidence": "app/charges.py:122-126 — _purge_expired() iterates and d

*[... 1420 more characters in the raw stream]*
```

---

**On human checkpoints.** There are none in this trajectory, and that is a property of the task rather than an omission. Each agent works inside a throwaway copy of the case in the OS temp directory, with network tools and delegation denied, so no action it can take reaches anything outside its sandbox. Ground rule 4 asks for approval before a *consequential* action; there is no consequential action available here to approve.

**Raw source.** `evidence/runs/2026-08-28-1202-solution-t3/cases/002-idempotency-key/reverify.stream.jsonl` — every event, unedited, including the ones this page truncates.
