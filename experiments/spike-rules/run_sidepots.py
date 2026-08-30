"""Does a plain AI split side pots correctly? Answer key from sidepots.py, not a model."""
from __future__ import annotations
import json, os, re, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT); sys.path.insert(0, HERE)
from eval import cc  # noqa: E402
import sidepots  # noqa: E402

SYSTEM = """You are settling a finished poker hand at a live cash table.

Players who are all in for different amounts create a main pot and side pots. Each pot is
contested only by the players who put in at least that much money. Award every pot to the
best remaining hand eligible for that pot.

Answer with one line per player, in this exact format and nothing else:
Ann: 120
Ben: 0"""

def main() -> int:
    work = tempfile.mkdtemp(prefix="pots-")
    results = []
    for i, (contrib, ranking, text) in enumerate(sidepots.CASES, 1):
        key = sidepots.award(contrib, ranking)
        call = cc.run_agent(step="sp%d" % i, prompt=text + "\n\nHow much does each player win?",
                            system_prompt=SYSTEM, cwd=work, model="sonnet", timeout=300)
        got = {}
        for name, amount in re.findall(r"(Ann|Ben|Cal|Dee)\s*:\s*\$?([0-9,]+)", call.result or ""):
            got[name] = int(amount.replace(",", ""))
        ok = got == key
        results.append({"case": i, "key": key, "got": got, "ok": ok, "cost": call.cost_usd})
        print("case %d  %s" % (i, "CORRECT" if ok else "WRONG"))
        if not ok:
            print("   key: %s" % key)
            print("   AI : %s" % got)
    with open(os.path.join(HERE, "sidepot-results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    wrong = sum(1 for r in results if not r["ok"])
    print("\n%d of %d wrong. cost $%.3f" % (wrong, len(results), sum(r["cost"] for r in results)))
    return 0

if __name__ == "__main__":
    sys.exit(main())
