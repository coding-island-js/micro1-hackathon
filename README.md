# Does this code actually do what the ticket asked?

An AI wrote your payment retry logic. Every test passed. It still charges the customer twice.

This project measures whether a second AI, told to review adversarially rather than to help, can
catch that before you ship — and reports the result as evidence a person can check, not as a
verdict you have to trust.

**Baseline: 11 of 18, on all four runs. This workflow: 14 of 18 — and 12 to 15 across six runs of
the same scoring pipeline. Every one of them beats the baseline. None of them fixes the same
things twice.**

**Five-minute walkthrough:** [`video/solution-video.mp4`](video/solution-video.mp4) (4:47,
captions in [`video/solution-video.srt`](video/solution-video.srt), plain-text transcript in
[`video/transcript.txt`](video/transcript.txt)). It covers the problem and the baseline, one run
end to end, the comparison, the changelog, the change that mattered most, and the experiment that
was removed.

---

## Who has this problem

A solo founder shipping their own software. In this case me, but the shape is common: one person,
several small products, an AI agent doing most of the typing, and **no second developer anywhere
in the loop**.

The specific person I built this for reviews their own code at 11pm, having written none of it.
There is no colleague to ask. There is no QA. The only signal that the work is finished is the
agent saying "done, tests pass" — and the tests it is talking about are the ones that came with
the ticket, which describe what someone remembered to ask for, not what the feature actually has
to do.

## The bottleneck

Coding agents are good at satisfying the tests in front of them and bad at knowing which tests
should have existed.

Our baseline agent passes **10 out of 10** of the tests that ship with the three tickets. It
passes **11 of the 18** requirements those features are actually held to. The seven it misses are
not obscure: key expiry, rate limiting, what happens when two identical requests arrive at once,
what happens when the connection drops halfway through a charge.

Nobody wrote those seven down in the ticket, because tickets are written by people who assume you
know. So a green test run means nothing, and the founder either reviews code they didn't write and
don't have context on, or ships and finds out from a customer.

That is the gap this measures: **not "is the code correct" but "is the ticket's silence going to
cost you money".**

## What this does

You hand it a ticket and a codebase. It writes the implementation, then runs an adversarial
reviewer over it that is explicitly told to find how it will fail in production and is **forbidden
from editing anything**. The findings go to a repair step. Then the reviewer runs again on the
repaired code, because a repair can break something that worked.

What you get back is a **readiness report**: what was found, which published rule each finding
violates, what happens in production if you ship it, and what is *still* wrong after repair. It
ends with a recommendation and this line:

> **This is a recommendation, not an approval.**

That is the whole design position. The workflow does not decide whether to ship. It puts a
reviewer's worth of evidence in front of the person who does.

A real one is at
[`evidence/runs/2026-08-28-1202-solution-t3/cases/002-idempotency-key/readiness-report.md`](evidence/runs/2026-08-28-1202-solution-t3/cases/002-idempotency-key/readiness-report.md).

## Results

Three cases, 18 hidden assertions, same tickets and same scorer for both arms. The scorer does not
know which arm produced the code.

| Metric | Do nothing | Baseline: one agent, one pass | This workflow | Change |
|---|---|---|---|---|
| **Hidden-test pass rate** | 1/18 (5.6%) | **11/18 (61.1%)** | **14/18 (77.8%)** | **+16.7 pts** |
| Spread in the total | — | 0.0 over 4 runs | 0.0 over 3 runs | — |
| Tests shipped with the ticket | 0/10 | 10/10 | 10/10 | no change |
| Wall clock, 3 cases (mean per run) | — | 90 s | 1105 s | ×12.3 |
| Cost per run, mean (API-rate equivalent) | — | $0.268 | $2.014 | ×7.5 |

Both cost and wall-clock rows are means over all runs in that arm — 4 baseline, 3 solution — and
the ratios are computed from the unrounded means.

Per case:

| Case | Baseline | This workflow |
|---|---|---|
| `001-password-reset` | 3/6 | 4/6 |
| `002-idempotency-key` | 3/6 | 5/6 |
| `003-csv-import` | 5/6 | 5/6 |

**Both arms produced the same number on every single run** — four baseline runs at exactly 11/18,
three solution runs at exactly 14/18. The 16.7-point gap is not noise, and it is why the
experiment we removed stands out so clearly: that one swung 16.6 points across three runs of an
identical configuration.

### The stable total is hiding something, and you should know about it

The baseline really is identical run to run, assertion for assertion. **The workflow is not.**

It lands on 14/18 every time, but *which* requirements it fixes changes between runs — two runs
fix four and break one, the third fixes three and breaks nothing. Four of the eighteen assertions
flip, and they happen to cancel out:

| Assertion | Baseline | Run 1 | Run 2 | Run 3 |
|---|---|---|---|---|
| `002::keys_expire_after_a_day` | fail | **pass** | **pass** | **pass** |
| `002::same_key_with_different_params_is_an_error` | fail | **pass** | **pass** | **pass** |
| `001::reset_requests_are_rate_limited` | fail | fail | **pass** | **pass** |
| `001::user_is_notified_when_the_password_changes` | fail | **pass** | fail | fail |
| `002::an_in_flight_key_is_not_served_the_cached_result` | fail | **pass** | **pass** | fail |
| `002::failed_results_are_replayed_not_retried` | **pass** | fail | fail | **pass** |

Two requirements are fixed reliably. Four are a coin toss, including one the baseline already
passed that the workflow breaks in two runs out of three.

I only found this because I compared assertion by assertion rather than trusting a stable total.
If you are measuring an agent workflow, **a repeatable score is not the same as repeatable
behaviour**, and the aggregate will happily hide that from you. This is the single most useful
thing I learned building it.

Every number above is re-derivable from [`evidence/runs/`](evidence/runs/), which is committed.
Reproduce it with [`REPRODUCTION.md`](REPRODUCTION.md) — about 20 minutes and $2.30, or $0.10 for
a single case if you just want to check we are honest.

### What it costs you

Roughly seven and a half times the money and twelve times the wall clock, to catch three
requirements per three tickets that would otherwise have reached production. Whether that trade is worth it depends
entirely on what your bug costs. For a double charge on a customer's card, it is not close.

## The hard case

`002-idempotency-key` is the one that matters, and it is deliberately the nastiest.

The ticket says: *"if we see the same key again we shouldn't put a second charge through."* It does
not mention concurrency, it does not mention expiry, and it does not mention what happens when the
call fails halfway. The baseline reads that sentence, writes a dictionary lookup, passes all four
shipped tests, and ships a payment system that double-charges under two separate conditions.

The reviewer caught both without ever seeing the hidden tests. It independently derived Stripe's
documented key-scoping and in-flight semantics from the ticket's context, then named the rule it
was applying:

> Idempotency-Key semantics require mutual exclusion for the duration of processing, not just
> de-duplication of completed results.

And then — the part I find most useful — after the repair, it **still** reported a remaining
double-charge window, so the report goes to the developer saying "5 issues still flagged" rather
than "done". You can read that happen in
[`trajectories/solution__002-idempotency-key__reverify.md`](trajectories/solution__002-idempotency-key__reverify.md).

## Why only three cases

The brief suggests ten or more, and three is fewer. The reason is that I chose to spend the budget
on **repetition instead of breadth**: ten runs across three cases rather than one run across ten.

Given that the first comparison showed a 16.7-point gap, the question that decided whether this
project had a result was "is that gap real?", not "does it also appear on case four". Repeating
each arm three to four times answered it, and it is what exposed the removed experiment's 16.6-point
instability — which one run per arm would have shown as a modest improvement.

It is a real limitation and it is the first thing I would fix with another day. Three cases cannot
tell you where this stops working.

## What existed before

Code review agents are not new, and I am not claiming the reviewer is the novel part.

Two things here are less common. First, **the reviewer is not allowed to edit**, so its findings
have to survive being written down and handed to a different agent, which makes them auditable.
Second, and more to the point, **the definition of correct was not written by me.** Every one of
the 18 hidden assertions traces to a numbered clause in a public document that existed before this
repository — Stripe's published idempotency behaviour, the OWASP password reset guidance, RFC 4180.
The mapping is in [`benchmark/MANIFEST.md`](benchmark/MANIFEST.md), clause by clause.

That matters because the easiest way to win a benchmark is to author the definition of winning. I
could not tune "correct" toward what my workflow happened to be good at, because I do not control
those documents. `benchmark/MANIFEST.md` also lists the two biases that survive that precaution.

## Reproducing it

[`REPRODUCTION.md`](REPRODUCTION.md). It was executed on a clean clone on 29 August and it found
four real defects in this repository, which are listed in the guide itself.

## The changelog

[`CHANGELOG-IMPROVEMENT.md`](CHANGELOG-IMPROVEMENT.md) — one row per experiment, written as each
ran, including the one that was removed.

Short version: the baseline established the floor, iteration 1 added verify/repair/re-verify and
kept it, and iteration 2 tried to make the reviewer safer and made everything worse.

## Main failure mode

**Confident-but-wrong findings.** The reviewer writes a well-argued case for a requirement that is
not the real one, and the repair step believes it.

On case 002 it argued that caching a 5xx response against an idempotency key blocks legitimate
retries. That is a reasonable thing to believe, and it is the opposite of Stripe's documented
contract. Repair acted on it and **broke `002::failed_results_are_replayed_not_retried`, which the
baseline passes.** It does this in two runs out of three — the regression is not reliable either,
which is worse than if it were, because you cannot test for it once and call it handled.

Two assertions are never reached by any arm in any run: `001::token_expires_within_ten_minutes`
and `003::spaces_are_part_of_the_field`. Case 003 does not move at all — every gain is in
lifecycle and concurrency work, which is where a ticket's silence is most expensive and where a
reviewer has the most to say.

## Hot take

Adding a reviewer agent helped. **Adding a mechanism to make that reviewer safer made things 13
points worse.**

Iteration 2 gated every repair behind evidence: a finding could only change code if its own
reproduction failed and it did not contradict a documented contract. It sounds obviously correct.
It scored 64.8% against the plain workflow's 77.8%. It suppressed two findings that were right,
and across three runs each it did not stop the wrong one either — that assertion fails in two runs
of three with the gate and two of three without it.

The reason is the transferable bit. **The gate screened the reviewer's argument.** Does it
reproduce, is it well grounded — which measures how well an LLM argued, the one thing an LLM is
best at faking and worst at calibrating. The finding that actually hurt us was dangerous for an
entirely different reason: applying it **deleted behaviour that already worked**, and nothing in
the gate was looking at that.

So: **screen the change, not the argument.** The question to ask before a repair lands is not "did
the reviewer prove this?" but "does applying this remove something that currently passes?" That is
cheap, needs no judgement, and would have caught the one case that mattered without touching the
two that did not.

If you are building one of these: your verifier's confidence is not a signal, and any gate you
build out of its own reasoning inherits its blind spots. Gate on observable consequences.

And the one I nearly missed: **a repeatable score is not repeatable behaviour.** Three runs
returned 14/18 and I treated that as settled. Underneath, only two of the fixes were reliable and
four assertions were flipping run to run, cancelling out to the same number by coincidence. If I
had shipped on the total, I would have told you this workflow reliably fixes key expiry, parameter
mismatch, rate limiting and in-flight collisions. It reliably fixes the first two. Aggregate
metrics are where agent instability goes to hide — diff the assertions.

## Honest limits

- **Three cases, one model, one domain.** This says nothing about where the effect stops.
- **Block 1 is a development set.** Only iteration 2 was designed from hidden results, and it was
  removed, so the shipped workflow is effectively pre-registered — but a properly frozen holdout
  would be stronger and I did not have time to build one.
- **The workflow breaks an assertion the baseline passes, in two runs out of three.** It is
  reported above rather than netted out, and it is not reliable enough to test for once.
- **$13.87 is API-rate equivalent, not money spent.** These runs went through a Claude subscription;
  actual incremental cost was $0.
- I also spent two hours on Saturday testing whether the same approach helps with web accessibility.
  It does not — a single plain pass already does near-expert work there, so there is no gap to
  close. That negative result is in `experiments/spike-a11y/`.

---

Built for the micro1 Agentic Workflows Hackathon, August 2026, by Rajan Lakhani.
