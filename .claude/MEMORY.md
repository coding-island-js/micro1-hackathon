# Memory index — micro1-hackathon

One fact per file. **Open the one file you need, not the directory.**

## Decisions — settled, do not relitigate
- [no-pivot](memory/decision-no-pivot.md) — **fantasy and ShortCheck both evaluated and
  rejected**; the answer stays no unless the deadline moves
- [freeze-before-baseline](memory/decision-freeze-before-baseline.md) — cases and hidden tests
  committed **before** the baseline runs; commit order is the proof
- [external-case-sources](memory/decision-external-case-sources.md) — requirements come from
  **public specs we did not write**: ASVS · Stripe · RFC 4180
- [zero-spend-via-cli](memory/decision-zero-spend-via-cli.md) — both arms run `claude -p`;
  **$0 actual spend**, and it meters cost/time/trajectories for free
- [user-and-human-control](memory/decision-user-and-human-control.md) — the user is a **solo
  founder with no second reviewer**; human control sits at **final acceptance only**
- [evidence-is-tracked](memory/decision-evidence-is-tracked.md) — `evidence/` and
  `trajectories/` are **git-tracked here**, unlike the contract repo
- [rules-md-is-canon](memory/decision-rules-md-is-canon.md) — precedence RULES → REQUIREMENTS →
  BRIEF; the PDF wins

## Constraints — how this competition actually behaves
- [packaging-is-the-gap](memory/constraint-packaging-is-the-gap.md) — **the experiment is done;
  every remaining point is presentation.** Reproducibility is 3/15 and cannot be fixed late
- [block1-is-a-dev-set](memory/constraint-block1-is-a-dev-set.md) — iterations were designed
  using block 1's hidden results, so **001-003 are development cases**
- [ten-case-target](memory/constraint-ten-case-target.md) — the PDF asks for 10+ cases; six
  credible ones beat ten rushed
- [two-micro1-repos](memory/constraint-two-micro1-repos.md) — hackathon vs contract repo have
  **opposite rules**; never carry a habit across

## Reference
- [rubric-weights](memory/reference-rubric-weights.md) — **50 of 100 are engineering (30) +
  finish (20)**; Hot Take is 5 points for one paragraph
- [deadline-schedule](memory/reference-deadline-schedule.md) — **Mon 31 Aug, 11:00 PT**
