# Playbook — the experiment loop

Every meaningful change to the solution is an experiment, and every experiment leaves two
artifacts: a file in `experiments/` and a row in `CHANGELOG-IMPROVEMENT.md`. Written **when the
experiment runs**, not on Sunday. Reconstructed changelogs read as reconstructed.

## The loop

1. **State the hypothesis before changing anything.** "Adding X will fix Y, which I observed in
   run Z, case N." A hypothesis that cannot name the observation that provoked it is a guess —
   run the diagnosis first.
2. **Open `experiments/NNN-slug.md`** from the template. Fill in hypothesis, the observation,
   and the change, before running.
3. **Change one thing.** Two changes in one run means neither is attributable, and attribution
   is exactly what the Measured Improvement line is scoring.
4. **Run the same eval, same cases, same scorer.** No exceptions, including "just a quick check".
5. **Record the result** — primary metric, per-case deltas, wall-clock, cost. Note regressions
   explicitly; a change that gains two cases and loses one has gained one.
6. **Decide: keep / modify / remove.** Write the reason. If the change did not move the number,
   **remove it** — an unjustified component costs points under Agent Solution & Engineering.
7. **Write the changelog row** and close the experiment file with the lesson.

## The changelog row

`STAGE | WHAT YOU TRIED AND WHY | EVIDENCE | DECISION / LEARNING` — the PDF's own columns.
Evidence is a run id and a number, never a description. Decision is one of keep / revised /
removed, plus the lesson in a sentence.

**Removed experiments stay in the changelog.** The PDF asks for them by name: *"Include
experiments you later removed and explain what they taught you about the problem."* They score
twice — under Measured Improvement, and as raw material for the Hot Take. Deleting a failure to
make the story look cleaner throws away points.

## Ablations

Where practical, measure a component by **removing it** from the final workflow and re-running,
rather than by remembering what the score was before it was added. Scores drift as everything
else changes; an ablation against the current system is the honest measurement and is what
"which design choices helped the agent" is asking for.

Budget: an ablation costs one eval run. On a three-day project, ablate the two or three
components the video will actually claim credit for, not all of them.

## When the number does not move

Say so, in the changelog, with the run id. Then diagnose before iterating: read the per-case
failures and name the class. Tuning prompts against an unchanged number is how a Saturday
disappears. If the hypothesis itself is dead, that is a finding — it belongs in the README's
failure-mode section and probably in the Hot Take.

## Numbering

`experiments/NNN-slug.md`, zero-padded, never renumbered, never deleted. An abandoned experiment
keeps its number and gets a one-line "abandoned, why" — the gap in a sequence raises a question
that costs more to answer than the file costs to keep.
