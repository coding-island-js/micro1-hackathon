"""Spike: run one agent pass over the broken checkout page and keep the result.

Not part of the benchmark. This exists to answer one question before we build three more
pages: left alone with a vague ticket, does the model do shallow accessibility work?

    python experiments/spike-a11y/run_spike.py
"""
from __future__ import annotations

import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from eval import cc  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out-plain")


def main() -> int:
    with open(os.path.join(HERE, "TICKET.md"), encoding="utf-8") as f:
        ticket = f.read()
    with open(os.path.join(HERE, "implement.md"), encoding="utf-8") as f:
        system_prompt = f.read()

    work = os.path.join(tempfile.mkdtemp(prefix="spike-a11y-"), "workspace")
    shutil.copytree(os.path.join(HERE, "workspace"), work)

    print("workspace: %s" % work)
    print("running the plain pass...")

    call = cc.run_agent(
        step="implement",
        prompt="Here is the ticket.\n\n---\n\n" + ticket + "\n\n---\n\nImplement it.",
        system_prompt=system_prompt,
        cwd=work,
        model="sonnet",
    )

    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    shutil.copytree(work, OUT)
    cc.write_stream(call, os.path.join(OUT, "_trajectory.jsonl"))

    print("\nerror: %s | turns: %d | %.0fs | $%.3f"
          % (call.is_error, call.num_turns, call.duration_ms / 1000.0, call.cost_usd))
    print("result saved to experiments/spike-a11y/out-plain/")
    if call.is_error:
        print("\n--- agent reported an error ---\n%s" % call.result[:1500])
    return 0


if __name__ == "__main__":
    sys.exit(main())
