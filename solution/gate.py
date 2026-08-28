"""The evidence gate.

Iteration 1 trusted the reviewer. It produced a confident, well-argued finding that was wrong,
the repair step acted on it, and behaviour the baseline had got right was broken. This module is
the response: **review proposes, evidence authorises.**

A finding reaches the repair step only if it clears two independent legs:

1. **It reproduces.** The reviewer's own pytest function must actually fail against the code as
   it stands. A finding with no reproduction, or one that passes, describes a defect that is not
   there.
2. **It does not contradict a PROVIDED contract.** The reviewer must check its intended
   behaviour against the docstrings in its own workspace and declare any conflict.

Leg 1 alone is not enough, and it is worth being clear why: the reviewer writes its own
reproduction, so a reviewer that believes something false will write a reproduction that fails
for the wrong reason. It would have "demonstrated" the Stripe finding perfectly well. Leg 2 is
the one that is not downstream of the reviewer's reasoning -- it points at an artifact already in
the workspace.

Findings that fail either leg are not discarded. They go to the developer in the readiness
report, which is where an unproven opinion belongs.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile

CONFTEST = (
    "import os, sys\n"
    "_ws = os.environ.get('CASE_WORKSPACE')\n"
    "if _ws and _ws not in sys.path:\n"
    "    sys.path.insert(0, _ws)\n"
)


def _run_repro(source: str, workspace: str, timeout: int = 120) -> tuple[bool, str]:
    """Run one reviewer-authored reproduction against the current workspace.

    Returns (fails_now, output). `fails_now` True means the defect is demonstrated.
    The reproduction runs in its own directory, never inside the workspace, so it cannot
    end up shipped in the delivered code or picked up by the visible test suite.
    """
    tmp = tempfile.mkdtemp(prefix="m1repro-")
    try:
        with open(os.path.join(tmp, "conftest.py"), "w", encoding="utf-8") as f:
            f.write(CONFTEST)
        with open(os.path.join(tmp, "test_repro.py"), "w", encoding="utf-8") as f:
            f.write(source)

        env = dict(os.environ)
        env["CASE_WORKSPACE"] = workspace
        try:
            proc = subprocess.run(
                [sys.executable, "-m", "pytest", "test_repro.py",
                 "-q", "--tb=short", "-p", "no:cacheprovider"],
                cwd=tmp, env=env, capture_output=True, text=True,
                encoding="utf-8", errors="replace", timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            return False, "reproduction timed out"

        output = (proc.stdout or "") + (proc.stderr or "")
        # A collection error is not a demonstrated defect -- it is a broken reproduction.
        if "error" in output.lower() and "collected 0 items" in output.lower():
            return False, output[-1500:]
        return proc.returncode != 0, output[-1500:]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def apply(findings: list, workspace: str) -> dict:
    """Split the reviewer's findings into what may be repaired and what may only be reported."""
    demonstrated, advisory = [], []

    for finding in findings or []:
        record = dict(finding)
        repro = finding.get("repro")

        if finding.get("contradicts_provided_contract"):
            record["gate"] = "blocked: contradicts a PROVIDED contract"
            record["gate_detail"] = finding.get("contradiction_note") or ""
            advisory.append(record)
            continue

        if not repro or not isinstance(repro, str) or "def test" not in repro:
            record["gate"] = "advisory: no runnable reproduction"
            advisory.append(record)
            continue

        fails_now, output = _run_repro(repro, workspace)
        record["repro_output"] = output
        if fails_now:
            record["gate"] = "demonstrated: reproduction fails against current code"
            demonstrated.append(record)
        else:
            record["gate"] = "advisory: reproduction does not fail; defect not demonstrated"
            advisory.append(record)

    return {"demonstrated": demonstrated, "advisory": advisory}


def snapshot(workspace: str) -> str:
    dest = tempfile.mkdtemp(prefix="m1snap-")
    target = os.path.join(dest, "workspace")
    shutil.copytree(workspace, target)
    return target


def restore(snapshot_path: str, workspace: str) -> None:
    shutil.rmtree(workspace, ignore_errors=True)
    shutil.copytree(snapshot_path, workspace)
