# Next actions — micro1-hackathon

Read second, every session. A cold session starts from this file alone.

**Updated:** Sat 29 Aug, end of day · **Deadline: Mon 31 Aug, 11:00 AM Pacific.**

## Where we are

**Everything is done except the video.**

| Arm | n | Every run | Spread |
|---|---:|---|---:|
| Do nothing | — | 1/18 | — |
| One agent | 4 | 11/18 (61.1%) | 0.0 |
| **implement → verify → repair → re-verify** | 3 | 14/18 (77.8%) | 0.0 |
| Removed: evidence-gated repair | 3 | 64.8% mean | 16.6 |

Public repo: **github.com/coding-island-js/micro1-hackathon**
`python tools/qa-submission.py` → 48 ok, 0 failed. Self-score **82/100**.

## The only thing left

**Record the video.** Source is `ops/slides/deck.html` — 17 slides, opens in a browser, no
terminal, nothing to run. Raj scrolls it. Words on screen carry the detail; he narrates little
or nothing. Six required beats are all covered.

If time remains after recording: ablation of the re-verify step (n=3) buys ~3 on Engineering.
Not before the recording.

## Facts not to re-derive

- **The 14/18 total is stable; the behaviour is not.** Only 2 repairs happen every run. 4
  assertions flip and cancel out. The regression `002::failed_results_are_replayed_not_retried`
  appears in 2 of 3 runs, not all three.
- Never fixed by any arm: `001::token_expires_within_ten_minutes`,
  `003::spaces_are_part_of_the_field`. Case 003 does not move at all.
- **Five other domains were tested for a pivot and all five passed** — accessibility twice,
  allergens, pickleball, side pots. Do not test a sixth. It is a changelog row now.
- Real spend is **$0**. The $13.87 is API-rate equivalent on a subscription.

## Standing risks

- The video is the only incompressible item and the only line that can still move.
- Three cases against a suggested ten is disclosed in the README with the reason.
