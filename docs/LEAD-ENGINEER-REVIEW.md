# Lead engineer review of the brief

**2026-08-28.** Written after reading the official PDF (`RULES.md`), `HACKATHON_BRIEF.md`, and
inspecting the environment. The brief asked to be argued with; this is the argument. Nothing here
is settled until Raj signs off — five decisions are parked in `REQUIREMENTS.md` §Open.

## The short version

The brief is well-shaped and the process discipline in it (freeze first, changelog during, honest
negative results) is exactly what the rubric pays for. **The plan is sound. The problem choice is
the weak part**, for two reasons that a judge will find quickly. Both are fixable cheaply, today,
before any code exists.

---

## Risk 1 — we author the cases *and* the tests *and* the fix. Git ordering does not answer that.

The freeze protocol proves *when* the benchmark was written. It cannot prove the benchmark was
not **conceived** to suit the workflow we already intended to build. We know we plan to build
adversarial verification, and then we go and write cases whose failures are exactly what
adversarial verification catches. Every commit is honestly ordered and the objection still lands:
*"you chose edge-case-heavy tasks because you knew your verifier was good at edge cases."*

This is the single strongest attack available against the entry, and it is aimed at Measured
Improvement (15) plus, by contagion, the credibility of Engineering (30).

**Fix, and it is cheap:** derive the cases from material we did not write. Public library
documentation, a real published spec, real issue threads from a permissively licensed repo — any
source where the requirements existed before we did. We then author the *harness*, not the
*problem*. The freeze protocol stays exactly as designed; it just now guards something worth
guarding.

Second-best fix if sourcing proves slow: **pre-register the failure taxonomy** — write down the
classes of production failure we will probe, and commit that, *before* designing the workflow.
Then the cases are traceable to a taxonomy rather than to a solution.

I would spend the first hour on this and no more. It changes what a judge can say about
everything downstream.

## Risk 2 — a pass-rate table is not "a final result the user can use"

End-to-End Quality is **20 points**, more than Measured Improvement, and the PDF's wording is
specific: *"produces a final result the user can use, with the finish of something a person would
sign their name to"*. An eval harness that prints 61% vs 84% is a research report. It is not
something the named user receives.

**Fix:** the workflow's output should be an artifact the developer actually gets — a production
readiness report on their change: what was verified, what failed and how, what was repaired, what
is still unproven, each item pointing at a test result or a line of code. The number then becomes
*evidence about* the artifact rather than being the whole deliverable. Same engineering, same
runs, and it converts a research demo into a tool, which is also a much better video.

This is the highest-value hour in the whole weekend and the brief does not mention it.

## Risk 3 — the problem sits in the judges' own back yard

"AI coding agents miss production requirements" is a real problem, but it is also the most-covered
territory in agent research, and Problem & User Value (15) rewards a *specific person* a reader
can picture. "Solo developers using coding agents" is a category, not a person.

I do not recommend switching domains — the weekend is too short and the correctness story is
genuinely strong. I recommend narrowing hard: one named user, one concrete moment (the merge with
no second reviewer), one recognisable consequence. That is a paragraph of work in the README, not
a change of project.

If Raj does want a differentiated domain, say so now and not Saturday. Switching after Friday's
freeze costs the whole experiment.

## Risk 4 — the fairness trap inside "hidden test pass rate"

If the visible requirements underspecify what the hidden tests check, the baseline is being
graded on requirements it was never handed. A judge can read that as rigged.

It is not rigged — *anticipating reasonable-but-unstated production requirements is the actual
thesis* — but that has to be said out loud, in the README, as the point of the experiment rather
than as a footnote. Stated: it is the strongest sentence in the entry. Unstated: it is the hole
someone puts a finger through.

Concretely: the visible case text should read like a real ticket (underspecified, as tickets are),
and the README should say plainly that the hidden tests encode production requirements a
competent reviewer would expect but that the ticket does not spell out.

## Risk 5 — instrumentation retrofitted is instrumentation re-run

Cost and wall-clock must be captured from run one. Two of the three metric rows the PDF suggests
need them, and adding the counters after thirty runs means re-running thirty runs on Sunday with
the clock gone. This is a Friday requirement, not a Saturday nicety. It is already written into
`playbooks/evidence-capture.md`; it needs to be true in the harness before the baseline, not after.

## Where the brief is right, and I would not touch it

- **Freeze before baseline, auditable history.** Correct, and rare. Keep it exactly.
- **Changelog written during, removed experiments kept.** The PDF asks for removed experiments by
  name. This is free marks most entrants will not collect.
- **Video finished Sunday, Monday is buffer.** Correct. The video is the one incompressible item.
- **"Do not assume our architecture is correct."** Also correct — and the corollary is that every
  component needs an **ablation**, not a memory of what the score was before it was added. Budget
  two or three ablations for the components the video will claim credit for.
- **Do not fabricate or target a number.** Non-negotiable, and now written into `CLAUDE.md`.

## Where I disagree with the brief outright

**Case count.** The brief plans ~3. The PDF says *"Ten or more cases is a good target when the
task allows it"* and asks for one deliberately hard case whose finding is explained. Three is a
fine Friday gate; three on Monday leaves points in two categories and invites the obvious
sample-size objection. This is a design constraint **now**: the case format has to be cheap enough
that ten is affordable. Decide the per-case authoring budget before authoring case one.

**Architecture-first framing.** The brief spends a lot of words on candidate agent components.
The rubric explicitly says purposeful choices beat component count. The smallest thing that could
move the number is: implement → adversarially verify → repair → re-verify, with one loop. Start
there, add only what an ablation earns.

---

## Recommended Friday experiment — the smallest credible one

1. **Sourcing (1h).** Pick the external source for case material. Commit the failure taxonomy we
   intend to probe. *This is the fix for Risk 1 and it happens before anything else.*
2. **Three cases (2h).** Visible ticket text (realistically underspecified) + hidden evaluator
   tests. One case deliberately hard. Format held to a budget that makes ten affordable.
3. **Freeze commit.** Nothing else in it. Hash into `benchmark/MANIFEST.md`.
4. **Harness (1.5h).** One scorer, `--arm` flag, writes `evidence/runs/<id>/` with per-case
   pass/fail, wall-clock, tokens and cost. Hidden tests executed by the harness only, never
   readable by an implementation agent — enforced by working directory, not by a prompt.
5. **Baseline run.** Same model, same repo access, a prompt a competent developer would write.
   Commit the evidence.
6. **Advanced arm (2h).** Implement → verify → repair → re-verify. One loop. Nothing else.
7. **Write the comparison down.** Whatever it says.

Friday's deliverable is step 7, not a working system. If the gap is not there, Saturday changes
the experiment rather than tuning a workflow that is not moving.

## What must be decided before any of that

The five in `REQUIREMENTS.md` §Open Decisions: the user, the per-case budget, which agent is under
test and whether both arms share it, the spend ceiling, and whether a human checkpoint stays in
the final workflow. Decisions 1, 2 and 3 block step 1. **Nothing substantial gets built until
they are called.**
