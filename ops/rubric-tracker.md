# Rubric tracker — score ourselves before the judges do

Re-score at every "sharpen up" and before the video. Be pessimistic: score what a stranger would
see in the repo today, not what is planned. Full criteria in `RULES.md` §6.

**Updated:** 2026-08-29 midday (repro tested, evidence committed, trajectories + README done) · **Self-score: 82 / 100**

| Criterion | Pts | Now | The gap | What closes it |
|---|---:|---:|---|---|
| Agent Solution & Engineering | 30 | 22 | Workflow exists and moves the number, but no component is ablated yet, and repair caused a regression | Smallest workflow that moves the number, plus an **ablation per component** so each one is justified by evidence rather than asserted |
| End to End Quality | 20 | 16 | Docs read like a person; nothing to run | A complete self-contained execution producing something the user can use, and prose that does not read as AI-generated (Gate 4) |
| Problem & User Value | 15 | 13 | User named (solo founder, no second reviewer); README opening not written yet | Name a specific user and a bottleneck a reader recognises; open the README with it |
| Measured Improvement | 15 | 13 | One comparison, n=1 per arm, variance unmeasured | Frozen benchmark, fair baseline, same scorer both arms, changelog rows tied to run ids, regressions reported |
| Reproducibility | 15 | 13 | Structure and conventions exist; no code, no guide | `REPRODUCTION.md` executed on a clean machine (Gate 3), versions pinned, runtime and cost stated |
| Hot Take / Insights | 5 | 5 | Real observed failure mode (confident-but-wrong findings) already written up | One observed failure mode turned into a lesson that changes what you would build next |

## The one that moves everything right now

**Reproducibility (15) is now the weakest line, and a holdout block is the second.** The
measurement is done and it repeated exactly, so Measured Improvement is largely banked — except
that block 1 is a development set, which caps how strongly the number can be claimed. A freshly
sourced holdout, frozen before inspection, converts a development result into a validation
result. After that, `REPRODUCTION.md` executed on a clean machine is the single biggest
remaining pot of points that nothing else can substitute for.

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

---

## Re-score, Sat 29 Aug midday

**55 → 82.** What moved, and why each is defensible rather than optimistic:

- **Reproducibility 3 → 13.** `REPRODUCTION.md` was executed on a clean clone, found four real
  defects, and the guide names them. Versions pinned, runtime and cost stated, per-case expected
  scores verified against `evidence/`. Not 15, because it has still only been run on *this*
  machine from a local clone — a genuinely different machine would settle the last two points.
- **End-to-End 8 → 16.** README written from the user's problem, trajectories exist and are
  readable, the readiness report is a real artifact a person would use. Not higher until the
  video exists.
- **Problem & User Value 9 → 13.** Specific user, named bottleneck, opens on the double charge.
- **Engineering 18 → 22.** The assertion-level audit is the kind of evidence this line rewards:
  it shows the workflow's contribution honestly, including where it is unreliable. Still no
  per-component ablation, which is the remaining gap.
- **Measured Improvement 12 → 13.** Same numbers, but now every one of them is committed and
  re-derivable, and the composition instability is disclosed rather than hidden behind a total.

**The two things still worth points:** the video (blocks End-to-End) and an ablation of the
re-verify step (blocks Engineering). In that order.
