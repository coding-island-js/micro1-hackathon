# The PDF asks for ten or more cases — the brief's "three" is a Friday slice, not the target

Read from the official PDF, §"How to evaluate your solution", 2026-08-28.

Exact wording: *"Ten or more cases is a good target when the task allows it. Include one
challenging case and explain what it revealed."*

The ChatGPT handoff brief proposes ~3 cases. That is a reasonable **Friday validation slice** —
enough to learn whether the hypothesis survives — but shipping three on Monday leaves points on
the table under both Measured Improvement (15) and Reproducibility (15), and invites the
obvious objection that the sample is too small to support the headline number.

**How to apply:**
- Treat 3 as the Friday gate and **10+ as the Sunday requirement**, budgeted from the start:
  cases must be cheap enough to author that ten is affordable.
- One case must be deliberately hard, and the README must say what it revealed. That is an
  explicit rubric ask, not a nice-to-have.
- If the final benchmark is smaller than ten, the README states the reason in one sentence.
  Silence reads as an oversight.

Related: [[decision-freeze-before-baseline]] · [[reference-rubric-weights]]
