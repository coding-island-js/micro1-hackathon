# Memory index — micro1-hackathon

One fact per file. **Open the one file you need, not the directory.**

## Decisions — settled, do not relitigate
- [freeze-before-baseline](memory/decision-freeze-before-baseline.md) — cases and hidden tests
  are committed **before** the baseline runs; the commit order is the proof
- [evidence-is-tracked](memory/decision-evidence-is-tracked.md) — `evidence/` and
  `trajectories/` are **git-tracked here**, unlike the contract repo
- [rules-md-is-canon](memory/decision-rules-md-is-canon.md) — precedence is
  RULES → REQUIREMENTS → BRIEF; the PDF wins
- [external-case-sources](memory/decision-external-case-sources.md) — requirements come from
  **public specs we did not write**; ASVS · Stripe idempotency · RFC 4180
- [user-and-human-control](memory/decision-user-and-human-control.md) - the user is a **solo
  founder with no second reviewer**; human control sits at **final acceptance only**
- [zero-spend-via-cli](memory/decision-zero-spend-via-cli.md) — both arms run `claude -p`;
  **$0 incremental, $10 hard ceiling**, and it meters cost/time/trajectories for free

## Constraints — how the competition actually behaves
- [ten-case-target](memory/constraint-ten-case-target.md) — the PDF asks for **10+ cases**;
  the brief's three is a Friday slice, not the target
- [block1-is-a-dev-set](memory/constraint-block1-is-a-dev-set.md) - iterations were designed
  using block 1's hidden results, so **001-003 are development cases**; the headline claim
  needs a freshly frozen **holdout** block
- [two-micro1-repos](memory/constraint-two-micro1-repos.md) — hackathon vs contract repo have
  **opposite rules**; never carry a habit across

## Reference
- [rubric-weights](memory/reference-rubric-weights.md) — **50 of 100 points are engineering
  (30) + finish (20)**; Hot Take is 5 points for one paragraph
- [deadline-schedule](memory/reference-deadline-schedule.md) — **Mon 31 Aug, 11:00 PT**;
  Fri validate · Sat improve · Sun produce · Mon buffer
