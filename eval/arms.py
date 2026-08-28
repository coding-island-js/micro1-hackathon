"""The two arms.

Both start from the same frozen case, the same workspace copy, the same model, the same
tools and the same implement prompt. The only difference is what happens after the first
implementation: the baseline stops, the solution verifies, repairs and re-verifies.
"""
from __future__ import annotations

import json
import os

from . import cc

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

IMPLEMENT_PROMPT = os.path.join(REPO_ROOT, "eval", "prompts", "implement.md")
VERIFY_PROMPT = os.path.join(REPO_ROOT, "solution", "prompts", "verify.md")
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


def _verify(ticket: str, workspace: str, model: str, step: str) -> tuple:
    call = cc.run_agent(
        step=step,
        prompt=(
            "Here is the ticket the implementation was written from.\n\n---\n\n"
            + ticket
            + "\n\n---\n\nReview the implementation in this directory and report your findings "
            "as the JSON object described in your instructions."
        ),
        system_prompt=_read(VERIFY_PROMPT),
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


ARMS = {"baseline": run_baseline, "solution": run_solution}
