# Requirements — micro1-hackathon

What we are building, what is settled, and what is still open. Precedence: `RULES.md` (the
competition PDF) → this file → `HACKATHON_BRIEF.md`.

**Status 2026-08-28: all decisions called. Friday experiment approved and under way.**

---

## 1. The problem

**The user: a solo founder who uses coding agents to build and ship backend features without
another engineer routinely reviewing each change.**

They get implementations that *look* finished. They read well, they
pass the obvious tests, and they ship — and then they fail on the cases nobody wrote a test for:
token lifecycles, partial failures, boundary conditions, conflicting rules.

The bottleneck is not writing the code. It is **deciding whether code that appears finished is
safe enough to move toward production** - and there is no second engineer to ask. Answering it
by hand costs a careful read of every diff, which is exactly the work the agent was supposed to
remove.

## 2. Research question

Can an agentic workflow that separates implementation from adversarial verification and
evidence-driven repair materially improve production correctness over a reasonable single-pass
coding-agent baseline?

This is a hypothesis to **test**. If Friday's evidence contradicts it, that is a result — write
it up and change the experiment rather than tuning toward a wanted answer.

## 3. Success criteria

**Primary metric:** hidden-test pass rate on a frozen benchmark, same cases both arms.

**Secondary:** wall-clock per case, API cost per case, regressions introduced, pass rate by
failure category, human interventions required.

Per `RULES.md` §5, define what a good final result looks like **before** running the evaluation.
Written down here, before the first run:

- A result worth submitting is a **clear, consistent gap** on the primary metric across the whole
  case set — not one case flipping.
- A gap that only appears on one or two cases is noise at this sample size and must be reported
  as such.
- No improvement, honestly reported and diagnosed, is still a submission. A fabricated or
  cherry-picked improvement is not.

## 4. Scope — in

- A frozen benchmark: visible case requirements + hidden evaluator tests. **10+ cases** is the
  target (`RULES.md` §5), including one deliberately hard case.
- A fair baseline: a reasonable single-pass coding-agent workflow.
- The advanced workflow: the **smallest** agentic design that could plausibly move the number.
- One evaluation harness, one scorer, both arms, `--arm` flag.
- Evidence capture from run one: results, timings, costs, trajectories.
- The four deliverables in `ops/deliverables.md`.

## 5. Scope — out

No UI. No deployment. No accounts, auth, payments or database. No Netlify, no Stripe, no
`AutomationTools`. No framework the judge would have to install for the sake of it. Nothing from
another Raj project, nothing from the micro1 contract repo.

## 6. Constraints

- **Three days.** Fri validate · Sat improve · Sun produce · Mon buffer.
- Minimal, pinned dependencies. A judge runs this from a clean clone.
- Public or synthetic data only (ground rule 7). Credentials from the environment (ground rule 8).
- Consequential actions sandboxed or simulated, with human approval (ground rule 4).
- Benchmark frozen before the baseline runs; hidden tests never reach an implementation agent.
- Every claim tied to a file in `evidence/`.

---

## Decided — 2026-08-28

- **Case requirements come from public specs we did not write.** ASVS v4.0.3 · Stripe idempotency
  docs · RFC 4180. Sourcing timeboxed 60–90 min; prefer authoritative specs, security guidance and
  API docs over trawling repos. We author the harness and the tests, never the definition of
  correct. → `.claude/memory/decision-external-case-sources.md`,
  `docs/BENCHMARK-CASE-PROPOSAL.md`
- **Output = repaired implementation + a lean, evidence-backed readiness report.** One page per
  case: invariant, verdict, evidence, what was repaired, what is still unproven. Report generation
  must not become a product feature; the measured claim stays hidden-test pass rate.
- **Same model both arms. Workflow is the only independent variable.** Tooling never differs
  between baseline and advanced.
- **$0 incremental spend, $10 hard ceiling without asking.** Both arms run `claude -p` headless on
  the existing subscription; it returns wall-clock, turns, token usage and equivalent API cost per
  run, plus the full tool stream for trajectories. No `ANTHROPIC_API_KEY` needed.
  → `.claude/memory/decision-zero-spend-via-cli.md`
- **Three cases Friday.** The validation gate. **10+ is a target, not a requirement** - six
  credible externally sourced cases with strong evidence beat ten rushed ones.
- **The user is a solo founder with no second reviewer**, and **human control sits at the final
  acceptance decision only** - no approval gate inside the verify/repair loop, because nothing
  in the benchmark acts outside a sandbox.
  -> `.claude/memory/decision-user-and-human-control.md`
- **Stop after the three Friday cases** and report baseline vs advanced, runtime and
  cost-equivalent, failures by case, and a recommendation on whether the hypothesis held,
  before expanding the benchmark.

## How decisions get recorded

Every decision from here gets a line under **Decided** above and, if it should never be
relitigated, a file in `.claude/memory/` plus a line in `.claude/MEMORY.md`.
