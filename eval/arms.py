"""The two arms.

Both start from the same frozen case, the same workspace copy, the same model, the same
tools and the same implement prompt. The only difference is what happens after the first
implementation: the baseline stops, the solution verifies, repairs and re-verifies.
"""
from __future__ import annotations

import json
import os

from . import cc, score
from solution import gate

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

IMPLEMENT_PROMPT = os.path.join(REPO_ROOT, "eval", "prompts", "implement.md")
VERIFY_PROMPT = os.path.join(REPO_ROOT, "solution", "prompts", "verify.md")
VERIFY_GATED_PROMPT = os.path.join(REPO_ROOT, "solution", "prompts", "verify-gated.md")
REPAIR_PROMPT = os.path.join(REPO_ROOT, "solution", "prompts", "repair.md")


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def _task(ticket: str) -> str:
    return "Here is the ticket.\n\n---\n\n" + ticket + "\n\n---\n\nImplement it."


def run_baseline(ticket: str, workspace: str, model: str) -> dict:
    """A reasonable single-pass coding-agent workflow: ticket in, implementation out."""
    call = cc.run_agent(
        step="implement",
        prompt=_task(ticket),
        system_prompt=_read(IMPLEMENT_PROMPT),
        cwd=workspace,
        model=model,
    )
    return {"calls": [call], "findings_initial": None, "findings_final": None}


def _verify(ticket: str, workspace: str, model: str, step: str, prompt_path: str = None) -> tuple:
    call = cc.run_agent(
        step=step,
        prompt=(
            "Here is the ticket the implementation was written from.\n\n---\n\n"
            + ticket
            + "\n\n---\n\nReview the implementation in this directory and report your findings "
            "as the JSON object described in your instructions."
        ),
        system_prompt=_read(prompt_path or VERIFY_PROMPT),
        cwd=workspace,
        model=model,
    )
    parsed = cc.extract_json(call.result)
    if parsed is None or not isinstance(parsed.get("findings"), list):
        # A verifier whose output cannot be parsed has not said "no problems" -- it has
        # failed. Record that honestly rather than scoring it as a clean review.
        return call, None
    return call, parsed["findings"]


def run_solution(ticket: str, workspace: str, model: str) -> dict:
    """implement -> adversarially verify -> repair -> re-verify.

    One loop. No human gate inside it: nothing here acts outside the sandbox, so the
    developer's decision point is at the end, on the finished patch and report.
    """
    calls = []

    implement = cc.run_agent(
        step="implement",
        prompt=_task(ticket),
        system_prompt=_read(IMPLEMENT_PROMPT),
        cwd=workspace,
        model=model,
    )
    calls.append(implement)

    verify_call, findings = _verify(ticket, workspace, model, "verify")
    calls.append(verify_call)

    if findings:
        repair = cc.run_agent(
            step="repair",
            prompt=(
                "Here is the ticket.\n\n---\n\n" + ticket + "\n\n---\n\n"
                "Fix the findings in your instructions."
            ),
            system_prompt=_read(REPAIR_PROMPT).replace(
                "{{FINDINGS}}", json.dumps(findings, indent=2)
            ),
            cwd=workspace,
            model=model,
        )
        calls.append(repair)

        reverify_call, findings_after = _verify(ticket, workspace, model, "reverify")
        calls.append(reverify_call)
    else:
        findings_after = findings

    return {
        "calls": calls,
        "findings_initial": findings,
        "findings_final": findings_after,
    }


def run_solution_no_reverify(ticket: str, workspace: str, model: str) -> dict:
    """ABLATION of run_solution: implement -> verify -> repair, and stop.

    Identical to run_solution in every other respect -- same prompts, same model, same
    frozen cases -- so the difference between the two arms is the re-verify step and
    nothing else. The point is to measure that step rather than assert it earns its place.

    Note what this can show. Re-verification runs *after* the last intended code change,
    so on the design as written it should not move the hidden-test score at all: it only
    feeds the readiness report. If the score does move, the reviewer is editing code it
    was asked only to read -- which is worth knowing either way.
    """
    calls = []

    implement = cc.run_agent(
        step="implement",
        prompt=_task(ticket),
        system_prompt=_read(IMPLEMENT_PROMPT),
        cwd=workspace,
        model=model,
    )
    calls.append(implement)

    verify_call, findings = _verify(ticket, workspace, model, "verify")
    calls.append(verify_call)

    if findings:
        repair = cc.run_agent(
            step="repair",
            prompt=(
                "Here is the ticket.\n\n---\n\n" + ticket + "\n\n---\n\n"
                "Fix the findings in your instructions."
            ),
            system_prompt=_read(REPAIR_PROMPT).replace(
                "{{FINDINGS}}", json.dumps(findings, indent=2)
            ),
            cwd=workspace,
            model=model,
        )
        calls.append(repair)

    return {
        "calls": calls,
        "findings_initial": findings,
        # No second review happened, so there is no "still flagged after repair" state.
        # None here means absent, not unparseable -- the flag below keeps the report honest.
        "findings_final": None,
        "reverify_skipped": True,
    }


def _visible_passed(workspace: str) -> int:
    out, _ = score._run_pytest("tests", cwd=workspace)
    return score._parse(out)["passed"]


def run_solution_gated(ticket: str, workspace: str, model: str) -> dict:
    """implement -> verify -> EVIDENCE GATE -> repair -> regression check -> re-verify.

    Iteration 1 let a confident-but-wrong finding reach the repair step and it broke working
    behaviour. Here a finding may authorise a code change only if its own reproduction fails
    against the current code and it does not contradict a PROVIDED contract. Everything else
    is reported to the developer instead.
    """
    calls = []

    implement = cc.run_agent(
        step="implement",
        prompt=_task(ticket),
        system_prompt=_read(IMPLEMENT_PROMPT),
        cwd=workspace,
        model=model,
    )
    calls.append(implement)

    verify_call, findings = _verify(ticket, workspace, model, "verify", VERIFY_GATED_PROMPT)
    calls.append(verify_call)

    gated = gate.apply(findings or [], workspace)
    demonstrated, advisory = gated["demonstrated"], gated["advisory"]
    reverted = False

    findings_after = findings
    if demonstrated:
        before = _visible_passed(workspace)
        snap = gate.snapshot(workspace)

        repair = cc.run_agent(
            step="repair",
            prompt=(
                "Here is the ticket.\n\n---\n\n" + ticket + "\n\n---\n\n"
                "Fix the findings in your instructions. Each one comes with a reproduction "
                "that currently fails; make it pass without breaking anything else."
            ),
            system_prompt=_read(REPAIR_PROMPT).replace(
                "{{FINDINGS}}", json.dumps(demonstrated, indent=2)
            ),
            cwd=workspace,
            model=model,
        )
        calls.append(repair)

        # Regression gate: a repair that costs a test the ticket shipped with is not a repair.
        if _visible_passed(workspace) < before:
            gate.restore(snap, workspace)
            reverted = True

        reverify_call, findings_after = _verify(
            ticket, workspace, model, "reverify", VERIFY_GATED_PROMPT
        )
        calls.append(reverify_call)

    return {
        "calls": calls,
        "findings_initial": findings,
        "findings_final": findings_after,
        "gate": {
            "demonstrated": len(demonstrated),
            "advisory": len(advisory),
            "advisory_reasons": [f.get("gate", "") for f in advisory],
            "repair_reverted": reverted,
        },
        "advisory_findings": advisory,
    }


ARMS = {
    "baseline": run_baseline,
    "solution": run_solution,
    "solution-gated": run_solution_gated,
    "solution-no-reverify": run_solution_no_reverify,
}
