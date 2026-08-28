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


def test_names(case_id: str) -> list[str]:
    path = os.path.join(HIDDEN_ROOT, case_id, "test_invariants.py")
    with open(path, encoding="utf-8") as f:
        return re.findall(r"^def (test_\w+)", f.read(), re.MULTILINE)


def _score_hidden_per_test(case_id: str, workspace: str) -> dict:
    """Fall back to running each assertion in its own process.

    An implementation can hang one assertion -- a blocking lock on the reentrancy case will
    deadlock, which is a real defect. But a whole-suite timeout scores every assertion zero
    for one hang, which measures the wrong thing. Each test gets its own short budget; a
    hang fails that assertion only.
    """
    path = os.path.join(HIDDEN_ROOT, case_id, "test_invariants.py")
    tests, chunks = {}, []
    for name in test_names(case_id):
        out, rc = _run_pytest(
            "%s::%s" % (path, name), cwd=REPO_ROOT,
            env_extra={"CASE_WORKSPACE": workspace}, timeout=45,
        )
        hung = out == "TIMEOUT"
        tests[name] = "PASSED" if (not hung and rc == 0) else "FAILED"
        chunks.append("%s: %s%s" % (name, tests[name], "  (HUNG - timed out)" if hung else ""))
    passed = sum(1 for v in tests.values() if v == "PASSED")
    return {"passed": passed, "total": len(tests), "tests": tests,
            "output": "per-test scoring (suite did not complete)\n" + "\n".join(chunks)}


def score_case(case_id: str, workspace: str) -> dict:
    """Score one produced workspace. Hidden tests are the metric; visible are context."""
    visible_out, _ = _run_pytest("tests", cwd=workspace)
    visible = _parse(visible_out)

    hidden_dir = os.path.join(HIDDEN_ROOT, case_id)
    hidden_out, _ = _run_pytest(
        hidden_dir, cwd=REPO_ROOT, env_extra={"CASE_WORKSPACE": workspace}
    )
    hidden = _parse(hidden_out)

    if hidden_out == "TIMEOUT" or hidden["total"] != len(test_names(case_id)):
        per = _score_hidden_per_test(case_id, workspace)
        hidden = {"passed": per["passed"], "total": per["total"], "tests": per["tests"]}
        hidden_out = per["output"]

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
