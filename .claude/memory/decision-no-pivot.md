# Four pivots evaluated and rejected. Do not reopen before submission.

Decided 2026-08-28 by Raj, with `MASTER-HACKATHON-DECISION-HANDOFF.md` and two evaluations.

**Fantasy auction intelligence — rejected. The public data does not exist**, verified rather
than assumed: Sleeper documents **no auction fields**, MFL's `auctionResults` is **owner-only**,
nothing multi-season on Kaggle/nflverse, DataForce's own example is a 2016 *non-auction* draft.
No public data → no judge reproduction. It also fails on depth even with perfect data: price
prediction is regression, so the honest build is a model plus an LLM explaining it, which scores
badly against Engineering (30). ~6.5/10 as a hackathon entry, ~8.5 as a later product.

**ShortCheck — rejected, but close.** The generate-then-score design was right. It loses on the
**evaluator**: ours is pytest (binary, opinion-free); ShortCheck must score free-form English,
and avoiding LLM-as-judge means hand-written pattern rules across ~10 cases × ~8 facts × 7 error
types — brittle, with no fallback time. Copyright forces synthetic text sources, removing the
multimodal appeal that motivates the pivot. 76 realistic (55-85) vs 85 here.

**Why, honestly:** ShortCheck beats us on distinctiveness (our risk is reading as "another AI
code reviewer") and demo legibility. Both are **positioning problems, fixable in the README and
video framing in an hour** — not evidence problems. Sunk cost was checked: the verdict holds even
with an empty repo, because the evaluator-objectivity advantage is structural, not earned.
**ShortCheck is the better future entry — keep the idea.**

**Exit Test (agent cancels subscriptions, resists dark patterns) — rejected 2026-08-29.** The
contribution is published prior art: SusBench (Oct 2025) benchmarks dark-pattern susceptibility of
computer-use agents; "Don't Click That" (May 2026) covers obstructed *cancellation flows* and tests
the same mitigations it proposes; state-vs-claim verification is tau-bench's defining design.
Ceiling ~82 against this entry's realistic ~85, and it needed 4+ days.

**Accessibility remediation — rejected 2026-08-29, on our own evidence, not judgement.** Two spike
runs in `experiments/spike-a11y/`. A single plain pass did near-expert work on both a static
checkout and an interactive booking page: correct focus trap, Escape handling, focus return, real
buttons, native `<select>`, `autocomplete` attributes, and contrast ratios it stated to one decimal
that were correct to two when verified independently. **No baseline failure means no gap to
measure, and no gap means no Measured Improvement.** ~2 h, $0.76 equivalent. The lesson worth
keeping: a domain only works for this competition if the *plain* agent visibly fails, and those
domains are rarer than they look — this entry's 61.1% baseline is the asset, not the boring part.

**How to apply:** if a pivot is raised again, the answer is no unless the deadline moves. Spend
the remaining time on packaging — see [[constraint-packaging-is-the-gap]].

Related: [[reference-rubric-weights]] · [[reference-deadline-schedule]]
