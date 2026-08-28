# Rubric tracker — score ourselves before the judges do

Re-score at every "sharpen up" and before the video. Be pessimistic: score what a stranger would
see in the repo today, not what is planned. Full criteria in `RULES.md` §6.

**Updated:** 2026-08-28 (after run 1) · **Self-score: 41 / 100**

| Criterion | Pts | Now | The gap | What closes it |
|---|---:|---:|---|---|
| Agent Solution & Engineering | 30 | 14 | Workflow exists and moves the number, but no component is ablated yet, and repair caused a regression | Smallest workflow that moves the number, plus an **ablation per component** so each one is justified by evidence rather than asserted |
| End to End Quality | 20 | 8 | Docs read like a person; nothing to run | A complete self-contained execution producing something the user can use, and prose that does not read as AI-generated (Gate 4) |
| Problem & User Value | 15 | 9 | User named (solo founder, no second reviewer); README opening not written yet | Name a specific user and a bottleneck a reader recognises; open the README with it |
| Measured Improvement | 15 | 7 | One comparison, n=1 per arm, variance unmeasured | Frozen benchmark, fair baseline, same scorer both arms, changelog rows tied to run ids, regressions reported |
| Reproducibility | 15 | 3 | Structure and conventions exist; no code, no guide | `REPRODUCTION.md` executed on a clean machine (Gate 3), versions pinned, runtime and cost stated |
| Hot Take / Insights | 5 | 4 | Real observed failure mode (confident-but-wrong findings) already written up | One observed failure mode turned into a lesson that changes what you would build next |

## The one that moves everything right now

**Measured Improvement is the bottleneck, and the fix is repetition, not features.** A +3
assertion result with ≥1 assertion of observed run-to-run noise cannot carry the submission.
Three runs per arm would cost roughly $7 equivalent and about an hour of wall clock, and would
either turn 61.1 vs 77.8 into a defensible claim or reveal it as noise. That is worth more than
a fourth benchmark case.

## Where points are most at risk

**Engineering (30) is the biggest block and the easiest to lose quietly.** It is not scored on
component count — the PDF says purposeful choices matter more. An agent that cannot show its own
measured contribution actively costs points here. Plan the ablations at the same time as the
components.

**End-to-End Quality (20) is worth more than Measured Improvement (15)** and is largely a
*writing and finish* line: "the finish of something a person would sign their name to rather
than an obvious AI generated draft". It is the cheapest 20 points in the rubric and the easiest
to leave on the table at 2am on Sunday. Protect the time.

**Reproducibility (15) is decided on someone else's machine.** It cannot be self-assessed from
this repo. Untested, assume it is worth 5, not 15.

**Hot Take is 5 points for one paragraph** — the best points-per-minute in the whole rubric, and
it needs a real observed failure, so it depends on having run enough to have seen one.

## Scoring notes

- A criterion only moves once the evidence exists in the repo. "Planned" scores zero.
- Record the date of each re-score. A tracker that has not moved in a day is a signal.
