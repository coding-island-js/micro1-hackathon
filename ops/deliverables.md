# Deliverables tracker — the four required artifacts

Line-by-line requirements live in `.claude/playbooks/submission-checklist.md`. This file is
just: what state is each one in, and what is blocking it.

**Updated:** Fri 28 Aug, end of day

| # | Deliverable | File(s) | State | Blocked on |
|---|---|---|---|---|
| 1 | Solution code + improvement changelog | `solution/`, `eval/`, `README.md`, `CHANGELOG-IMPROVEMENT.md` | **code + changelog DONE** (4 rows, 1 removed experiment, failure mode + hot take written). **README still placeholders** | nothing — write it |
| 2 | Reproduction guide | `REPRODUCTION.md` | **skeleton** — the single biggest gap, 3/15 | nothing — write it, then run it on a clean clone |
| 3 | Solution video ≤5:00 | not started | **not started** | script Saturday, record Sunday. All numbers already exist |
| 4 | Agent trajectories | `trajectories/` | **still empty** — but 84 raw streams captured in `evidence/runs/*/cases/*/*.stream.jsonl` | nothing — render a readable subset |

## State — Sun 30 Aug

1. **Code + changelog** — done. Seven rows including the removed iteration, the assertion-level
   audit, the domain search and the 30 Aug accuracy audit.
2. **Reproduction guide** — done, executed on a clean clone; it found four real defects.
3. **Video** — **NOT RECORDED, the only thing left.** `ops/slides/deck.html`, 16 slides;
   `ops/video-script.md` keyed slide by slide, 4:29 at speaking pace.
4. **Trajectories** — done. 13 files, all four agents plus the removed iteration, with an index.

## Notes that still bite

**1 —** *"Include the instructions that shape each agent."* System prompts are part of the
submission. They live in `solution/prompts/`, never inline in a function.

**2 —** Versions, runtime and cost are explicitly required, and must come from a real run on a
clean environment, not an estimate.

**3 —** The one item that cannot be compressed on Monday morning. Numbers must be final before
recording — they were re-derived and five were corrected on 30 Aug.

**4 —** "Every agent you used" includes the ones that only verify or repair. Pick trajectories
where something happens: a caught defect, a retry, a checkpoint. Scrub before commit.
