"""Run one arm over the frozen benchmark and write the evidence.

    python -m eval.run --arm baseline --cases all
    python -m eval.run --arm solution --cases 002-idempotency-key

Both arms go through this file. The arm only chooses which function in eval/arms.py runs;
the workspace preparation, the scorer and the evidence format are identical either way.

The agent works in a copy of the case workspace placed in the OS temp directory, outside
this repository. It has no path to benchmark/hidden/. That isolation is structural -- it
does not depend on the agent being told not to look.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eval import arms, cc, score  # noqa: E402
from solution import report as readiness  # noqa: E402

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CASES_ROOT = os.path.join(REPO_ROOT, "benchmark", "cases")
EVIDENCE_ROOT = os.path.join(REPO_ROOT, "evidence", "runs")


def all_cases() -> list[str]:
    return sorted(
        d for d in os.listdir(CASES_ROOT) if os.path.isdir(os.path.join(CASES_ROOT, d))
    )


def git(*args: str) -> str:
    try:
        return subprocess.run(
            ["git"] + list(args), cwd=REPO_ROOT, capture_output=True, text=True, timeout=20
        ).stdout.strip()
    except Exception:
        return ""


def freeze_commit() -> str:
    """The commit that froze the benchmark. Recorded in every run's manifest."""
    out = git("log", "--format=%H %s", "--", "benchmark")
    for line in out.splitlines():
        commit, _, subject = line.partition(" ")
        if subject.lower().startswith("freeze:"):
            return commit
    return ""


def prepare_workspace(case_id: str) -> str:
    src = os.path.join(CASES_ROOT, case_id, "workspace")
    dest = os.path.join(tempfile.mkdtemp(prefix="m1hack-"), "workspace")
    shutil.copytree(src, dest)
    return dest


def ticket_for(case_id: str) -> str:
    with open(os.path.join(CASES_ROOT, case_id, "TICKET.md"), encoding="utf-8") as f:
        return f.read()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True, choices=sorted(arms.ARMS))
    ap.add_argument("--cases", default="all", help="'all' or a comma-separated list of case ids")
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--label", default="", help="optional suffix for the run id")
    args = ap.parse_args()

    cases = all_cases() if args.cases == "all" else [c.strip() for c in args.cases.split(",")]
    unknown = [c for c in cases if c not in all_cases()]
    if unknown:
        print("unknown case(s): %s" % ", ".join(unknown))
        return 2

    started = dt.datetime.now()
    run_id = "%s-%s%s" % (
        started.strftime("%Y-%m-%d-%H%M"),
        args.arm,
        ("-" + args.label) if args.label else "",
    )
    out_root = os.path.join(EVIDENCE_ROOT, run_id)
    os.makedirs(out_root, exist_ok=True)

    print("run %s | arm=%s | model=%s | %d case(s)" % (run_id, args.arm, args.model, len(cases)))

    results = []
    for case_id in cases:
        print("  %-24s " % case_id, end="", flush=True)
        case_out = os.path.join(out_root, "cases", case_id)
        os.makedirs(case_out, exist_ok=True)

        workspace = prepare_workspace(case_id)
        outcome = arms.ARMS[args.arm](ticket_for(case_id), workspace, args.model)

        for call in outcome["calls"]:
            cc.write_stream(call, os.path.join(case_out, "%s.stream.jsonl" % call.step))

        scored = score.score_case(case_id, workspace)
        expected = score.expected_hidden_total(case_id)
        if scored["hidden_total"] != expected:
            # A 0/0 is an import failure, not a perfect score. Normalise so the metric
            # always has the frozen denominator.
            scored["hidden_total"] = expected
            scored["note"] = "hidden suite did not collect cleanly; scored against the frozen total"

        shutil.copytree(workspace, os.path.join(case_out, "workspace"), dirs_exist_ok=True)

        if args.arm == "solution":
            readiness.write(
                os.path.join(case_out, "readiness-report.md"),
                readiness.render(case_id, case_id, outcome, scored),
            )

        record = {
            "id": case_id,
            "hidden_passed": scored["hidden_passed"],
            "hidden_total": scored["hidden_total"],
            "hidden_tests": scored["hidden_tests"],
            "visible_passed": scored["visible_passed"],
            "visible_total": scored["visible_total"],
            "wall_clock_s": round(sum(c.duration_ms for c in outcome["calls"]) / 1000.0, 1),
            "cost_usd": round(sum(c.cost_usd for c in outcome["calls"]), 4),
            "turns": sum(c.num_turns for c in outcome["calls"]),
            "steps": [c.summary() for c in outcome["calls"]],
            "agent_errors": [c.step for c in outcome["calls"] if c.is_error],
            "findings_initial": outcome["findings_initial"],
            "findings_final": outcome["findings_final"],
            "note": scored.get("note", ""),
        }
        results.append(record)

        with open(os.path.join(case_out, "hidden_output.txt"), "w", encoding="utf-8") as f:
            f.write(scored["hidden_output"])
        with open(os.path.join(case_out, "visible_output.txt"), "w", encoding="utf-8") as f:
            f.write(scored["visible_output"])

        print(
            "hidden %d/%d  visible %d/%d  %.0fs  $%.3f"
            % (
                record["hidden_passed"], record["hidden_total"],
                record["visible_passed"], record["visible_total"],
                record["wall_clock_s"], record["cost_usd"],
            )
        )

    passed = sum(r["hidden_passed"] for r in results)
    total = sum(r["hidden_total"] for r in results)
    manifest = {
        "run_id": run_id,
        "arm": args.arm,
        "model": args.model,
        "case_ids": cases,
        "git_commit": git("rev-parse", "HEAD"),
        "benchmark_freeze": freeze_commit(),
        "started": started.isoformat(timespec="seconds"),
        "finished": dt.datetime.now().isoformat(timespec="seconds"),
        "python": sys.version.split()[0],
        "harness": "eval/run.py",
        "invocation": " ".join(sys.argv),
    }
    summary = {
        "hidden_passed": passed,
        "hidden_total": total,
        "hidden_pass_rate": round(passed / total, 4) if total else 0.0,
        "visible_passed": sum(r["visible_passed"] for r in results),
        "visible_total": sum(r["visible_total"] for r in results),
        "wall_clock_s": round(sum(r["wall_clock_s"] for r in results), 1),
        "cost_usd": round(sum(r["cost_usd"] for r in results), 4),
        "turns": sum(r["turns"] for r in results),
    }

    with open(os.path.join(out_root, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    with open(os.path.join(out_root, "results.json"), "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "cases": results}, f, indent=2)

    lines = [
        "# Run %s" % run_id,
        "",
        "arm **%s** · model `%s` · freeze `%s` · python %s"
        % (args.arm, args.model, manifest["benchmark_freeze"][:12], manifest["python"]),
        "",
        "| Case | Hidden | Visible | Wall clock | Cost (equiv. API) |",
        "|---|---|---|---|---|",
    ]
    for r in results:
        lines.append(
            "| %s | %d/%d | %d/%d | %.0fs | $%.3f |"
            % (r["id"], r["hidden_passed"], r["hidden_total"],
               r["visible_passed"], r["visible_total"], r["wall_clock_s"], r["cost_usd"])
        )
    lines += [
        "| **total** | **%d/%d (%.1f%%)** | **%d/%d** | **%.0fs** | **$%.3f** |"
        % (passed, total, 100 * summary["hidden_pass_rate"],
           summary["visible_passed"], summary["visible_total"],
           summary["wall_clock_s"], summary["cost_usd"]),
        "",
    ]
    with open(os.path.join(out_root, "summary.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("  %-24s hidden %d/%d (%.1f%%)  %.0fs  $%.3f"
          % ("TOTAL", passed, total, 100 * summary["hidden_pass_rate"],
             summary["wall_clock_s"], summary["cost_usd"]))
    print("  evidence -> evidence/runs/%s/" % run_id)
    return 0


if __name__ == "__main__":
    sys.exit(main())
