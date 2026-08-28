# micro1 Frontier Engineering Challenge 2026 — Project Brief

> **Provenance.** Drafted with ChatGPT on 2026-08-28 as a handoff to Claude Code. It is
> **context, not an implementation specification** — Claude Code is expected to disagree with it
> where the evidence warrants. The binding competition requirements live in `RULES.md`; where
> this brief and `RULES.md` conflict, `RULES.md` wins. Claude Code's response to this brief is
> in `docs/LEAD-ENGINEER-REVIEW.md`.

## Context

This is an individual entry for the micro1 Agentic Workflows / Frontier Engineering Challenge.

Competition deadline: Monday, August 31, 2026 at 11:00 AM Pacific.

This repository is purpose-built for the competition.

Do not incorporate proprietary code, private data, credentials, or code from unrelated existing
projects.

---

## Competition Objective

The challenge asks us to:

Choose a specific, meaningful problem that a real person experiences.

Use coding/AI agents to improve how that problem is handled.

Demonstrate through evidence that the final solution improves over a reasonable baseline.

The submission must be reproducible and clearly explain what was tried, what worked, what
failed, and what was learned.

This is not primarily a product/UI competition.

Correctness, engineering judgment, measurable improvement, reproducibility, and end-to-end
quality matter.

---

## Judging Rubric

100 points total:

- Agent Solution & Engineering: 30
- End-to-End Quality: 20
- Problem & User Value: 15
- Measured Improvement: 15
- Reproducibility: 15
- Hot Take / Insights: 5

Optimize for the total rubric, not architectural complexity.

A simpler architecture that produces stronger evidence is preferable to a complex architecture
that cannot justify its components.

---

## Current Project Hypothesis

We are exploring a Production Readiness Agent / workflow for developers using AI coding agents.

The underlying problem:

AI coding agents can produce implementations that look convincing and pass obvious tests while
still missing production requirements, hidden dependencies, boundary conditions, failure modes,
or other important invariants.

The intended user should be made more specific if doing so improves the strength of the project.

Current candidate: solo developers and small engineering teams using coding agents to ship
backend features quickly.

The bottleneck: a generated implementation may appear complete while still containing failures
that only emerge under realistic edge cases.

---

## Research Question

The current research question is approximately:

Can an agentic engineering workflow materially improve production correctness over a reasonable
single-pass coding-agent baseline?

Do not treat that wording as immutable. If inspection or experimentation suggests a
better-defined research question, propose it.

---

## Current Hypothesis

Separating implementation from adversarial verification and evidence-driven repair may
substantially improve correctness compared with a single-pass coding agent.

This is a hypothesis to TEST, not an assumption to encode into the project.

If the evidence contradicts it, surface that immediately.

---

## Baseline

We need a fair baseline representing a reasonable basic coding-agent workflow.

Current candidate: feature request + repository → coding agent → implementation. No deliberate
adversarial verification or repair cycle.

The exact baseline should be evaluated for fairness before implementation.

The baseline must not be intentionally weakened merely to make the advanced solution look
better.

---

## Evaluation

The primary metric should preferably be objective and reproducible.

Current candidate: hidden test pass rate.

Secondary metrics may include runtime, model/API cost, number of regressions, success rate by
failure category, and human intervention required.

Baseline and advanced approaches must be evaluated against the same cases.

Evaluation methodology should be decided before optimizing the advanced workflow.

---

## Benchmark Independence

This is extremely important.

We need evidence that the benchmark was not constructed or modified simply to favor the final
agent architecture.

Preferred ordering:

1. Define benchmark requirements.
2. Define hidden evaluation tests.
3. Commit/freeze them.
4. Establish the baseline.
5. Only then develop and tune the advanced approach.

Do not expose hidden evaluator tests to implementation agents.

Maintain Git history that makes the ordering auditable.

If there is a better method of ensuring benchmark independence, propose it.

---

## Initial Benchmark Scope

For Friday, we want a SMALL benchmark sufficient to determine whether the idea works. Target
approximately three cases initially.

Candidate cases discussed so far:

1. Password reset — token lifecycle and unusual user states.
2. Bulk CSV import — partial failures and transactional integrity.
3. Discount calculation — rounding, boundaries, and conflicting promotions.

These are candidates, not mandatory choices. Before implementing them, evaluate whether they are
sufficiently realistic, diverse, understandable to judges, and fair. Replace them if better cases
materially improve the experiment without increasing weekend scope.

---

## Advanced Solution

DO NOT assume a predetermined number of agents.

Previously discussed possible components: requirements analysis, implementation, adversarial
verification, repair, re-verification. Treat these as candidate capabilities, not required
architecture.

Design the smallest agentic workflow that you believe can produce a meaningful measured
improvement.

Every major component should ideally justify itself through evidence. If a component adds
complexity/cost without measurable value, remove it and record the experiment.

---

## Friday Goal

Friday is hypothesis-validation day. Do NOT attempt to finish the entire hackathon project today.

By the end of Friday we want:

1. A defensible baseline.
2. A small frozen benchmark.
3. Working trajectory/evidence logging.
4. At least one advanced approach.
5. Baseline vs advanced evaluation results.
6. Enough evidence to decide whether to continue, modify, simplify, or pivot.

The most important Friday output is an actual measured comparison, e.g. baseline hidden-test pass
rate X% vs advanced Y%.

Do not fabricate or target a desired value. Let the experiment tell us what happened.

---

## Saturday Goal

Assuming Friday validates the hypothesis: improve the workflow experimentally, evaluate
architectural additions individually where practical, expand the benchmark if useful,
investigate failures, track cost/runtime, maintain the improvement changelog, preserve
representative trajectories, and get the system essentially feature-complete.

Do not expand benchmark size merely to make the project look larger. Quality and credibility
matter more than raw case count.

---

## Sunday Goal

Sunday is primarily submission-production day. Freeze major architecture early enough to
complete: final evaluation, improvement changelog, README, reproduction guide, representative
agent trajectories, final results/evidence, and the five-minute-or-less solution video.

The video should be COMPLETED Sunday. Do not plan important feature development for Monday.

---

## Monday Goal

Monday morning is buffer only: clean-environment reproduction test, fix submission-blocking
problems, verify artifacts, upload, submit before deadline.

---

## Improvement Changelog

Maintain this DURING development rather than reconstructing it afterward. For every meaningful
experiment capture: hypothesis / problem observed; change attempted; reason for trying it;
evaluation result; cost/runtime change if relevant; decision (keep / modify / remove); lesson
learned.

Removed experiments are valuable evidence. Do not hide negative results.

---

## Agent Trajectories

Trajectory capture must exist from the beginning. For agents used inside the submitted solution,
preserve enough information to show: instructions, inputs/context, tool calls/actions, tool
responses, retries, verification feedback, human checkpoints, and the final result.

Keep credentials and private information out of trajectories.

---

## Reproducibility

A judge should be able to start from a clean environment and reproduce the important result.
Prefer minimal dependencies, pinned/reported versions, synthetic/public data, deterministic tests
where possible, simple setup, simple commands, no unnecessary infrastructure, and no undocumented
environment assumptions.

Eventually aim for a very small number of commands to reproduce baseline and advanced evaluation.

---

## Video Story

Do not optimize the implementation around flashy UI. The likely five-minute story is:

1. Who has the problem and why it matters.
2. Show the simple baseline.
3. Show the baseline apparently succeeding.
4. Reveal failures through independent evaluation.
5. Run one realistic advanced workflow end-to-end.
6. Show what verification discovers.
7. Show repair/re-verification.
8. Compare final baseline vs advanced results.
9. Explain the most valuable architectural change.
10. Explain one experiment we removed.
11. State the primary remaining failure mode.
12. Give our evidence-backed hot take.
13. Show how the project can be reproduced.

Exact content should follow the evidence we actually obtain.

---

## Important Principles

1. Do not optimize for looking sophisticated.
2. Do not assume our current architecture is correct.
3. Challenge the project concept if evidence warrants it.
4. Prefer measured engineering decisions over intuition.
5. Keep scope appropriate for a three-day competition.
6. Preserve evidence as work happens.
7. Never alter evaluation methodology merely to improve our reported score.
8. Keep baseline comparisons fair.
9. Optimize for a polished, reproducible submission.
10. Tell us when an idea is unnecessary or actively harmful.

---

## Your Role as Lead Engineering Agent

You are not merely implementing a specification. Act as the lead engineer for this competition
entry.

Before writing substantial code:

1. Read this entire brief.
2. Inspect the repository/environment.
3. Evaluate the proposed problem and experiment.
4. Identify the biggest risks or weaknesses.
5. Challenge assumptions where appropriate.
6. Recommend the smallest credible Friday experiment.
7. Propose an execution plan.
8. Identify anything we should decide before implementation.

You have authority to recommend changes to: benchmark cases, baseline design, agent
architecture, evaluation methodology, project structure, implementation approach.

But preserve the central competition constraints and document significant changes.

Do not expand scope without explaining why the additional work is likely to improve the
submission.

Once the plan is agreed, execute autonomously where reasonable and stop for human input when a
decision materially affects project direction, benchmark fairness, competition compliance, or
scope.
