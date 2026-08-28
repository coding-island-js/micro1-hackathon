# Block 1 is a development set. The headline claim needs a holdout.

Recognised 2026-08-28, prompted by ChatGPT's guardrail during iteration 2.

**Reporting hidden results is required. Designing against them is contamination.** The line is
crossed the moment a design decision is informed by which hidden assertions failed.

**We have already crossed it.** Iteration 2's evidence gate was designed after seeing that
`002::failed_results_are_replayed_not_retried` regressed — hidden-test information. The gate is
structural (it never tells an agent to cache 500s), which limits the damage, but the motivation
came from the exam. Cases 001-003 are therefore **development cases**, and a number measured on
them is a development number.

**How to apply:**
- Any further design change informed by block 1's hidden results keeps block 1 as dev.
- The next benchmark block is a **holdout**: newly sourced, frozen **before** the iteration it
  will judge is designed, and never inspected until that iteration is finished.
- Report dev and holdout results **separately**. A single blended number hides which is which.
- Expanding the benchmark is now worth doing for this reason, not for case count. That reframes
  [[constraint-ten-case-target]]: the cases still to come should be holdout, not more of the same.
- The README must say plainly that 001-003 were used to develop the workflow. Unstated, it is the
  strongest available attack on the result; stated, it is evidence of rigour.

Related: [[decision-freeze-before-baseline]] · [[decision-external-case-sources]]
