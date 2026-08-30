# Six pivots evaluated and rejected. Do not reopen before submission.

Decided 2026-08-28 by Raj, with `MASTER-HACKATHON-DECISION-HANDOFF.md` and two evaluations.

**Fantasy auction — rejected.** No public auction data exists: Sleeper documents no auction
fields, MFL's `auctionResults` is owner-only, nothing multi-season on Kaggle/nflverse. No data,
no judge reproduction. Also fails Engineering: price prediction is regression plus an LLM
explaining it.

**ShortCheck — rejected, but close.** Generate-then-score was right; it loses on the evaluator.
Ours is pytest, binary and opinion-free. ShortCheck must score free-form English, and avoiding
LLM-as-judge means brittle hand-written pattern rules with no fallback time. Copyright forces
synthetic sources, removing the multimodal appeal. 76 vs 85 here. **Keep the idea for later.**

**Exit Test (agent cancels subscriptions) — rejected 2026-08-29.** Published prior art: SusBench
(Oct 2025) benchmarks dark-pattern susceptibility of computer-use agents; "Don't Click That"
(May 2026) covers obstructed cancellation flows and tests the same mitigations; state-vs-claim
verification is tau-bench's defining design. Ceiling ~82 vs ~85 here, and needed 4+ days.

**Five domains tested and all five passed, 2026-08-29** — accessibility on a static page,
accessibility on an interactive page, recipes with hidden allergens, pickleball scoring, poker
side pots. Spikes in `experiments/spike-a11y/`, `spike-allergen/`, `spike-rules/`. A plain agent
handled every one, including hidden allergens and side-pot arithmetic. ~$2 equivalent, $0 real.

**The lesson, and it is the reason not to keep looking:** a domain only works here if the *plain*
agent visibly fails, and modern models rarely do on tasks that are common and well documented.
That makes this entry's 61.1% baseline the asset, not the boring part. It is now a changelog row.

**How to apply:** if a pivot is raised again, the answer is no unless the deadline moves. Spend
the remaining time on packaging — see [[constraint-packaging-is-the-gap]].

Related: [[reference-rubric-weights]] · [[reference-deadline-schedule]]
