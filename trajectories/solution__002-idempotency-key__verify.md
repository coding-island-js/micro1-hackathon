# 2026-08-28-1202-solution-t3 — `002-idempotency-key` — the `verify` agent

Reads the implementation against the ticket and reports findings. It cannot edit anything.

| | |
|---|---|
| Run | `2026-08-28-1202-solution-t3` |
| Case | `002-idempotency-key` |
| Model | `claude-sonnet-5` |
| Turns | 5 |
| Wall clock | 93 s |
| Cost (API-rate equivalent) | $0.1492 |
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

**1. Uses `Bash`** on `find <workspace> -type f -not -path "*/node_modules/*" | head -200`

> `Bash` responded:
>
> ```
> <workspace>/.pytest_cache/.gitignore
> <workspace>/.pytest_cache/CACHEDIR.TAG
> <workspace>/.pytest_cache/README.md
> <workspace>/.pytest_cache/v/cache/nodeids
> <workspace>/app/charges.py
> <workspace>/app/__pycache__/charges.cpython-312.pyc
> <workspace>/tests/test_charges.py
> <workspace>/tests/__pycache__/test_charges.cpython-312-pytest-9.1.1.pyc
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
> *[... 2721 more characters in the raw stream]*
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

**4. Uses `Bash`** on `python -m pytest tests/ -q`

> `Bash` responded:
>
> ```
> ....                                                                     [100%]
> 4 passed in 0.01s
> ```

> **Reasoning.** 

```json
{
  "findings": [
    {
      "id": "no-inflight-lock-concurrent-double-charge",
      "title": "Two simultaneous requests with the same idempotency key both reach the processor",
      "requirement": "Idempotency-Key semantics require mutual exclusion for the duration of processing, not just de-duplication of completed results (RFC draft 'Idempotency-Key HTTP Header Field' and Stripe's documented behavior: a second request received while the first with the same key is still in flight must be rejected or held, not executed).",
      "evidence": "app/charges.py post_charge (lines 89-102): the guard `if idempotency_key in self._idempotent_results` only checks a dict that is populated *after* `_execute` returns. There is no 'in-progress' marker or lock taken before calling `_execute`. `before_execute` is explicitly documented as the hook Operations uses in staging 'to inject latency and to replay traffic' -- i.e. the exact race this code fails to close.",
      "failure": "The precise bug PAY-208 exists to fix -- a client retry firing while the original request is still in flight (e.g. slow network, not a dropped connection) -- passes the `in` check twice before either write completes, so both requests call `_execute` and the customer is billed twice. This reproduces the double-charge tickets under concurrency instead of eliminating them.",
      "severity": "high"
    },
    {
      "id": "no-parameter-fingerprint-check",
      "title": "Reusing a key with different request parameters silently replays the wrong result instead of erroring",
      "requirement": "Documented Idempotency-Key behavior (e.g. Stripe API): a key is bound to the exact parameters of the request that first used it; replaying the key with different parameters must return an error (409/422 idempotency-key-mismatch), not the cached response for a different charge.",
      "evidence": "app/charges.py post_charge: the cache lookup `self._idempotent_results[idempotency_key]` is keyed only by the string key -- `params` is never compared against what was stored for that key on the first call.",
      "failure": "A client that reuses a key with a different amount or currency (bug, copy-paste, or key collision) silently gets back the first charge's result -- e.g. told a $50 charge 'succeeded' when only the earlier $25 charge exists, or vice versa. This causes reconciliation mismatches and incorrect confirmations shown to the customer, with no error surfaced to catch the bug.",
      "sev

*[... 2191 more characters in the raw stream]*

## What the agent finished with

```
```json
{
  "findings": [
    {
      "id": "no-inflight-lock-concurrent-double-charge",
      "title": "Two simultaneous requests with the same idempotency key both reach the processor",
      "requirement": "Idempotency-Key semantics require mutual exclusion for the duration of processing, not just de-duplication of completed results (RFC draft 'Idempotency-Key HTTP Header Field' and Stripe's documented behavior: a second request received while the first with the same key is still in flight must be rejected or held, not executed).",
      "evidence": "app/charges.py post_charge (lines 89-102): the guard `if idempotency_key in self._idempotent_results` only checks a dict that is populated *after* `_execute` returns. There is no 'in-progress' marker or lock taken before calling `_execute`. `before_execute` is explicitly documented as the hook Operations uses in staging 'to inject latency and to replay traffic' -- i.e. the exact race this code fails to close.",
      "failure": "The precise bug PAY-208 exists to fix -- a client retry firing while the original request is still in flight (e.g. slow network, not a dropped connection) -- passes the `in` check twice before either write completes, so both requests call `_execute` and the customer is billed twice. This reproduces the double-charge tickets under concurrency instead of eliminating them.",
      "severity": "high"
    },
    {
      "id": "no-parameter-fingerprint-check",
      "title": "Reusing a key with different request parameters silently replays the wrong result instead of erroring",
      "requirement": "Documented Idempotency-Key behavior (e.g. Stripe API): a key is bound to the exact parameters of the request that first used it; replaying the key with different parameters must return an error (409/422 idempotency-key-mismatch), not the cached response for a different charge.",
      "evidence": "app/charges.py post_charge: the cache lookup `self._idempotent_results[idempotency_key]` is keyed only by the string key -- `params` is never compared against what was stored for that key on the first call.",
      "failure": "A client that reuses a key with a different amount or currency (bug, copy-paste, or key collision) silently gets back the first charge's result -- e.g. told a $50 charge 'succeeded' when only the earlier $25 charge exists, or vice versa. This causes reconciliation mismatches and incorrect confirmations shown to the customer, with no error surfaced to catch the bug.",
      "severity": "high"
    },
    {
      "id": "idempotency-keys-never-expire",
      "title": "Idempotency records have no TTL despite Clock being injected for exactly this purpose",
      "requirement": "Published idempotency-key behavior scopes keys to a bounded window (e.g. 24 hours in Stripe's implementation) after which the same key may legitimately start a new operation; keys must not be retained forever.",
      "evidence": "app/charges.py: `Clock.now()` is only ever read inside the provided `_execute` for the ledger timestamp. `post_charge` never calls `self.clock.now()`, so `_idempotent_results` entries carry no timestamp and are never evicted or expired.",
      "failure": "Two production consequences: (1) unbounded memory growth in `_idempotent_results` since nothing is ever purged; (2) a client that legitimately wants to reuse a key after the expected window (e.g. a scheduled job reusing a template key per period) is permanently locked out with a stale replayed result instead of a fresh charge going through.",
      "severity": "medium"
    },
    {
      "id": "unvalidated-key-shape",
      "title": "Idempotency key is accepted with no format/type/length validation",
      "requirement": "API input-boundary handling: values used as a cross-request correlation/lookup key must be validated (non-empty, bounded length, expected type) before being trusted, per standard API hardening practice for idempotency headers.",
      "evidence": "app/charges.py post_charge: the only

*[... 691 more characters in the raw stream]*
```

---

**On human checkpoints.** There are none in this trajectory, and that is a property of the task rather than an omission. Each agent works inside a throwaway copy of the case in the OS temp directory, with network tools and delegation denied, so no action it can take reaches anything outside its sandbox. Ground rule 4 asks for approval before a *consequential* action; there is no consequential action available here to approve.

**Raw source.** `evidence/runs/2026-08-28-1202-solution-t3/cases/002-idempotency-key/verify.stream.jsonl` — every event, unedited, including the ones this page truncates.
