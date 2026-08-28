# NNN — <slug>

**Opened:** YYYY-MM-DD HH:MM · **Status:** open / kept / revised / removed / abandoned

## Observation that provoked this
What was seen, in which run, on which cases. A hypothesis with no observation behind it is a
guess — go diagnose first.

## Hypothesis
"Doing X will improve Y because Z." Written **before** the change.

## The change
Exactly one thing. Files touched, prompt diffs, config. If this section lists two changes,
neither result is attributable — split it.

## Run
- Run id:
- Arm:
- Cases: (must be the frozen set, same as the baseline)
- Freeze hash:
- Model / temperature:

## Result
| | Before | After | Δ |
|---|---|---|---|
| Primary metric (hidden-test pass rate) | | | |
| Cases won | | | |
| **Cases regressed** | | | |
| Wall-clock per case | | | |
| Cost per case | | | |

Per-case notes, especially anything that got worse.

## Decision
`kept` / `revised` / `removed` — and why. If the number did not move, remove the change; an
unjustified component costs points under Agent Solution & Engineering.

## Lesson
One or two sentences. This is the raw material for the hot take, so write the thing you actually
learned about the problem, not a summary of what happened.

## Changelog row written?
- [ ] Row added to `CHANGELOG-IMPROVEMENT.md`
- [ ] Trajectory captured if this run is representative
