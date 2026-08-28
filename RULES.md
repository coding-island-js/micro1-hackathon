# Competition rules — micro1 Agentic Workflows Hackathon

**Source of truth.** Everything here is transcribed or tightly summarised from the official
brief PDF (`micro1 - First Hackathon97ce7c5.pdf`, 10 pages incl. appendix). Where this file and
a conversation disagree, **this file wins** — unless the organisers say otherwise in writing, in
which case update this file and date the change.

Deadline (from Raj, not stated in the PDF): **Monday 31 August 2026, 11:00 AM Pacific.**

---

## 1. The challenge, in the organisers' words

> Pick a specific and meaningful problem you understand. Use agents to solve it and show
> through clear evidence that your solution improves the way the task is handled today.

> Start by explaining who has the problem. Describe the bottleneck they face and why solving it
> would be valuable in practice. The goal is to create something a real person would want to use.

### The four questions to keep in mind
1. Who has this problem?
2. What bottleneck makes it worth solving?
3. Does the agent solve it well?
4. Can another person reproduce the result?

Every deliverable should visibly answer all four.

## 2. How agents can help

Use whichever agent capabilities fit. The PDF names these as options, not requirements: better
**context**, better **tools**, **memory** to carry information forward, **verification** to catch
errors before they reach the user, specialised **skills**, and **orchestration** across several
agents.

> Judges focus on whether each design choice improves the solution and helps the agent reach the
> goal reliably. **Purposeful choices matter more than the number of components.**

Read that last line as a warning: an unjustified agent costs points, it does not earn them.

## 3. Baseline — required

Create a **simple baseline** representing a reasonable basic way to handle the task today.
The PDF's own examples of an acceptable baseline:

- one direct prompt with basic instructions
- one general-purpose agent with basic tools
- a simple script or template
- the manual process people use today

Fairness rules:

- Baseline and final solution get **the same task and the same evaluation cases**.
- Any meaningful difference in the **resources** available to each must be explained.
- The final comparison shows the *size* of the improvement; the changelog explains *where it
  came from*. Both are required — they tell the story together.

## 4. Improvement changelog — required deliverable

A short changelog telling the story from baseline to final result. One entry per **important
experiment**, each stating:

- what you tried
- why you tried it
- the result, measured with the **same evaluation method** wherever possible
- what you decided next

> Include experiments you later removed and explain what they taught you about the problem.

Table shape given in the PDF: `STAGE | WHAT YOU TRIED AND WHY | EVIDENCE | DECISION / LEARNING`,
running Baseline → Iteration 1 → Iteration 2 → Iteration 3 → Final. Those stages are an example
only — replace them with the changes the project actually made.

## 5. Evaluation

- Choose **one primary metric** reflecting what success means to the user. Their examples: tests
  passing for a developer; time or cost saved for an ops team; calibration for forecasting.
- **Define what a good final result looks like before running the evaluation.**
- Same cases for baseline and final solution. **Share the complete results.**
- **Ten or more cases is a good target when the task allows it.**
- **Include one challenging case and explain what it revealed.**

Suggested table: rows `Primary outcome` / `Human time per task` / `Cost per task`; columns
`SIMPLE BASELINE | AGENT SOLUTION | CHANGE`.

> You run this evaluation yourself. If the format above fits your task poorly, design your own
> clear scoring rubric and propose it, so the judges can use it to assess your workflow.

## 6. Judging rubric — 100 points

| Criterion | Pts | What strong work looks like | Self-check question |
|---|---|---|---|
| Problem & User Value | 15 | A meaningful problem for a clearly defined user | Who experiences the bottleneck and why does solving it matter? |
| Agent Solution & Engineering | 30 | Agents used purposefully and technically sound; context / tools / memory / verification / skills / orchestration as the problem warrants | Which design choices helped the agent solve the problem? |
| End to End Quality | 20 | A realistic, **self-contained** execution producing a final result the user can use, "with the finish of something a person would sign their name to rather than an obvious AI generated draft" | Would the intended user consider this high quality, or does it read as clearly AI generated? |
| Measured Improvement | 15 | Gains over a fair baseline, changelog connecting each iteration to evidence | Which changes truly improved the outcome? |
| Reproducibility | 15 | A clear path for another person to run solution + baseline and reach the main result | Could they do it from a clean environment? |
| Hot Take / Insights | 5 | Turns an observed failure mode into a practical lesson for building more reliable agents | What did you learn and how would it change what you build next? |

**Engineering is 30 — the largest single block. End-to-end quality is 20 and is about finish,
not feature count.**

## 7. Ground rules (all ten)

1. You are welcome to build with tools and components you already know.
2. **Make it clear what existed before the competition and what you added.**
3. Use every tool and component according to its license and service terms.
4. **Keep consequential actions controlled through a sandbox or simulation. Add human approval
   before the action happens.**
5. Make a **qualified human reviewer** part of any solution that could significantly affect
   someone.
6. Choose a legal and ethical use case that treats people and their data responsibly.
7. Use information you are allowed to share. **Public or synthetic data** are usually the
   easiest options. Approved anonymous data also works.
8. **Keep credentials and private information outside the submission.**
9. **Connect every claim about your results to the evidence you submit.**
10. Give judges enough access to run the project and reproduce the main result.

## 8. Final deliverables — four items

1. **Complete solution code and improvement changelog.** The full project and everything needed
   to run it, *including the instructions that shape each agent*. The README introduces the
   intended user, their current bottleneck, and why solving it is valuable. Clearly labelled
   Improvement Changelog, one entry per meaningful iteration, each tied to the evidence that
   guided the next decision. **Close with the main failure mode and the hot take.**
2. **Reproduction guide.** Written for a clean environment. Setup plus the **exact commands** for
   solution, baseline and evaluation. Which data is required, what output to expect, relevant
   **versions**, approximate **runtime and cost**.
3. **Solution video, up to 5 minutes.** Problem and simple baseline → one realistic execution end
   to end → the final comparison → brief changelog walk-through → the change that contributed
   most → **one experiment you removed**.
4. **Agent trajectories.** Representative trajectories for **every agent used**. Easy to follow
   from the agent instructions to the final result: what the agent did, how its tools responded,
   the feedback that shaped its next step, and any **retries or human checkpoints**.

## 9. What the appendix examples teach

Three worked examples: repository quality valuation, candidate evaluation, podcast translation.
The pattern common to all three, worth copying:

- a named human decision that today depends on inconsistent judgement
- a **shared rubric** applied to both a human/simple baseline and the agent
- a fixed case set decided **before** running anything
- at least one deliberately hard case (the candidate with conflicting signals; the translation
  that depends on a recurring detail from an earlier episode)
- every score traced back to a file, test result, build output or source line
- a second person, from a clean environment, reaching the same result

## 10. House interpretations (ours, not the PDF's)

- The rubric rewards **evidence density** over architecture. A component that cannot show its own
  measured contribution is a liability under both "Agent Solution" and "Measured Improvement".
- Ground rule 2 means the repo's git history is part of the submission. Do not squash it.
- Ground rule 9 means: no number appears in the README that is not reproducible from a file in
  `evidence/`.
- "Ten or more cases" (§5) is a target the PDF states plainly. Any final benchmark smaller than
  ten needs a written reason in the README, not silence.
