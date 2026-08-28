#!/usr/bin/env python
"""Aggregate repeated trials into the comparison a judge should be shown.

    python tools/analyse-trials.py                       # every run in evidence/runs/
    python tools/analyse-trials.py --arms baseline solution-gated

One run is an anecdote. This reports mean, median and range per arm, per-case spread across
trials, and assertion-level stability -- so a difference can be told apart from noise.

It also answers the question that decides whether the evidence gate is worth having: how many
reviewer findings did the gate block, why, and which hidden assertions were still failing at the
end. A gate that blocks everything looks safe and is useless; the blocked findings have to be
read against the assertions that stayed red.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import statistics
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNS = os.path.join(ROOT, "evidence", "runs")


def load_runs() -> list[dict]:
    out = []
    for d in sorted(glob.glob(os.path.join(RUNS, "*"))):
        rp, mp = os.path.join(d, "results.json"), os.path.join(d, "manifest.json")
        if not (os.path.exists(rp) and os.path.exists(mp)):
            continue
        with open(rp, encoding="utf-8") as f:
            results = json.load(f)
        with open(mp, encoding="utf-8") as f:
            manifest = json.load(f)
        out.append({"dir": os.path.basename(d), "results": results, "manifest": manifest})
    return out


def pct(x: float) -> str:
    return "%.1f%%" % (100 * x)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", nargs="*", default=None)
    a = ap.parse_args()

    runs = load_runs()
    by_arm: dict[str, list] = {}
    for r in runs:
        by_arm.setdefault(r["manifest"]["arm"], []).append(r)
    arms = a.arms or sorted(by_arm)

    freezes = {r["manifest"].get("benchmark_freeze", "") for r in runs}
    if len(freezes) > 1:
        print("!! runs span more than one benchmark freeze -- not comparable: %s\n" % freezes)

    print("=" * 78)
    print("HEADLINE — hidden pass rate per arm")
    print("=" * 78)
    print("%-18s %5s  %8s %8s %8s  %8s %9s" %
          ("arm", "n", "mean", "median", "range", "wall/run", "cost/run"))
    stats = {}
    for arm in arms:
        rs = by_arm.get(arm, [])
        if not rs:
            continue
        rates = [r["results"]["summary"]["hidden_pass_rate"] for r in rs]
        walls = [r["results"]["summary"]["wall_clock_s"] for r in rs]
        costs = [r["results"]["summary"]["cost_usd"] for r in rs]
        stats[arm] = {"rates": rates, "walls": walls, "costs": costs}
        print("%-18s %5d  %8s %8s %8s  %7.0fs %9s" % (
            arm, len(rates), pct(statistics.mean(rates)), pct(statistics.median(rates)),
            "%s-%s" % (pct(min(rates)), pct(max(rates))),
            statistics.mean(walls), "$%.3f" % statistics.mean(costs)))

    if len(stats) >= 2 and "baseline" in stats:
        base = statistics.mean(stats["baseline"]["rates"])
        for arm in stats:
            if arm == "baseline":
                continue
            d = statistics.mean(stats[arm]["rates"]) - base
            spread = max(stats["baseline"]["rates"]) - min(stats["baseline"]["rates"])
            print("\n  %s vs baseline: %+.1f pts (baseline's own spread across trials: %.1f pts)"
                  % (arm, 100 * d, 100 * spread))
            if abs(d) <= spread:
                print("  ^ the difference is inside the baseline's own run-to-run spread. "
                      "Not a result yet.")

    print("\n" + "=" * 78)
    print("PER CASE — hidden passed, one column per trial")
    print("=" * 78)
    for arm in arms:
        rs = by_arm.get(arm, [])
        if not rs:
            continue
        print("\n%s" % arm)
        cases = sorted({c["id"] for r in rs for c in r["results"]["cases"]})
        for cid in cases:
            vals = []
            for r in rs:
                for c in r["results"]["cases"]:
                    if c["id"] == cid:
                        vals.append("%d/%d" % (c["hidden_passed"], c["hidden_total"]))
            print("  %-24s %s" % (cid, "  ".join(vals)))

    print("\n" + "=" * 78)
    print("ASSERTION STABILITY — how often each assertion passed, per arm")
    print("=" * 78)
    names: dict[str, set] = {}
    for r in runs:
        for c in r["results"]["cases"]:
            names.setdefault(c["id"], set()).update(c.get("hidden_tests", {}))
    for cid in sorted(names):
        print("\n%s" % cid)
        print("  %-46s %s" % ("assertion", "  ".join("%-14s" % a for a in arms)))
        for name in sorted(names[cid]):
            cells = []
            for arm in arms:
                rs = by_arm.get(arm, [])
                got = [c["hidden_tests"].get(name) for r in rs
                       for c in r["results"]["cases"] if c["id"] == cid]
                got = [g for g in got if g]
                cells.append("%d/%d" % (sum(1 for g in got if g == "PASSED"), len(got)))
            print("  %-46s %s" % (name[5:][:46], "  ".join("%-14s" % c for c in cells)))

    print("\n" + "=" * 78)
    print("EVIDENCE GATE — what it blocked, and what stayed broken")
    print("=" * 78)
    any_gate = False
    for arm in arms:
        for r in by_arm.get(arm, []):
            for c in r["results"]["cases"]:
                g = c.get("gate")
                if not g:
                    continue
                any_gate = True
                failing = sorted(k[5:] for k, v in (c.get("hidden_tests") or {}).items()
                                 if v != "PASSED")
                print("\n%s / %s" % (r["dir"], c["id"]))
                print("  repaired under gate: %d   blocked/advisory: %d   repair reverted: %s"
                      % (g.get("demonstrated", 0), g.get("advisory", 0),
                         g.get("repair_reverted")))
                for reason in g.get("advisory_reasons", []):
                    print("    - %s" % reason)
                print("  hidden assertions STILL FAILING: %s" % (", ".join(failing) or "none"))
                for f in (c.get("advisory_findings") or []):
                    print("    blocked finding: %s" % (f.get("title", "?"))[:96])
    if not any_gate:
        print("  (no gated runs yet)")

    print("\nRead the blocked findings against the still-failing assertions by hand. A blocked "
          "\nfinding that matches a still-failing assertion is a correct finding the gate "
          "\nsuppressed -- that is the gate being too conservative, and it must be reported.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
