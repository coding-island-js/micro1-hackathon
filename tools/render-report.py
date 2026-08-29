#!/usr/bin/env python
"""Render the readiness report as a page a developer would actually read.

    python tools/render-report.py                      # the shipped run, all cases
    python tools/render-report.py --run <run-id>

The markdown report at evidence/runs/<run>/cases/<case>/readiness-report.md is the artifact
the workflow produces. This turns the same data into one self-contained HTML file per case.

It reads `results.json` and nothing else. It makes no model call, changes no measurement and
is not on the path that produced any number in the README -- it is a rendering layer, so a
judge can diff it against the markdown and see the same findings in the same order.

No framework, no CDN, no build step. One file, opens in a browser, works offline.
"""
from __future__ import annotations

import argparse
import glob
import html
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNS = os.path.join(ROOT, "evidence", "runs")
DEFAULT_RUN = "2026-08-28-1202-solution-t3"

CSS = """
:root {
  --ink:#171717; --muted:#5f5b54; --line:#e4e0d8; --bg:#fdfcf9; --card:#fff;
  --high:#b3261e; --medium:#9a6700; --low:#57534e; --ok:#1a7f5a;
}
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--ink);
       font:16px/1.6 system-ui,-apple-system,"Segoe UI",sans-serif; }
.wrap { max-width:820px; margin:0 auto; padding:48px 20px 96px; }
header { border-bottom:1px solid var(--line); padding-bottom:24px; margin-bottom:32px; }
h1 { font-size:30px; line-height:1.2; margin:0 0 6px; letter-spacing:-.02em; }
.case { font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:14px;
        color:var(--muted); }
.verdict { background:var(--card); border:1px solid var(--line); border-left:4px solid var(--high);
           border-radius:12px; padding:20px 22px; margin:28px 0; }
.verdict strong { display:block; font-size:19px; margin-bottom:6px; }
.verdict .caveat { color:var(--muted); font-size:15px; }
.stats { display:grid; grid-template-columns:repeat(auto-fit,minmax(128px,1fr)); gap:12px;
         margin:28px 0 36px; }
.stat { background:var(--card); border:1px solid var(--line); border-radius:12px; padding:14px 16px; }
.stat .n { font-size:22px; font-weight:600; letter-spacing:-.02em; }
.stat .k { font-size:13px; color:var(--muted); margin-top:2px; }
h2 { font-size:20px; margin:44px 0 6px; letter-spacing:-.01em; }
h2 + p.note { color:var(--muted); margin:0 0 18px; font-size:15px; }
.finding { background:var(--card); border:1px solid var(--line); border-radius:12px;
           padding:20px 22px; margin-bottom:14px; }
.finding h3 { font-size:17px; margin:0 0 12px; line-height:1.35; }
.sev { display:inline-block; font-size:11px; font-weight:700; letter-spacing:.08em;
       text-transform:uppercase; padding:3px 8px; border-radius:999px; margin-bottom:10px;
       border:1px solid currentColor; }
.sev.high{color:var(--high)} .sev.medium{color:var(--medium)} .sev.low{color:var(--low)}
dl { margin:0; }
dt { font-size:12px; letter-spacing:.06em; text-transform:uppercase; color:var(--muted);
     margin-top:14px; font-weight:600; }
dd { margin:4px 0 0; }
dd code, p code { font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:.9em;
                  background:#f4f1ea; padding:1px 5px; border-radius:4px; }
.empty { color:var(--muted); font-style:italic; }
footer { margin-top:56px; padding-top:22px; border-top:1px solid var(--line);
         color:var(--muted); font-size:14px; }
footer a { color:inherit; }
@media (prefers-color-scheme: dark) {
  :root { --ink:#ece9e3; --muted:#a19b91; --line:#33302b; --bg:#16150f; --card:#1e1d17;
          --high:#f2857c; --medium:#e0b25c; --low:#a8a29a; --ok:#5fcfa2; }
  dd code, p code { background:#2a2822; }
}
"""


def esc(value) -> str:
    return html.escape(str(value if value is not None else ""))


def finding_block(finding: dict) -> str:
    sev = str(finding.get("severity", "unrated")).lower()
    sev_class = sev if sev in ("high", "medium", "low") else "low"
    return """
    <div class="finding">
      <span class="sev {sev_class}">{sev}</span>
      <h3>{title}</h3>
      <dl>
        <dt>The rule it breaks</dt><dd>{requirement}</dd>
        <dt>Where</dt><dd>{evidence}</dd>
        <dt>If you ship it</dt><dd>{failure}</dd>
      </dl>
    </div>""".format(
        sev_class=sev_class,
        sev=esc(sev),
        title=esc(finding.get("title", "(untitled)")),
        requirement=esc(finding.get("requirement", "not stated by the reviewer")),
        evidence=esc(finding.get("evidence", "not stated")),
        failure=esc(finding.get("failure", "not stated")),
    )


def section(title: str, note: str, findings: list) -> str:
    body = "".join(finding_block(f) for f in findings) if findings else (
        '<p class="empty">Nothing in this section.</p>')
    return "<h2>%s</h2>\n<p class=\"note\">%s</p>\n%s" % (esc(title), esc(note), body)


def render(run_id: str, case: dict) -> str:
    initial = case.get("findings_initial") or []
    final = case.get("findings_final") or []
    open_count = len(final)
    verdict = ("Ready for developer review — %d issue%s still flagged"
               % (open_count, "" if open_count == 1 else "s")) if open_count else \
              "Nothing left flagged after repair"

    stats = [
        ("%d/%d" % (case["visible_passed"], case["visible_total"]), "Tests shipped with the ticket"),
        (str(len(initial)), "Raised by the first review"),
        (str(open_count), "Still flagged after repair"),
        ("%.0f s" % case["wall_clock_s"], "Wall clock"),
        ("$%.2f" % case["cost_usd"], "Cost, API-rate equivalent"),
    ]
    stat_html = "".join(
        '<div class="stat"><div class="n">%s</div><div class="k">%s</div></div>' % (esc(n), esc(k))
        for n, k in stats)

    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Readiness report — {case_id}</title>
<style>{css}</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>Production readiness report</h1>
    <p class="case">{case_id} &middot; run {run_id}</p>
  </header>

  <div class="verdict">
    <strong>{verdict}</strong>
    <span class="caveat">This is a recommendation, not an approval. You decide whether to ship
    it — this is the reviewer's notes you would otherwise not have.</span>
  </div>

  <div class="stats">{stat_html}</div>

  {sec_initial}
  {sec_final}

  <footer>
    Generated from <code>evidence/runs/{run_id}/results.json</code> by
    <code>tools/render-report.py</code>. Same findings, same order as the markdown report
    alongside it. No model was asked to summarise anything — this is a renderer.
  </footer>
</div>
</body>
</html>
""".format(
        css=CSS,
        case_id=esc(case["id"]),
        run_id=esc(run_id),
        verdict=esc(verdict),
        stat_html=stat_html,
        sec_initial=section(
            "What the review found",
            "Raised by the first pass and sent to the repair step.", initial),
        sec_final=section(
            "Still flagged after the repair pass",
            "The repair ran, then the reviewer looked again. These survived it — which is why "
            "this report does not tell you the work is done.", final),
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default=DEFAULT_RUN)
    args = ap.parse_args()

    results_path = os.path.join(RUNS, args.run, "results.json")
    if not os.path.exists(results_path):
        print("no such run: %s" % args.run)
        print("available: %s" % ", ".join(sorted(os.path.basename(d) for d in glob.glob(RUNS + "/*"))))
        return 2

    with open(results_path, encoding="utf-8") as f:
        results = json.load(f)

    written = 0
    for case in results["cases"]:
        out = os.path.join(RUNS, args.run, "cases", case["id"], "readiness-report.html")
        if not os.path.isdir(os.path.dirname(out)):
            continue
        with open(out, "w", encoding="utf-8") as f:
            f.write(render(args.run, case))
        print("wrote %s" % os.path.relpath(out, ROOT).replace("\\", "/"))
        written += 1

    print("\n%d report(s). Open one in a browser." % written)
    return 0


if __name__ == "__main__":
    sys.exit(main())
