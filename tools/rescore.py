#!/usr/bin/env python
"""Re-score completed runs from their saved workspaces, without re-running any agent.

    python tools/rescore.py            # show what would change
    python tools/rescore.py --write    # apply, preserving the original results

Why this exists: the first scorer ran each case's hidden suite as one pytest process with a
single timeout. An implementation that deadlocks one assertion -- a blocking lock on the
reentrancy case does exactly that -- made the whole suite time out, and the case scored 0/6
when five assertions actually passed. That is a measurement artifact, and it fell hardest on
the arm most likely to reach for a lock.

Re-scoring reads the produced code that is already stored under evidence/runs/<id>/cases/<case>/
workspace/, so every run is measured the same way with no new model calls and no new spend.
The original results.json is kept as results.pre-rescore.json; nothing is overwritten silently.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from eval import score  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNS = os.path.join(ROOT, "evidence", "runs")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()

    changed_any = False
    for run_dir in sorted(glob.glob(os.path.join(RUNS, "*"))):
        rp = os.path.join(run_dir, "results.json")
        if not os.path.exists(rp):
            continue
        with open(rp, encoding="utf-8") as f:
            data = json.load(f)

        run_id = os.path.basename(run_dir)
        changed = False
        for case in data["cases"]:
            ws = os.path.join(run_dir, "cases", case["id"], "workspace")
            if not os.path.isdir(ws):
                print("  %s / %s: no saved workspace, skipped" % (run_id, case["id"]))
                continue
            fresh = score.score_case(case["id"], os.path.abspath(ws))
            before = (case["hidden_passed"], case["hidden_total"])
            after = (fresh["hidden_passed"], fresh["hidden_total"])
            if before != after:
                changed = changed_any = True
                print("  %s / %-24s %d/%d -> %d/%d" %
                      (run_id, case["id"], before[0], before[1], after[0], after[1]))
            case["hidden_passed"] = fresh["hidden_passed"]
            case["hidden_total"] = fresh["hidden_total"]
            case["hidden_tests"] = fresh["hidden_tests"]
            case["rescored"] = True
            case.pop("note", None)

        passed = sum(c["hidden_passed"] for c in data["cases"])
        total = sum(c["hidden_total"] for c in data["cases"])
        data["summary"]["hidden_passed"] = passed
        data["summary"]["hidden_total"] = total
        data["summary"]["hidden_pass_rate"] = round(passed / total, 4) if total else 0.0
        data["summary"]["rescored"] = True

        if a.write:
            keep = os.path.join(run_dir, "results.pre-rescore.json")
            if not os.path.exists(keep):
                shutil.copyfile(rp, keep)
            with open(rp, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        if changed:
            print("  %s TOTAL -> %d/%d (%.1f%%)" % (run_id, passed, total, 100 * passed / total))

    if not changed_any:
        print("  no run changed under the fixed scorer")
    if not a.write:
        print("\n(dry run -- pass --write to apply)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
