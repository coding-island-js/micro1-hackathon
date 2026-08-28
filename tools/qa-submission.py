#!/usr/bin/env python
"""
Submission QA gate for the micro1 hackathon entry.

Four gates, cheapest first. The prose behind each one is in
`.claude/playbooks/qa-gates.md`; this script automates the parts a machine can check and
says plainly which parts it cannot.

    python tools/qa-submission.py              # every gate
    python tools/qa-submission.py --gate 1     # one gate
    python tools/qa-submission.py --strict     # PENDING counts as failure (use on Sunday)

Exit code 0 when nothing FAILED. PENDING checks (work not done yet) do not fail the run
unless --strict. HUMAN checks never pass or fail on their own - they are printed so they
cannot be forgotten.
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PASS, FAIL, PENDING, HUMAN = "PASS", "FAIL", "PENDING", "HUMAN"
MARK = {PASS: "  ok  ", FAIL: " FAIL ", PENDING: "pending", HUMAN: "human "}

results = []


def check(gate, name, status, detail=""):
    results.append((gate, name, status, detail))


def rel(path):
    return os.path.relpath(path, ROOT).replace("\\", "/")


def read(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def tracked_text_files():
    """Every text file we would ship, excluding the obvious noise."""
    skip = (".git/", "node_modules/", "__pycache__/", "runs/")
    keep = (".md", ".py", ".js", ".ts", ".json", ".txt", ".yml", ".yaml", ".toml", ".cfg")
    out = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        r = rel(dirpath) + "/"
        if any(s in r for s in skip):
            dirnames[:] = []
            continue
        for fn in filenames:
            if fn.endswith(keep):
                out.append(os.path.join(dirpath, fn))
    return out


def git(*args):
    try:
        return subprocess.run(
            ["git"] + list(args), cwd=ROOT, capture_output=True, text=True, timeout=20
        ).stdout
    except Exception:
        return ""


# --------------------------------------------------------------------------- gate 0: hygiene

REQUIRED = [
    "CLAUDE.md", "LINEMAP.md", "RULES.md", "REQUIREMENTS.md", "README.md",
    "REPRODUCTION.md", "CHANGELOG-IMPROVEMENT.md", ".gitignore",
    ".claude/INDEX.md", ".claude/MEMORY.md",
    "ops/next-actions.md", "ops/todos.md", "ops/rubric-tracker.md", "ops/deliverables.md",
    "benchmark/MANIFEST.md", "experiments/_TEMPLATE.md",
]

SECRET_PATTERNS = [
    (r"sk-[A-Za-z0-9_\-]{20,}", "OpenAI-style key"),
    (r"sk-ant-[A-Za-z0-9_\-]{20,}", "Anthropic key"),
    (r"ghp_[A-Za-z0-9]{20,}", "GitHub token"),
    (r"AKIA[0-9A-Z]{16}", "AWS access key"),
    (r"Bearer\s+[A-Za-z0-9_\-\.]{24,}", "bearer token"),
]


def gate_hygiene():
    g = "0 hygiene"
    missing = [p for p in REQUIRED if not os.path.exists(os.path.join(ROOT, p))]
    check(g, "required files present", FAIL if missing else PASS,
          ("missing: " + ", ".join(missing)) if missing else "%d files" % len(REQUIRED))

    # ground rule 8 - no credentials anywhere in the submission
    hits = []
    for path in tracked_text_files():
        if rel(path) == "tools/qa-submission.py":
            continue  # this file contains the patterns themselves
        body = read(path)
        for pat, label in SECRET_PATTERNS:
            if re.search(pat, body):
                hits.append("%s (%s)" % (rel(path), label))
    check(g, "no credentials in repo (ground rule 8)", FAIL if hits else PASS,
          "; ".join(hits[:5]) if hits else "scanned %d files" % len(tracked_text_files()))

    # Private absolute paths break reproduction on someone else's machine. Only the surfaces a
    # judge actually runs or reads are checked - the internal memory and playbook files may
    # legitimately name Raj's paths, since they are working notes about this machine.
    shipped = ("README.md", "REPRODUCTION.md", "CHANGELOG-IMPROVEMENT.md")
    shipped_dirs = ("solution/", "baseline/", "eval/", "benchmark/", "trajectories/", "evidence/")
    leaks = [rel(p) for p in tracked_text_files()
             if (rel(p) in shipped or rel(p).startswith(shipped_dirs))
             and re.search(r"C:\\+Users\\+raj", read(p))]
    check(g, "no personal absolute paths in judge-facing files", FAIL if leaks else PASS,
          ", ".join(leaks[:5]) if leaks else "")

    # memory index and memory dir agree
    idx = os.path.join(ROOT, ".claude", "MEMORY.md")
    if os.path.exists(idx):
        listed = set(re.findall(r"memory/([a-z0-9\-]+\.md)", read(idx)))
        actual = set(os.path.basename(p) for p in
                     glob.glob(os.path.join(ROOT, ".claude", "memory", "*.md")))
        drift = (listed ^ actual)
        check(g, "MEMORY.md matches memory/", FAIL if drift else PASS,
              ("drift: " + ", ".join(sorted(drift))) if drift else "%d facts" % len(actual))

    # linemap must describe the tree that exists
    lm = os.path.join(ROOT, "LINEMAP.md")
    if os.path.exists(lm):
        body = read(lm)
        undocumented = [d for d in sorted(os.listdir(ROOT))
                        if os.path.isdir(os.path.join(ROOT, d))
                        and not d.startswith(".g") and d not in ("node_modules", "__pycache__")
                        and d + "/" not in body and d not in body]
        check(g, "LINEMAP.md covers every directory", FAIL if undocumented else PASS,
              ", ".join(undocumented) if undocumented else "")


# ------------------------------------------------------------------------- gate 1: integrity

def run_dirs():
    return sorted(glob.glob(os.path.join(ROOT, "evidence", "runs", "*")))


def gate_integrity():
    g = "1 integrity"
    runs = run_dirs()
    if not runs:
        check(g, "evaluation runs exist", PENDING, "no runs under evidence/runs/ yet")
        return

    manifest_path = os.path.join(ROOT, "benchmark", "MANIFEST.md")
    freeze = None
    m = re.search(r"\b([0-9a-f]{7,40})\b", read(manifest_path)) if os.path.exists(manifest_path) else None
    if m:
        freeze = m.group(1)

    for d in runs:
        rid = os.path.basename(d)
        res_p = os.path.join(d, "results.json")
        man_p = os.path.join(d, "manifest.json")
        if not (os.path.exists(res_p) and os.path.exists(man_p)):
            check(g, "%s has results.json + manifest.json" % rid, FAIL, "")
            continue
        try:
            res = json.loads(read(res_p))
            man = json.loads(read(man_p))
        except json.JSONDecodeError as e:
            check(g, "%s json parses" % rid, FAIL, str(e))
            continue

        cases = res.get("cases", res if isinstance(res, list) else [])
        check(g, "%s covers cases" % rid, PASS if cases else FAIL, "%d cases" % len(cases))

        missing_cost = [c.get("id", "?") for c in cases
                        if not c.get("wall_clock_s") or c.get("cost_usd") is None]
        check(g, "%s records time + cost per case" % rid,
              FAIL if missing_cost else PASS,
              ("missing on: " + ", ".join(map(str, missing_cost[:5]))) if missing_cost else "")

        rf = str(man.get("benchmark_freeze", ""))
        if freeze and rf:
            ok = rf.startswith(freeze) or freeze.startswith(rf)
            check(g, "%s ran against the frozen benchmark" % rid, PASS if ok else FAIL,
                  "" if ok else "run says %s, manifest says %s" % (rf[:12], freeze[:12]))
        else:
            check(g, "%s records a freeze hash" % rid, FAIL if not rf else PENDING,
                  "benchmark/MANIFEST.md has no freeze hash yet" if not freeze else "")


# -------------------------------------------------------------------------- gate 2: fairness

def gate_fairness():
    g = "2 fairness"
    runs = run_dirs()
    arms = {}
    for d in runs:
        man_p = os.path.join(d, "manifest.json")
        if not os.path.exists(man_p):
            continue
        try:
            man = json.loads(read(man_p))
        except json.JSONDecodeError:
            continue
        arms.setdefault(str(man.get("arm", "?")), []).append((d, man))

    if len(arms) < 2:
        check(g, "both arms have been run", PENDING,
              "arms found: %s" % (", ".join(sorted(arms)) or "none"))
    else:
        # same case ids across arms, or it is not a comparison
        sets = {}
        for arm, entries in arms.items():
            d, man = entries[-1]
            sets[arm] = tuple(sorted(man.get("case_ids", [])))
        distinct = set(sets.values())
        check(g, "both arms ran the same case ids", PASS if len(distinct) == 1 else FAIL,
              "" if len(distinct) == 1 else "; ".join("%s: %d" % (a, len(s)) for a, s in sets.items()))

        models = set()
        for arm, entries in arms.items():
            models.add(str(entries[-1][1].get("model", "?")))
        check(g, "both arms used the same model", PASS if len(models) == 1 else FAIL,
              "" if len(models) == 1 else "models: " + ", ".join(sorted(models)))

    check(g, "baseline is not a strawman - a competent dev would work this way", HUMAN,
          "playbooks/benchmark-independence.md, section on a weak baseline")
    check(g, "resource differences between arms are written down in README.md", HUMAN, "")
    check(g, "regressions reported, not netted out", HUMAN, "")


# ------------------------------------------------------------------------- gate 3: repro

def gate_repro():
    g = "3 reproducibility"
    p = os.path.join(ROOT, "REPRODUCTION.md")
    body = read(p) if os.path.exists(p) else ""
    skeleton = "🚧" in body or "_pinned_" in body
    check(g, "REPRODUCTION.md is filled in", PENDING if skeleton else PASS,
          "still a skeleton" if skeleton else "")

    for label, pat in [("pinned versions", r"(?i)python\s*\|?\s*3\.\d"),
                       ("runtime", r"(?i)runtime"),
                       ("approximate cost", r"(?i)cost")]:
        check(g, "REPRODUCTION.md states %s" % label,
              PASS if re.search(pat, body) else (PENDING if skeleton else FAIL), "")

    check(g, "executed literally on a clean machine or container", HUMAN,
          "different machine, fresh clone, fresh env - not just a fresh folder")


# --------------------------------------------------------------------------- gate 4: finish

def gate_finish():
    g = "4 finish"
    readme = read(os.path.join(ROOT, "README.md"))
    chg = read(os.path.join(ROOT, "CHANGELOG-IMPROVEMENT.md"))
    skeleton = "🚧" in readme

    placeholders = len(re.findall(r"_\[[^\]]+\]_", readme))
    check(g, "README has no unfilled placeholders",
          PENDING if skeleton else (FAIL if placeholders else PASS),
          "%d left" % placeholders if placeholders else "")

    for label, pat in [("main failure mode", r"(?i)##\s*main failure mode"),
                       ("hot take", r"(?i)##\s*hot take"),
                       ("what existed before", r"(?i)before the competition")]:
        check(g, "README has %s" % label, PASS if re.search(pat, readme) else FAIL, "")

    rows = [ln for ln in chg.splitlines()
            if ln.strip().startswith("|") and "---" not in ln
            and not ln.lower().startswith("| stage") and "no experiments yet" not in ln.lower()]
    check(g, "changelog has experiment rows", PASS if rows else PENDING,
          "%d rows" % len(rows))
    # Must be the decision on an actual experiment row. Matching the whole file passes on
    # the word "removed" in this file's own instructions, which is a false green.
    removed_rows = [
        ln for ln in rows
        if ln.count("|") >= 2 and re.search(r"(?i)\bremoved\b", ln.split("|")[-2])
    ]
    check(g, "changelog includes a removed experiment",
          PASS if removed_rows else PENDING,
          "%d row(s) decided 'removed'" % len(removed_rows))

    trajectories = [p for p in glob.glob(os.path.join(ROOT, "trajectories", "*"))
                    if not os.path.basename(p).startswith(".")]
    check(g, "trajectories exist for every agent used",
          PENDING if not trajectories else HUMAN,
          "%d file(s) - confirm one per agent" % len(trajectories))

    check(g, "every number in README traces to a results.json", HUMAN, "check three at random")
    check(g, "prose reads like a person wrote it", HUMAN,
          "20 points. Read it aloud; cut anything you would not say")
    check(g, "video <= 5:00 and covers the six required beats", HUMAN,
          "playbooks/submission-checklist.md item 3")

    # ground rule 2 - the freeze must precede the baseline evidence in history
    log = git("log", "--oneline", "--reverse")
    if not log.strip():
        check(g, "git history shows freeze before baseline evidence", PENDING, "no commits yet")
    else:
        lines = log.splitlines()
        fi = next((i for i, l in enumerate(lines) if re.search(r"(?i)freeze", l)), None)
        bi = next((i for i, l in enumerate(lines) if re.search(r"(?i)baseline", l)), None)
        if fi is None or bi is None:
            check(g, "git history shows freeze before baseline evidence", PENDING,
                  "no freeze/baseline commit found yet")
        else:
            check(g, "git history shows freeze before baseline evidence",
                  PASS if fi < bi else FAIL, "")


GATES = {
    "0": gate_hygiene, "1": gate_integrity, "2": gate_fairness,
    "3": gate_repro, "4": gate_finish,
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate", help="run one gate: 0-4")
    ap.add_argument("--strict", action="store_true",
                    help="PENDING counts as failure (use on Sunday)")
    a = ap.parse_args()

    for key in ([a.gate] if a.gate else sorted(GATES)):
        if key not in GATES:
            print("unknown gate: %s" % key)
            return 2
        GATES[key]()

    current = None
    for gate, name, status, detail in results:
        if gate != current:
            print("\n%s" % gate.upper())
            current = gate
        line = "  [%s] %s" % (MARK[status], name)
        if detail:
            line += "  -- %s" % detail
        print(line)

    n = {s: sum(1 for r in results if r[2] == s) for s in (PASS, FAIL, PENDING, HUMAN)}
    print("\n%d ok, %d failed, %d pending, %d for a human" %
          (n[PASS], n[FAIL], n[PENDING], n[HUMAN]))
    if n[HUMAN]:
        print("Human checks are never automatic. Walk them before claiming the entry is done.")

    bad = n[FAIL] + (n[PENDING] if a.strict else 0)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
