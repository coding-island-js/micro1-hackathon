# Deliverables tracker — the four required artifacts

Line-by-line requirements live in `.claude/playbooks/submission-checklist.md`. This file is
just: what state is each one in, and what is blocking it.

**Updated:** Mon 31 Aug, morning

| # | Deliverable | File(s) | State | Blocked on |
|---|---|---|---|---|
| 1 | Solution code + improvement changelog | `solution/`, `eval/`, `README.md`, `CHANGELOG-IMPROVEMENT.md` | **DONE** — 8 rows, 1 removed experiment, 1 ablation, failure mode + hot take, README written | nothing |
| 2 | Reproduction guide | `REPRODUCTION.md` | **DONE** — executed on a clean clone, found four real defects | nothing; only a *different machine* would take it past 13/15 |
| 3 | Solution video ≤5:00 | `video/solution-video.mp4` (+ `.srt`, transcript) | **DONE** — 4:47, six beats verified, captions corrected | nothing |
| 4 | Agent trajectories | `trajectories/` | **DONE** — 14 files, all four agents plus the removed iteration, with an index | nothing |

## State — Sun 30 Aug evening

1. **Code + changelog** — done. Eight rows: the removed iteration, the assertion-level audit, the
   domain search, the 30 Aug accuracy audit, and the re-verify ablation.
2. **Reproduction guide** — done, executed on a clean clone; it found four real defects.
3. **Video** — **done.** Recorded Sun 30 Aug at 5:18.8, cut to **4:47** on Mon 31 Aug by
   removing 31.6s of dead air only: no re-record, no words dropped except one inaccurate clause
   (see below). All six required beats verified against the transcript. Post-production notes and
   verification in `ops/video/`.
4. **Trajectories** — done. 14 files, all four agents plus the removed iteration, with an index.

## Notes that still bite

**1 —** *"Include the instructions that shape each agent."* System prompts are part of the
submission. They live in `solution/prompts/`, never inline in a function.

**2 —** Versions, runtime and cost are explicitly required, and must come from a real run on a
clean environment, not an estimate.

**3 —** The one item that cannot be compressed on Monday morning. Numbers must be final before
recording — they were re-derived and five were corrected on 30 Aug.

**4 —** "Every agent you used" includes the ones that only verify or repair. Pick trajectories
where something happens: a caught defect, a retry, a checkpoint. Scrub before commit.
