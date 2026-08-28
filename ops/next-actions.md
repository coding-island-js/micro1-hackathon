# Next actions — micro1-hackathon

Read second, every session. A cold session starts from this file alone.

**Updated:** 2026-08-28 · **Deadline: Mon 31 Aug, 11:00 AM Pacific.**

## Where we are

Scaffold built. Rules captured from the PDF. **Four of six blocking decisions called by Raj.**
Three Friday cases proposed with every invariant traced to an external spec —
`docs/BENCHMARK-CASE-PROPOSAL.md`, **awaiting approval before implementation.**

Nothing measured. No case files, no harness, no runs.

## Settled (details in `REQUIREMENTS.md` §Decided)

- **Case requirements come from public specs we did not write** — ASVS v4.0.3 · Stripe
  idempotency docs · RFC 4180. All three verified verbatim today.
- **Output = repaired code + a lean readiness report.** Not a product feature.
- **Same model both arms.** Workflow is the only independent variable.
- **$0 incremental spend, $10 hard ceiling.** Both arms run `claude -p` headless; verified it
  returns `total_cost_usd`, `duration_ms`, `num_turns` and the full tool stream per run.

## ⛔ Blocked on Raj — two decisions

1. **Approve the three cases** in `docs/BENCHMARK-CASE-PROPOSAL.md` (001 password reset ·
   002 idempotency, the hard case · 003 CSV import), plus the two calls inside it: **Python 3 +
   pytest**, and the readiness-report shape.
2. **The two remaining decisions in `REQUIREMENTS.md` §Open** — who exactly the user is, and
   whether the final workflow keeps a human checkpoint.

## Friday, in order, once approved

| # | Step | Est. |
|---|---|---|
| 1 | Pin version-locked source URLs | 0h20 |
| 2 | Shared stub + pytest layout, reused by all three cases | 0h45 |
| 3 | Case 001 · 002 · 003 — ticket, stub, hidden tests | 3h00 |
| 4 | **Freeze commit** — cases + hidden tests, nothing else. Hash into `benchmark/MANIFEST.md` | 0h05 |
| 5 | `eval/` — one scorer, `--arm`, writes `evidence/runs/<id>/` | 1h15 |
| 6 | Baseline run, commit evidence | — |
| 7 | Advanced arm: implement → verify → repair → re-verify. One loop | 1h15 |
| 8 | **Write the comparison down**, whatever it says | 0h20 |

**~7h with no slack.** If it slips: freeze **two** cases Friday and add 003 as a second frozen
block Saturday — `playbooks/benchmark-independence.md` covers post-freeze blocks, results get
reported both ways. Do not cut step 5 or the evidence capture; that is what the rubric buys.

Step 8 is Friday's deliverable. Not a working system — a number.

## Standing risks

- **The video is not compressible.** Recorded Sunday.
- **Steps 1-4 happen before any solution code exists**, not roughly around then.
- If Friday's comparison shows no real gap, Saturday changes the experiment rather than tuning a
  workflow that is not moving the number.
- 10+ cases is the Sunday target. The case format has to stay cheap enough that it is reachable.

## Housekeeping

- `git init`ed, **nothing committed yet** — awaiting go-ahead. First commit should land before
  any benchmark work so the freeze ordering is clean from the start.
- No GitHub remote. Judges need access (ground rule 10) before Sunday; public vs
  private-with-access is Raj's call.
