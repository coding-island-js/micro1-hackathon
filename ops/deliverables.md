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

## Notes per deliverable

**1 —** The easiest requirement to miss is *"include the code as well as the instructions that
shape each agent"*. System prompts and role text are part of the submission, not an
implementation detail. Keep them in files under `solution/`, never inline in a string buried in
a function.

**2 —** Cannot be written honestly from this machine. It gets *drafted* as the code lands and
*proved* by running it on a clean environment. Versions, runtime and approximate cost are
explicitly required, so capture them from the real run rather than estimating.

**3 —** The only item that cannot be compressed on Monday morning. Thirteen beats in five
minutes is roughly twenty seconds each — it needs a script and one or two takes, and the final
numbers must exist before recording. Do not schedule feature work that lands Sunday night.

**4 —** "Every agent you used" means every agent in the final workflow, including any that only
verifies or repairs. Choose trajectories that show something happening: a caught defect, a
retry, a human checkpoint. Scrub before commit.


## State, end of Sat 29 Aug

1. **Code + changelog** — done. Changelog carries five rows including the removed iteration, the
   assertion-level audit and the domain search.
2. **Reproduction guide** — done and executed on a clean clone; it found four real defects.
3. **Video** — NOT RECORDED. Source deck: `ops/slides/deck.html`, 18 slides; script keyed to
   them in `ops/video-script.md`, measured at 4:35. The only thing left.
4. **Trajectories** — done. 13 files, all four agents plus the removed iteration, with an index.
