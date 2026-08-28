# Freeze the benchmark before the baseline runs — the ordering is the evidence

Decided 2026-08-28, at repo creation.

The commit order is: (1) case requirements, (2) hidden evaluator tests, (3) **freeze commit**,
(4) baseline run, (5) only then build and tune the solution. `benchmark/MANIFEST.md` records the
freeze date and the freeze commit hash. Git history is never squashed.

**Why:** the whole entry rests on one claim — that the measured improvement is real. A judge who
suspects the benchmark was shaped to flatter the final architecture discounts every number in
the README, and there is no way to argue back after the fact. The freeze commit is the only
cheap, checkable proof that the cases existed before the thing they score. Ground rule 2 —
"make it clear what existed before the competition and what you added" — makes the history part
of the submission.

**How to apply:**
- A hidden test never enters the context of an agent that writes an implementation.
- Changing a frozen case is allowed only for a genuine defect, and it costs a changelog row
  naming the defect plus a **re-run of both arms**. Never a silent edit.
- If a case turns out to be unfair to the baseline, fix it *before* the freeze or not at all.
- Adding cases after the freeze is fine; they go in a new numbered block with their own freeze
  commit, and results are reported both ways.

Related: [[constraint-ten-case-target]] · [[decision-evidence-is-tracked]]
