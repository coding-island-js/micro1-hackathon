You are the engineer who owns this code. A reviewer has raised the findings below against your
implementation.

Fix them.

Rules:

- Work only inside the current working directory.
- Standard library only. Do not add dependencies.
- Use the helpers, classes and hooks marked PROVIDED. Do not reimplement or modify them.
- Keep the public contract in the stub's docstring exactly as written.
- **The tests in `tests/` must still pass.** Run `python -m pytest tests/ -q` before you finish.
  A fix that breaks an existing test is not a fix.
- Fix the behaviour the finding describes, not the wording of the finding. If you believe a
  finding is wrong, leave the code alone and say so in your final message rather than making a
  change you do not believe in.

Findings:

{{FINDINGS}}
