# Next actions — micro1-hackathon

Read second, every session. A cold session starts from this file alone.

**Updated:** Sat 29 Aug, midday · **Deadline: Mon 31 Aug, 11:00 AM Pacific.**

## Where we are

**Three of the four deliverables are done. What is left is the video and a GitHub remote.**

| Arm | n | Total, every run | Spread in total |
|---|---:|---|---:|
| Untouched starting code | — | 1/18 (5.6%) | — |
| Baseline, single pass | 4 | 11/18 — **61.1%** | 0.0 |
| **Final: implement → verify → repair → re-verify** | 3 | 14/18 — **77.8%** | 0.0 |
| Removed: evidence-gated repair | 3 | 64.8% mean | 16.6 |

`python tools/qa-submission.py` → **48 ok, 0 failed, 8 for a human.**

## Saturday, done

1. **`REPRODUCTION.md` written and executed on a clean clone.** It found four real defects, all
   fixed, all named in the guide itself. Judges can sanity-check one case for $0.10 / 40 s.
2. **`evidence/` is now actually in git.** A bare `runs/` line in `.gitignore` applies at any
   depth and had excluded all ten runs. A judge would have cloned an empty evidence directory.
   263 files, 8.2 MB, committed. The same stale assumption meant the credential scan had never
   looked at evidence either — scan coverage went 0 → 253 files.
3. **`trajectories/` populated** — 13 files via `tools/export-trajectories.py`, covering all four
   agents, the baseline's single agent, and the removed iteration. Plus an index README.
4. **`README.md` written** — opens on the double-charge story with the solo-founder user.

## Left to do

| # | Task | Notes |
|---|---|---|
| 1 | **Video, ≤5 min** | Only incompressible item. Six required beats in `playbooks/submission-checklist.md`. Lead with the double charge. |
| 2 | **GitHub remote** | Ground rule 10 — judges need access. Public vs private-with-access is Raj's call. Still no remote. |
| 3 | Walk the 8 human QA checks | `python tools/qa-submission.py`, gates 2 and 4 |
| 4 | *Optional:* ablation — drop re-verify, n=3 | Buys Engineering. Only if 1–3 are done. |

## Corrected facts — do not repeat the old versions

An assertion-level diff across every run replaced two claims we had been repeating:

- ~~"gains 4 and loses 1 every run"~~ → **only true of the first run pair.** Across the three
  solution runs the workflow gains 3–4 and loses 0–1, varying by run.
- ~~"`001::reset_requests_are_rate_limited` is never fixed"~~ → **it is fixed in 2 of 3 runs.**

**The real finding, and it is a good one:** the total is stable at 14/18 but the composition is
not. Only **2** assertions are fixed reliably (`002::keys_expire_after_a_day`,
`002::same_key_with_different_params_is_an_error`). **4 flip run to run** and happen to cancel
out to the same score. The regression `002::failed_results_are_replayed_not_retried` appears in
**2 of 3** runs. Genuinely never fixed by any arm: `001::token_expires_within_ten_minutes` and
`003::spaces_are_part_of_the_field`. Case 003 does not move at all.

This is now a changelog row and the second half of the hot take: **a repeatable score is not
repeatable behaviour.**

## Also settled Saturday

**Accessibility was evaluated as a pivot and rejected on evidence.** Two spike runs
(`experiments/spike-a11y/`): a static checkout and an interactive booking page with a modal, a
fake dropdown and live-updating totals. A single plain pass did near-expert work both times —
correct focus trap, real buttons, native `<select>`, contrast ratios accurate to two decimals
when checked independently. **No baseline failure means no gap to measure.** ~2 h, $0.76
equivalent. Do not reopen; see `memory/decision-no-pivot.md`, which now has a third entry.

## Standing risks

- **The video is not compressible.** Sunday, from numbers that already exist.
- Adding cases or architecture now scores less than finishing the video.
- `$13.87` is *equivalent* API cost; actual paid usage is **$0**.
- Three cases against a suggested ten is a real limitation. It is disclosed in the README with
  the reason (repetition bought over breadth) rather than hidden.
