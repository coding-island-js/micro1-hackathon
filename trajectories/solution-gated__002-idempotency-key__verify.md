# 2026-08-28-1124-solution-gated-t3 — `002-idempotency-key` — the `verify` agent

Reads the implementation against the ticket and reports findings. It cannot edit anything.

| | |
|---|---|
| Run | `2026-08-28-1124-solution-gated-t3` |
| Case | `002-idempotency-key` |
| Model | `claude-sonnet-5` |
| Turns | 9 |
| Wall clock | 120 s |
| Cost (API-rate equivalent) | $0.2255 |
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

**1. Uses `Bash`** on `find <workspace> -type f -not -path '*/.git/*' | sort`

> `Bash` responded:
>
> ```
> <workspace>/.pytest_cache/.gitignore
> <workspace>/.pytest_cache/CACHEDIR.TAG
> <workspace>/.pytest_cache/README.md
> <workspace>/.pytest_cache/v/cache/nodeids
> <workspace>/app/__pycache__/charges.cpython-312.pyc
> <workspace>/app/charges.py
> <workspace>/tests/__pycache__/test_charges.cpython-312-pytest-9.1.1.pyc
> <workspace>/tests/test_charges.py
> ```

**2. Uses `Read`** on `<workspace>/app/charges.py`

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
> 10	import secrets
> 11	from dataclasses import dataclass
> 12	
> 13	
> 14	class Clock:
> 15	    """PROVIDED. The service's only source of time. Do not call time.time() directly."""
> 16	
> 17	    def __init__(self, now: float = 1_700_000_000.0) -> None:
> 18	        self._now = now
> 19	
> 20	    def now(self) -> float:
> 21	        return self._now
> 22	
> 23	    def advance(self, seconds: float) -> None:
> 24	        self._now += seconds
> 25	
> 26	
> 27	def validate_params(params: dict) -> str | None:
> 28	    """PROVIDED. Returns an error message, or None if the request is well formed.
> 29	
> 30	    This runs before the charge is attempted -- nothing has happened yet when it fails.
> 31	    """
> 32	    amount = params.get("amount")
> 33	    if not isinstance(amount, int) or isinstance(amount, bool) or amount <= 0:
> 34	        return "amount must be a positive integer number of cents"
> 35	    if not isinstance(params.get("
> 
> *[... 2717 more characters in the raw stream]*
> ```

**3. Uses `Read`** on `<workspace>/tests/test_charges.py`

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

**4. Uses `Bash`** on `python -m pytest tests/ -q 2>&1 | tail -30`

> `Bash` responded:
>
> ```
> ....                                                                     [100%]
> 4 passed in 0.01s
> ```

Now let me write and run repro tests for the candidate defects.

**5. Uses `Write`** on `<workspace>/tests/test_repro_scratch.py`

> `Write` responded:
>
> ```
> File created successfully at: <workspace>/tests/test_repro_scratch.py (file state is current in your context — no need to Read it back)
> ```

> **Reasoning.** 

**6. Uses `Bash`** on `python -m pytest tests/test_repro_scratch.py -q 2>&1 | tail -60`

> `Bash` responded:
>
> ```
> FFF                                                                      [100%]
> ================================== FAILURES ===================================
> _________________ test_repro_concurrent_retry_double_charges __________________
> 
>     def test_repro_concurrent_retry_double_charges():
>         clock, api = build()
>         fired = []
>     
>         def before_execute_hook():
>             if not fired:
>                 fired.append(1)
>                 api.post_charge(dict(PARAMS), idempotency_key="key_abc")
>     
>         api.before_execute = before_execute_hook
>         status, body = api.post_charge(dict(PARAMS), idempotency_key="key_abc")
> >       assert len(api.executed) == 1, "concurrent/in-flight retry with same key caused double charge"
> E       AssertionError: concurrent/in-flight retry with same key caused double charge
> E       assert 2 == 1
> E        +  where 2 = len([{'id': 'ch_1', 'amount': 2500, 'currency': 'usd', 'at': 1700000000.0}, {'id': 'ch_2', 'amount': 2500, 'currency': 'usd', 'at': 1700000000.0}])
> E        +    where [{'id': 'ch_1', 'amount': 2500, 'currency': 'usd', 'at': 1700000000.0}, {'id': 'ch_2', 'amount': 2500, 'currency': 'usd', 'at': 1700
> 
> *[... 2058 more characters in the raw stream]*
> ```

All three repros fail against current code as expected. Let me remove the scratch file since I'm reviewing, not modifying the workspace deliverables.

**7. Uses `Bash`** on `rm <workspace>/tests/test_repro_scratch.py python -m pytest tests/ -q 2>&1 | tail -10`

> `Bash` responded:
>
> ```
> ....                                                                     [100%]
> 4 passed in 0.01s
> ```

> **Reasoning.** 

**8. Uses `Bash`** on `ls <workspace>/tests/`

> `Bash` responded:
>
> ```
> __pycache__/
> test_charges.py
> ```

```json
{
  "findings": [
    {
      "id": "in-flight-retry-double-charge",
      "title": "A retry that arrives while the first attempt is still in flight is not deduplicated, so it double-charges",
      "requirement": "The idempotency key must lock/reserve on first receipt, before the upstream call is made, so a second attempt with the same key that arrives before the first completes is rejected or made to wait rather than executed. This is the exact scenario the ticket is written to prevent ('the client's connection drops, it retries the charge... we bill the customer twice') — the client retries while its original request is still being processed server-side.",
      "grounding": "ticket",
      "evidence": "app/charges.py post_charge: the cache lookup happens first, but `self._idempotency_cache[idempotency_key] = result` is only written *after* `self._execute(params)` returns. Nothing marks the key as 'in progress' before calling `_execute`. `before_execute` (called inside `_execute`) is documented as the point where 'Operations monkey-patches this in staging to inject latency and to replay traffic' — i.e. overlapping calls during that window are an anticipated real scenario, and the current code has no guard against it.",
      "failure": "A customer whose retry (automatic, from the mobile SDK per the ticket) reaches the server before the first attempt's response is recorded gets charged twice — the exact double-charge bug this ticket exists to fix.",
      "severity": "high",
      "contradicts_provided_contract": false,
      "contradiction_note": null,
      "repro": "def test_repro_concurrent_retry_double_charges():\n    from app.charges import ChargeAPI, Clock\n    PARAMS = {\"amount\": 2500, \"currency\": \"usd\"}\n    clock = Clock()\n    api = ChargeAPI(clock)\n    fired = []\n\n    def before_execute_hook():\n        if not fired:\n            fired.append(1)\n            api.post_charge(dict(PARAMS), idempotency_key=\"key_abc\")\n\n    api.before_execute = before_execute_hook\n    api.post_charge(dict(PARAMS), idempotency_key=\"key_abc\")\n    assert len(api.executed) == 1, \"concurrent/in-flight retry with same key caused double charge\"\n"
    },
    {
      "id": "processor-error-permanently-cached",
      "title": "A transient processor failure (e.g. simulate='processor_down') is cached under the idempotency key forever, so retries never actually re-attempt the charge",
      "requirement": "Standard idempotency-key semantics (as impl

*[... 3991 more characters in the raw stream]*

## What the agent finished with

```
```json
{
  "findings": [
    {
      "id": "in-flight-retry-double-charge",
      "title": "A retry that arrives while the first attempt is still in flight is not deduplicated, so it double-charges",
      "requirement": "The idempotency key must lock/reserve on first receipt, before the upstream call is made, so a second attempt with the same key that arrives before the first completes is rejected or made to wait rather than executed. This is the exact scenario the ticket is written to prevent ('the client's connection drops, it retries the charge... we bill the customer twice') — the client retries while its original request is still being processed server-side.",
      "grounding": "ticket",
      "evidence": "app/charges.py post_charge: the cache lookup happens first, but `self._idempotency_cache[idempotency_key] = result` is only written *after* `self._execute(params)` returns. Nothing marks the key as 'in progress' before calling `_execute`. `before_execute` (called inside `_execute`) is documented as the point where 'Operations monkey-patches this in staging to inject latency and to replay traffic' — i.e. overlapping calls during that window are an anticipated real scenario, and the current code has no guard against it.",
      "failure": "A customer whose retry (automatic, from the mobile SDK per the ticket) reaches the server before the first attempt's response is recorded gets charged twice — the exact double-charge bug this ticket exists to fix.",
      "severity": "high",
      "contradicts_provided_contract": false,
      "contradiction_note": null,
      "repro": "def test_repro_concurrent_retry_double_charges():\n    from app.charges import ChargeAPI, Clock\n    PARAMS = {\"amount\": 2500, \"currency\": \"usd\"}\n    clock = Clock()\n    api = ChargeAPI(clock)\n    fired = []\n\n    def before_execute_hook():\n        if not fired:\n            fired.append(1)\n            api.post_charge(dict(PARAMS), idempotency_key=\"key_abc\")\n\n    api.before_execute = before_execute_hook\n    api.post_charge(dict(PARAMS), idempotency_key=\"key_abc\")\n    assert len(api.executed) == 1, \"concurrent/in-flight retry with same key caused double charge\"\n"
    },
    {
      "id": "processor-error-permanently-cached",
      "title": "A transient processor failure (e.g. simulate='processor_down') is cached under the idempotency key forever, so retries never actually re-attempt the charge",
      "requirement": "Standard idempotency-key semantics (as implemented by every major payments API this feature is modeled on) do not permanently pin a client to a transient/definitive-failure response for a key; a retry after a failed attempt must be allowed to actually re-attempt the charge, otherwise clients can never successfully complete a purchase once the first attempt hit a 5xx.",
      "grounding": "convention",
      "evidence": "app/charges.py post_charge: `result = self._execute(params)` is stored into `self._idempotency_cache[idempotency_key]` unconditionally, including when `_execute` returns `500, {\"error\": \"processor unavailable\", ...}` (the `simulate=\"processor_down\"` branch that the provided `_execute` deliberately supports). Every subsequent call with that key replays the cached 500 forever, regardless of processor recovery.",
      "failure": "A customer whose first attempt hits a transient processor outage is permanently stuck: every retry with the same idempotency key (which is exactly what a retrying SDK would send) returns the same 500 forever, even after the processor recovers. The charge can never succeed unless the client fabricates a new key — defeating the point of idempotency and leaving the customer unable to complete checkout.",
      "severity": "high",
      "contradicts_provided_contract": false,
      "contradiction_note": null,
      "repro": "def test_repro_retry_after_processor_error_is_not_retried():\n    from app.charges import ChargeAPI, Clock\n    PARAMS = {\"amount\": 2500, \"currency\":

*[... 2491 more characters in the raw stream]*
```

---

**On human checkpoints.** There are none in this trajectory, and that is a property of the task rather than an omission. Each agent works inside a throwaway copy of the case in the OS temp directory, with network tools and delegation denied, so no action it can take reaches anything outside its sandbox. Ground rule 4 asks for approval before a *consequential* action; there is no consequential action available here to approve.

**Raw source.** `evidence/runs/2026-08-28-1124-solution-gated-t3/cases/002-idempotency-key/verify.stream.jsonl` — every event, unedited, including the ones this page truncates.
