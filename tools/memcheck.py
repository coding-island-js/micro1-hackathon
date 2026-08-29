#!/usr/bin/env python
"""
Token-budget audit for the memory system, plus an aging-todo scan.

"sharpen up" is supposed to make memory smaller without losing facts. This makes that
measurable instead of a feeling: it prints what each tier costs, what blew its budget,
what the delta is since the last run, and which to-dos have gone stale.

    python tools/memcheck.py            # report
    python tools/memcheck.py --snap     # report, then record sizes as the new baseline

Token counts are chars/4 estimates. They are consistent, which is all a budget needs.
"""
import argparse
import datetime as dt
import glob
import json
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):  # Windows consoles default to cp1252
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAP = os.path.join(ROOT, ".claude", ".memsize.json")

# (label, glob, per-file budget, counted in the always-on session load?)
BUDGETS = [
    ("Tier 0  index",     ".claude/INDEX.md",        800, True),
    ("Tier 0  board",     "ops/next-actions.md",     800, True),
    ("Tier 1  linemap",   "LINEMAP.md",             1400, False),
    ("Tier 1  mem index", ".claude/MEMORY.md",       600, False),
    ("Tier 1  rules",     "CLAUDE.md",              1300, False),
    ("Tier 1  reqs",      "REQUIREMENTS.md",        1500, False),
    ("Tier 2  facts",     ".claude/memory/*.md",     500, False),
    ("Tier 2  playbooks", ".claude/playbooks/*.md", 1100, False),
    ("Tier 2  todos",     "ops/todos.md",            700, False),
    ("Tier 2  rubric",    "ops/rubric-tracker.md",   900, False),
    ("Tier 2  delivs",    "ops/deliverables.md",     600, False),
    # Experiment records are deliverable-grade evidence the changelog links to, and
    # judges may read them. 500 was guessed before any existed.
    ("Tier 2  experiments", "experiments/*.md",     1300, False),
    # RULES.md is deliberately unbudgeted: it is the competition text, read in full when a
    # compliance question comes up, and never trimmed to fit a token budget.
]

AGING_DAYS = 10
DUE_SOON_DAYS = 3


def tokens(path: str) -> int:
    with open(path, encoding="utf-8", errors="replace") as f:
        return round(len(f.read()) / 4)


def rel(path: str) -> str:
    return os.path.relpath(path, ROOT).replace("\\", "/")


def audit() -> tuple[dict, int, list[str]]:
    sizes: dict[str, int] = {}
    session_load = 0
    problems: list[str] = []

    for label, pattern, budget, always_on in BUDGETS:
        paths = sorted(glob.glob(os.path.join(ROOT, pattern)))
        if not paths:
            problems.append(f"MISSING  {label:18} no file matches {pattern}")
            continue
        total = 0
        for p in paths:
            n = tokens(p)
            sizes[rel(p)] = n
            total += n
            if n > budget:
                problems.append(f"OVER     {rel(p)}  {n} tok > {budget} budget")
        if always_on:
            session_load += total
        count = f"{len(paths):>2} file(s)" if len(paths) > 1 else "          "
        print(f"  {label:18} {total:>6} tok  {count}  (budget {budget}/file)")

    return sizes, session_load, problems


def dup_headings() -> list[str]:
    seen: dict[str, str] = {}
    out = []
    for p in sorted(glob.glob(os.path.join(ROOT, ".claude/memory/*.md"))):
        with open(p, encoding="utf-8", errors="replace") as f:
            head = next((l.strip("# \n").lower() for l in f if l.startswith("#")), "")
        if head and head in seen:
            out.append(f"DUPE     {rel(p)} has the same heading as {seen[head]}")
        seen[head] = rel(p)
    return out


DATED = re.compile(r"(added|due):(\d{4}-\d{2}-\d{2})")


def todo_scan() -> list[str]:
    path = os.path.join(ROOT, "ops/todos.md")
    if not os.path.exists(path):
        return ["MISSING  ops/todos.md"]
    today = dt.date.today()
    tier = ""
    flags = []
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            s = line.strip()
            if s.startswith("##"):
                tier = s.strip("# ").upper()
                continue
            if not s.startswith("-"):
                continue
            dates = dict(DATED.findall(s))
            label = re.sub(r"\s*(added|due):\d{4}-\d{2}-\d{2}", "", s.lstrip("- ")).strip()
            if "due" in dates:
                due = dt.date.fromisoformat(dates["due"])
                if (due - today).days <= DUE_SOON_DAYS:
                    flags.append(f"DUE      [{tier}] {label}  (due {due}, {(due - today).days}d)")
            if "added" in dates and ("NOW" in tier or "NEXT" in tier):
                age = (today - dt.date.fromisoformat(dates["added"])).days
                if age >= AGING_DAYS:
                    flags.append(f"AGING    [{tier}] {label}  ({age}d old)")
    return flags


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--snap", action="store_true", help="record current sizes as the baseline")
    args = ap.parse_args()

    print("MEMORY BUDGET")
    sizes, session_load, problems = audit()
    print(f"\n  ALWAYS-ON SESSION LOAD: {session_load} tok  (target < 1600)")
    if session_load > 1600:
        problems.append(f"OVER     always-on load {session_load} tok > 1600 target")

    prev = {}
    if os.path.exists(SNAP):
        with open(SNAP, encoding="utf-8") as f:
            snap = json.load(f)
        prev = snap.get("sizes", {})
        before, after = sum(prev.values()), sum(sizes.values())
        sign = "+" if after >= before else ""
        print(f"  TOTAL TRACKED MEMORY:   {after} tok  ({sign}{after - before} since "
              f"{snap.get('date', 'last snap')})")
    else:
        print(f"  TOTAL TRACKED MEMORY:   {sum(sizes.values())} tok  (no baseline yet)")

    problems += dup_headings()
    flags = todo_scan()

    if problems:
        print("\nPROBLEMS")
        for p in problems:
            print(f"  {p}")
    if flags:
        print("\nTO-DOS NEEDING A CALL  (keep / defer / drop / do-now)")
        for f in flags:
            print(f"  {f}")
    if not problems and not flags:
        print("\n  Clean. Nothing over budget, nothing aging.")

    if args.snap:
        os.makedirs(os.path.dirname(SNAP), exist_ok=True)
        with open(SNAP, "w", encoding="utf-8") as f:
            json.dump({"date": dt.date.today().isoformat(), "sizes": sizes}, f, indent=1)
        print(f"\n  baseline written -> {rel(SNAP)}")

    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
