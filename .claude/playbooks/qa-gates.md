# Playbook — QA gates

Four gates, cheapest first. Each has a moment it runs and a thing it prevents. `python
tools/qa-submission.py` automates what can be automated; the rest is a checklist a human runs.

---

## Gate 1 — Integrity (runs on every eval run, automatic)

Prevents: a number that cannot be defended.

- `results.json` exists and covers **every** case in the manifest — no silent skips.
- `manifest.json` records the git commit and the benchmark freeze hash.
- The run's freeze hash **matches** `benchmark/MANIFEST.md`. A mismatch means the benchmark moved
  under the comparison; the run is void until explained.
- Wall-clock and cost are present and non-zero for every case.
- No file under `evidence/runs/<id>/` contains a credential pattern.

`tools/qa-submission.py --gate integrity` checks all of this.

## Gate 2 — Comparison fairness (runs before any claimed improvement)

Prevents: a headline number a judge can dismiss.

- Both arms ran the **same case ids**, from the **same freeze hash**.
- Both arms used the **same scorer code path** (one script, `--arm` flag).
- Same model family and same case text for both arms; any deliberate difference in resources is
  written down in `README.md`, not just known.
- The baseline is something a competent developer would plausibly do. Re-read
  `benchmark-independence.md` §"When the baseline looks too weak" and answer the question
  honestly.
- Regressions are reported, not netted out. Cases won and cases lost are both stated.

## Gate 3 — Reproducibility (runs Sunday, and again Monday morning)

Prevents: 15 points evaporating on a judge's laptop.

- **Clean clone into a fresh directory**, fresh virtualenv / `npm ci`, nothing from Raj's
  machine, no globally installed helper.
- Follow `REPRODUCTION.md` literally, typing only the commands it lists. If a step needs
  knowledge that is not on the page, the page is wrong — fix the page, not the run.
- Versions pinned and stated: Python, Node, model ids, key library versions.
- Runtime and approximate cost stated, and within ~30% of what the fresh run actually took.
- The main result reproduces. If it varies (LLM non-determinism), the README says the expected
  range and how many runs it is averaged over — silence here reads as a fluke.
- No network dependency beyond the model API. No credentials in the repo; the guide says which
  env vars to set.

Monday's run is on a *different machine or a container*, not just a different folder.

## Gate 4 — Finish (runs Sunday, before the video)

Prevents: losing the 20-point End-to-End Quality line.

- README answers all four questions — who has the problem, what the bottleneck is, does the
  agent solve it, can it be reproduced — in that order, near the top.
- Every number in the README traces to a `results.json`. Check three at random by hand.
- The improvement changelog is labelled as such, has a row per meaningful experiment, and
  includes at least one **removed** experiment.
- Main failure mode and the hot take are both present, and the hot take is a lesson, not a
  summary.
- Trajectories exist for **every** agent in the final workflow, scrubbed, readable end to end.
- Prose reads like Raj wrote it. No "unlock the power of", no filler triads, no section that
  exists only because a template had a slot. Read it aloud; anything you would not say, cut.
- Video is ≤5:00, covers baseline → one full execution → comparison → changelog → biggest
  contributor → one removed experiment.

---

## Running them

```
python tools/qa-submission.py            # all automatable checks
python tools/qa-submission.py --gate 3   # one gate
```

The script exits non-zero on failure and prints one line per check. It cannot judge prose or
fairness — Gates 2 and 4 are mostly human, and the script says so rather than passing silently.
