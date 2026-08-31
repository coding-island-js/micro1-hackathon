---
name: decision-reverify-is-reporting-not-correctness
description: The re-verify step earns 0 points and is kept only for the readiness report; the "zero spread" stability claim is retired.
metadata:
  type: project
---

Settled 2026-08-30 by the ablation, `experiments/003-ablate-reverify.md`.

**Re-verify cannot affect the score.** It makes 0 `Write`/`Edit` and 0 `Bash` calls across all 9
case-runs of the solution arm, and it runs after the last code change. Verified by grepping the
`reverify.stream.jsonl` trajectories, not inferred from the prompt.

It costs **44% of wall clock and 31% of spend** (1105 s → 618 s, $2.014 → $1.384 per run) and
produces exactly one thing: the "still flagged after the repair pass" section of the readiness
report. **Kept as a reporting step. Describe it as one** — never as part of what earns the 14/18.

**"Zero spread" is retired. Do not say it.** Because re-verify is inert, `solution` and
`solution-no-reverify` are six samples of the same scoring pipeline: **12–15 of 18, 76.9% mean.**
The old "77.8% on all three runs, zero spread" was three lucky draws. Wording was corrected in
the deck, script and README on 30 Aug.

**The improvement survives untouched** — all six runs beat the baseline's flat 11/18, and the
baseline's own zero spread across 4 runs is real.

Two facts this corrects: `003::spaces_are_part_of_the_field` is no longer never-fixed (1 of 3
here), leaving `001::token_expires_within_ten_minutes` as the only one; and
`003::quoted_field_may_span_lines` is a new regression at 2 of 3.

Lesson for the write-up, and the better half of the hot take: **a repeated score is not a stable
score, and an unmeasured step is a claim rather than a component.** Related:
[[decision-no-pivot]], [[constraint-packaging-is-the-gap]].
