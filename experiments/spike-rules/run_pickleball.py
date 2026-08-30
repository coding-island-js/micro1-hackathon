"""Does a plain AI keep pickleball score correctly?

Five rally sequences. The AI is told the rules and asked for the called score after
every rally. The answer key comes from pickleball.py, not from a model.
"""
from __future__ import annotations

import json
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)

from eval import cc  # noqa: E402
import pickleball  # noqa: E402

SYSTEM = """You are keeping score in a doubles pickleball game, traditional side-out scoring.

Rules:
- Only the serving side can score a point.
- The score is called as three numbers: serving side score, receiving side score, server number.
- The very first service turn of the game begins at server number 2.
- If the serving side wins the rally, the serving side scores a point and keeps serving.
- If the receiving side wins the rally and the server number is 1, service passes to the
  partner and the server number becomes 2.
- If the receiving side wins the rally and the server number is 2, service passes to the
  other team and the server number becomes 1.

Answer with the called score after EVERY rally, in order, separated by spaces, and nothing
else. Example format: 1-0-2 2-0-2 0-2-1"""


def main() -> int:
    work = tempfile.mkdtemp(prefix="pickle-")
    results = []
    for i, seq in enumerate(pickleball.CASES, 1):
        key = pickleball.play(seq)
        words = " ".join("Team A serving side won" if s == "S" else "Receiving side won"
                         for s in seq)
        prompt = ("Team A serves first. Here are the rallies in order:\n\n"
                  + "\n".join("%d. %s" % (n, "serving side won" if s == "S" else "receiving side won")
                              for n, s in enumerate(seq, 1))
                  + "\n\nGive the called score after each rally.")
        call = cc.run_agent(step="pb%d" % i, prompt=prompt, system_prompt=SYSTEM,
                            cwd=work, model="sonnet", timeout=300)
        got = re.findall(r"\d+-\d+-\d+", call.result or "")
        ok = got == key
        results.append({"case": i, "seq": seq, "key": key, "got": got, "ok": ok,
                        "cost": call.cost_usd})
        print("case %d  %s" % (i, "CORRECT" if ok else "WRONG"))
        if not ok:
            print("   key: %s" % " ".join(key))
            print("   AI : %s" % " ".join(got))
    with open(os.path.join(HERE, "pickleball-results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    wrong = sum(1 for r in results if not r["ok"])
    print("\n%d of %d wrong. cost $%.3f" % (wrong, len(results), sum(r["cost"] for r in results)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
