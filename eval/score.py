"""The scorer. One code path, used by every arm.

There is deliberately no per-arm scoring anywhere in this project. `score_case` is called
with a workspace and a case id and does not know or care which arm produced the code.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HIDDEN_ROOT = os.path.join(REPO_ROOT, "benchmark", "hidden")

OUTCOME = re.compile(r"^(PASSED|FAILED|ERROR)\s+(\S+)", re.MULTILINE)
COUNTS = re.compile(r"(\d+) (passed|failed|error|errors)")


def _run_pytest(target: str, cwd: str, env_extra: dict | None = None, timeout: int = 300):
    env = dict(os.environ)
    env.pop("CASE_WORKSPACE", None)
    if env_extra:
        env.update(env_extra)
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", target,
             "-q", "--tb=no", "-rA", "-p", "no:cacheprovider"],
            cwd=cwd, env=env, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=timeout,
        )
        return proc.stdout or "", proc.returncode
    except subprocess.TimeoutExpired:
        return "TIMEOUT", -1


def _parse(output: str) -> dict:
    tests = {}
    for status, nodeid in OUTCOME.findall(output):
        tests[nodeid.split("::")[-1]] = status
    if tests:
        passed = sum(1 for v in tests.values() if v == "PASSED")
        return {"passed": passed, "total": len(tests), "tests": tests}

    # No per-test lines (e.g. a collection error). Fall back to the summary counts so a
    # broken run scores zero rather than silently scoring nothing.
    counts = {kind: int(n) for n, kind in COUNTS.findall(output)}
    total = sum(counts.values())
    return {"passed": counts.get("passed", 0), "total": total, "tests": {}}


def score_case(case_id: str, workspace: str) -> dict:
    """Score one produced workspace. Hidden tests are the metric; visible are context."""
    visible_out, _ = _run_pytest("tests", cwd=workspace)
    visible = _parse(visible_out)

    hidden_dir = os.path.join(HIDDEN_ROOT, case_id)
    hidden_out, _ = _run_pytest(
        hidden_dir, cwd=REPO_ROOT, env_extra={"CASE_WORKSPACE": workspace}
    )
    hidden = _parse(hidden_out)

    return {
        "case": case_id,
        "hidden_passed": hidden["passed"],
        "hidden_total": hidden["total"],
        "hidden_tests": hidden["tests"],
        "visible_passed": visible["passed"],
        "visible_total": visible["total"],
        "visible_tests": visible["tests"],
        "hidden_output": hidden_out[-4000:],
        "visible_output": visible_out[-2000:],
    }


def expected_hidden_total(case_id: str) -> int:
    """How many assertions the frozen benchmark holds for this case.

    Used to catch a run that scored 0/0 because the module failed to import -- which must
    read as a total failure, not as a perfect score on an empty set.
    """
    path = os.path.join(HIDDEN_ROOT, case_id, "test_invariants.py")
    with open(path, encoding="utf-8") as f:
        return len(re.findall(r"^def (test_\w+)", f.read(), re.MULTILINE))
