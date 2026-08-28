# Friday benchmark — three externally grounded cases (proposal)

**2026-08-28. Awaiting Raj's approval. Nothing implemented yet.**

Sourcing was timeboxed. Citations below were fetched and verified today, not recalled — the
quoted text is the source's own wording. Remaining sourcing work is ~20 minutes to pin permanent
version-locked URLs for the ASVS and NIST references.

## The rule these cases follow

**The requirements and failure conditions come from public specifications we did not write. We
author only the ticket wording, the starting stub, and the test implementation.** Every hidden
test traces to a numbered clause in an external document, and `benchmark/MANIFEST.md` records
that mapping. A judge can check any assertion against its source.

This is what answers the objection in `docs/LEAD-ENGINEER-REVIEW.md` §Risk 1. It is not that we
were honest about ordering — it is that we did not get to choose what "correct" means.

---

## Case 001 — Password reset flow

**Source:** OWASP Application Security Verification Standard v4.0.3, §V2.5 Credential Recovery,
§V2.7 Out-of-Band Verifiers, §V2.2 General Authenticator Requirements.

**User-facing requirement (the visible ticket):** *"Add a forgot-password flow. User submits
their email, gets a reset link, clicks it, sets a new password."* Underspecified on purpose —
this is how the ticket actually arrives.

**Production invariants derived from the source** (each is a hidden test, each cites its clause):

| # | Invariant | Clause | Verbatim source text |
|---|---|---|---|
| 1 | Reset token expires | V2.7.2 | "expires out of band authentication requests, codes, or tokens **after 10 minutes**" |
| 2 | Token is single-use, bound to its request | V2.7.3 | "tokens are **only usable once**, and only for the original authentication request" |
| 3 | Recovery secret not stored/sent in clear | V2.5.1 | "a system generated initial activation or recovery secret is **not sent in clear text** to the user" |
| 4 | Recovery never discloses the existing password | V2.5.3 | "password credential recovery **does not reveal the current password** in any way" |
| 5 | User is notified when the factor changes | V2.5.5 | "if an authentication factor is changed or replaced, that the **user is notified** of this event" |
| 6 | Anti-automation on the endpoint | V2.2.1 | "no more than **100 failed attempts per hour** is possible on a single account" |

**Why it is a fair coding-agent benchmark:** every one of these is a documented, numbered
requirement that predates this repo, and none of them is stated in the ticket. That gap *is* the
thesis — a competent reviewer expects them; a single-pass agent typically implements 1 and
misses 2, 5 and 6. Nothing here is a trick; it is the published standard for the feature being
built.

**Effort:** ~1h (ticket 15m · stub 10m · six hidden tests 35m).

---

## Case 002 — Idempotent POST endpoint ⭐ *proposed hard case*

**Source:** Stripe API documentation, "Idempotent requests" (docs.stripe.com/api/idempotent_requests).

**User-facing requirement:** *"Our charge endpoint gets retried by clients on network errors and
we're double-charging people. Add support for an `Idempotency-Key` header."*

**Production invariants derived from the source:**

| # | Invariant | Verbatim source text |
|---|---|---|
| 1 | First result is replayed verbatim | "saving the resulting **status code and body** of the first request made for any given idempotency key" |
| 2 | Failures are replayed too, not retried | "regardless of whether it succeeds or fails. Subsequent requests with the same key return the same result, **including `500` errors**" |
| 3 | Same key + different params must error | "compares incoming parameters to those of the original request and **errors if they're not the same**" |
| 4 | Concurrent conflict is not cached | "if... the request **conflicts with another request that's executing concurrently**, we don't save the idempotent result" — the retry must remain possible |
| 5 | Keys expire | "remove keys from the system automatically after they're **at least 24 hours old**" |
| 6 | Scope is POST only | "Don't send idempotency keys in `GET` and `DELETE` requests because it has no effect" |

**Why this is the hard case:** invariants 2, 3 and 4 are where implementations reliably
under-deliver. Caching only *successes* looks correct and passes any happy-path test — and is the
exact bug that double-charges a customer when the first attempt 500s. Invariant 4 needs real
concurrency reasoning, not just a dictionary lookup.

**Why it is fair:** the behaviour is not our opinion of what idempotency should mean. It is the
published contract of the most widely-copied payments API in the industry, and any developer
implementing this feature would be expected to have read it.

**Effort:** ~1h15 (the concurrency test needs care to stay deterministic — a controllable barrier
in the stub, not `sleep`).

---

## Case 003 — CSV bulk import

**Source:** RFC 4180, §2 "Definition of the CSV Format", rules 2–7. Verified verbatim today.

**User-facing requirement:** *"Let admins bulk-import users from a CSV file."*

**Production invariants derived from the source:**

| # | Invariant | Rule | Verbatim source text |
|---|---|---|---|
| 1 | Quoted fields may contain commas | 6 | "Fields containing line breaks (CRLF), double quotes, and commas **should be enclosed in double-quotes**" |
| 2 | `""` is an escaped quote | 7 | "a double-quote appearing inside a field **must be escaped by preceding it with another double quote**" |
| 3 | Quoted fields may contain CRLF | 6 | as above — a record can span physical lines |
| 4 | Trailing newline is optional | 2 | "The last record in the file **may or may not** have an ending line break" |
| 5 | Header row handled as such | 3 | "an optional header line appearing as the first line" |
| 6 | Spaces are data | 4 | "Spaces are considered part of a field and **should not be ignored**" |

**Why it is fair, and why it is worth including:** the naive implementation is
`line.split(',')`, it passes every happy-path test, and it silently corrupts real data the first
time someone's job title contains a comma. It is the cheapest, most deterministic case in the
set — no clock, no concurrency, no network — and it probes a completely different failure class
(parsing) from 001 (security) and 002 (concurrency). That diversity is worth more than a third
security case.

**Effort:** ~45m. The cheapest of the three.

---

## Coverage check

| Case | Failure class | Source type | Needs a clock? | Needs concurrency? |
|---|---|---|---|---|
| 001 password reset | security / lifecycle | security standard | yes | no |
| 002 idempotency | concurrency / retry | vendor API contract | yes | yes |
| 003 CSV import | parsing / data integrity | IETF RFC | no | no |

Three distinct failure classes, three distinct kinds of authority. If all three showed the same
class, the headline number would only be evidence about that class.

---

## Friday time budget — honest version

| Item | Est. |
|---|---|
| Finish sourcing (pin version-locked URLs) | 0h20 |
| Shared scaffold: one small service stub + pytest layout, reused by all three | 0h45 |
| Case 001 | 1h00 |
| Case 002 (hard case) | 1h15 |
| Case 003 | 0h45 |
| **Freeze commit** | 0h05 |
| `eval/` harness — one scorer, `--arm`, evidence capture | 1h15 |
| Baseline run + advanced arm build + run | 1h15 |
| Write the comparison down | 0h20 |
| **Total** | **~7h** |

**That is a full day and it has no slack.** If it slips, the cut is to **freeze two cases on
Friday and add 003 as a second frozen block on Saturday** — the protocol in
`playbooks/benchmark-independence.md` already covers post-freeze blocks, and results get reported
both ways. Do not cut the harness or the evidence capture to save time; those are what the
rubric is actually buying.

---

## Two decisions this proposal needs

### 1. Language: Python 3 + pytest — recommended

Judges run this from a clean environment. Python 3.12 with `pytest` and nothing else means
`pip install pytest` and go — no `npm install`, no lockfile drift, no build step. Hidden tests
stay trivially isolatable (the harness runs pytest against `benchmark/hidden/`, the agent never
gets that directory in its working set). Node would work; Python removes a whole class of
reproduction failure for the judge.

### 2. The user artifact — lean, and nearly free

You chose repaired code plus a readiness report. Concretely, per case the workflow emits
`readiness-report.md`, about one page:

- **Invariant checked** — with its source citation
- **Verdict** — held / failed / unproven
- **Evidence** — the test id and the actual failure output, or the file and line that satisfies it
- **What was repaired** — the diff that fixed it, and what re-verification showed
- **Still unproven** — what the workflow could not establish, stated plainly

The verifier already has to produce this data structurally in order to drive the repair step, so
the report is a rendering of state we hold anyway — I estimate 30 minutes, not a feature. The
"still unproven" section is the part that makes it feel like a real engineering artifact rather
than a score, and it is the honest thing to show a judge.

**One caution:** the report must never become the thing being optimised. The measured claim stays
hidden-test pass rate. The report is the artifact the user receives; the number is the evidence
that the artifact is worth receiving.

---

## Budget: $0 incremental, and it is verified

Both arms run through the **Claude Code CLI in headless mode** (`claude -p`), on your existing
subscription. Verified working today on this machine (v2.1.250):

```
claude -p "..." --output-format json --model <same for both arms>
→ {"num_turns": 1, "duration_ms": 1371, "total_cost_usd": 0.0239, "usage": {...}}
```

That single call returns **wall-clock, turn count, token usage and an equivalent-API-cost figure
per run** — the whole metrics table, metered automatically, for no extra spend and no extra code.
`--output-format stream-json` gives the full tool-call/tool-result stream, which is deliverable 4
(agent trajectories) captured for free rather than hand-written.

**No programmatic API spend is necessary.** Nothing in the plan needs `ANTHROPIC_API_KEY`.

For the judge's reproduction path, `REPRODUCTION.md` will state both routes honestly: run it on a
Claude subscription at no marginal cost, or with an API key at an approximate cost we will report
from the real `total_cost_usd` totals. Same commands either way.

Fairness holds: same model, same tool, same permissions and same case text for both arms — the
only difference is the workflow. Ablations and re-runs cost nothing, which is the reason to be
generous with them rather than sparing.
