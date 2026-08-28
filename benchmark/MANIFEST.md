# Benchmark manifest

The first thing a sceptical judge should read. What the cases are, where their definition of
"correct" came from, when they were frozen, and whether anything changed since.

**Status: FROZEN — block 1, 3 cases, 18 hidden assertions.** Frozen 2026-08-28.
**Freeze commit: `4456df103276f4eaf895b5b893e85ac44c9b75ee`.** `git log` remains the authority.

## The rule this benchmark follows

**We did not author what "correct" means.** Every hidden assertion traces to a numbered clause in
a public document that existed before this repository. We wrote the ticket wording, the starting
stub, the test code and the harness — never the requirement. The mapping below is complete: if an
assertion is not in this table, it is not in the benchmark.

The visible ticket is deliberately underspecified, the way tickets arrive. The gap between the
ticket and the published standard **is the experiment**.

### What this does not claim

External sourcing makes the benchmark more credible. It does not make it unbiased, and we are
not claiming that it does.

**We chose which standards to use, which clauses within them to test, and which three features
to build cases around.** A different set of choices would produce a different number. Two
specific residual biases a judge should weigh:

1. **Selection.** We picked clauses that are crisply testable in a small sandbox. Requirements
   that are real but hard to assert -- operational, cross-service, or judgement-based -- are
   absent, and they may be where agent-written code fails most often.
2. **Feature choice.** Password reset, idempotency and CSV parsing are all domains with mature
   public specifications. Features without a published standard are the harder case for any
   verification workflow, and this benchmark says nothing about them.

What external sourcing does buy is narrower and still worth having: **the pass/fail line for each
assertion was set by a document we do not control**, so we could not tune the definition of
"correct" toward whatever our workflow happened to be good at. That is a real constraint on us,
and it is checkable clause by clause in the tables below.

## Freeze record

| Block | Cases | Hidden assertions | Frozen | Freeze commit |
|---|---|---|---|---|
| 1 | 001, 002, 003 | 18 | 2026-08-28 | `4456df1` — `freeze: benchmark block 1` |

The freeze commit contains the cases and hidden tests **and nothing else**, and lands **before**
any baseline evidence commit. History is never squashed.

## Cases

| ID | Description | Failure class | Hidden assertions | Hard case |
|---|---|---|---|---|
| 001-password-reset | Self-service forgot-password flow | security / credential lifecycle | 6 | |
| 002-idempotency-key | `Idempotency-Key` on `POST /charges` | concurrency / retry semantics | 6 | ⭐ |
| 003-csv-import | Bulk user import from uploaded CSV | parsing / data integrity | 6 | |

Three distinct failure classes and three distinct kinds of authority, so the headline number is
not evidence about one class only.

---

## Source mapping — 001 password reset

Source: **OWASP Application Security Verification Standard v4.0.3**, §V2 Authentication.
Retrieved and quoted verbatim 2026-08-28.

| Test | Clause | Quoted requirement |
|---|---|---|
| `test_token_expires_within_ten_minutes` | **V2.7.2** | "expires out of band authentication requests, codes, or tokens after 10 minutes" |
| `test_token_is_single_use` | **V2.7.3** | tokens "are only usable once" |
| `test_token_is_bound_to_the_account_that_requested_it` | **V2.7.3** | usable "only for the original authentication request" |
| `test_recovery_never_discloses_the_existing_password` | **V2.5.3** | "password credential recovery does not reveal the current password in any way" |
| `test_user_is_notified_when_the_password_changes` | **V2.5.5** | "if an authentication factor is changed or replaced, that the user is notified of this event" |
| `test_reset_requests_are_rate_limited` | **V2.2.1** | "anti-automation controls are effective at mitigating breached credential testing, brute force, and account lockout attacks… no more than 100 failed attempts per hour is possible on a single account" |

**Two derivations stated openly, because they are the only places we interpreted rather than
transcribed:**

1. **V2.2.1** is written about failed authentication attempts. Our surface is the recovery
   endpoint, so it is applied to `request_reset`: an unbounded recovery endpoint is a mail-bombing
   and token-generation oracle. The threshold (100/hour, single account) is the clause's own
   figure, unchanged.
2. **ASVS V2.5.1** ("recovery secret is not sent in clear text") was considered and **dropped**.
   It governs transmission, and stretching it to cover token *storage* would have meant inventing
   a requirement the clause does not make. It appeared in `docs/BENCHMARK-CASE-PROPOSAL.md`; it is
   not in the benchmark.

---

## Source mapping — 002 idempotency key ⭐ hard case

Source: **Stripe API documentation, "Idempotent requests"**
(docs.stripe.com/api/idempotent_requests). Retrieved and quoted verbatim 2026-08-28.

| Test | Quoted documented behaviour |
|---|---|
| `test_first_result_is_replayed_verbatim` | "saving the resulting status code and body of the first request made for any given idempotency key… Subsequent requests with the same key return the same result" |
| `test_failed_results_are_replayed_not_retried` | "regardless of whether it succeeds or fails… return the same result, **including 500 errors**" |
| `test_same_key_with_different_params_is_an_error` | "compares incoming parameters to those of the original request and **errors if they're not the same** to prevent accidental misuse" |
| `test_an_in_flight_key_is_not_served_the_cached_result` | "if… the request **conflicts with another request that's executing concurrently**, we don't save the idempotent result… You can retry these requests" |
| `test_keys_expire_after_a_day` | "remove keys from the system automatically after they're **at least 24 hours old**. We generate a new request if a key is reused after the original is pruned" |
| `test_validation_failures_are_not_cached` | "If incoming parameters fail validation… we don't save the idempotent result because no API endpoint initiates the execution. You can retry these requests" |

**Two notes:**

1. **Concurrency is modelled deterministically, not with threads.** The stub provides a
   `before_execute()` hook (documented in the visible contract as an operations extension point).
   The hidden test uses it to deliver a second same-key request while the first is inside
   `_execute`. This tests the documented invariant without a race, so the result is reproducible.
   The test asserts *behaviour* — no double execution, no premature cached success, retryable
   afterwards — and never a specific status code, which the ticket does not specify.
2. Stripe's clause about `GET`/`DELETE` requests ignoring idempotency keys has **no testable
   surface here** — the case's API is POST-only by construction. It is omitted for that reason,
   not because it was inconvenient.

---

## Source mapping — 003 CSV import

Source: **RFC 4180**, §2 "Definition of the CSV Format". Retrieved and quoted verbatim
2026-08-28.

| Test | Rule | Quoted rule |
|---|---|---|
| `test_quoted_field_may_contain_a_comma` | **6** | "Fields containing line breaks (CRLF), double quotes, and commas should be enclosed in double-quotes" |
| `test_doubled_quote_inside_a_quoted_field_is_a_literal_quote` | **7** | "a double-quote appearing inside a field must be escaped by preceding it with another double quote" |
| `test_quoted_field_may_span_lines` | **6** | as above — the record continues across the physical line break |
| `test_final_line_break_is_optional` | **2** | "The last record in the file may or may not have an ending line break" |
| `test_header_row_is_not_imported_as_a_user` | **3** | "an optional header line appearing as the first line of the file with the same format as normal record lines" |
| `test_spaces_are_part_of_the_field` | **4** | "Spaces are considered part of a field and should not be ignored" |

---

## Pre-freeze sanity check — 2026-08-28

Run before freezing, to establish that the benchmark is neither impossible nor trivial. Both
scratch implementations were written outside the repository and **were not committed** — a
solution key next to the tests is a contamination risk.

| Implementation | Visible tests | Hidden assertions |
|---|---|---|
| Reference (correct) | 10 / 10 | **18 / 18** |
| Naive (the obvious first attempt) | **10 / 10** | **7 / 18 (38.9%)** |

Per case, naive: 001 → 2/6 · 002 → 2/6 · 003 → 3/6.

**A naive implementation passes every test that ships with the ticket and fails 11 of the 18
documented invariants.** That is the condition the experiment needs: the visible tests do not
reveal the gap, and the external standards do.

Method, if a judge wants to repeat it: copy `benchmark/cases/<id>/workspace/` to a scratch
directory, implement the stub, then run
`CASE_WORKSPACE=<scratch> python -m pytest benchmark/hidden/<id>`.

*Open item for Sunday: decide whether to publish the reference implementations under
`benchmark/reference/` so judges can verify satisfiability directly. Not done now — the
contamination risk during the experiment outweighs it.*

## Structure

```
benchmark/
├─ cases/NNN-slug/
│  ├─ TICKET.md         VISIBLE. The underspecified ticket, used as the agent's prompt
│  └─ workspace/        VISIBLE. Stub + the tests that ship with the ticket
├─ hidden/NNN-slug/
│  └─ test_invariants.py    HIDDEN. Never in an implementation agent's working set
└─ hidden/conftest.py       puts the produced workspace on sys.path via CASE_WORKSPACE
```

Isolation is enforced by the harness, not by an instruction in a prompt: the agent runs with its
working directory set to a copy of `workspace/` in the OS temp directory, outside this repository
entirely. It has no path to `benchmark/hidden/`.

## Post-freeze changes

Every change to a frozen case gets a row here: the defect, the change, the new freeze commit, and
confirmation that **both arms were re-run**. No silent edits.

| Date | Case | Defect | Change | Re-ran both arms? |
|---|---|---|---|---|
| _none_ | | | | |

Protocol: `.claude/playbooks/benchmark-independence.md`.
