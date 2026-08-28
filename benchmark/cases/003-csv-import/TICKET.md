# ADM-77 — Bulk user import from CSV

**Component:** admin · **Priority:** P2

Onboarding a new customer means someone on our side adding users one at a time. The last one had
340. Let admins upload a CSV instead.

The file has a header row naming the columns. `email`, `name` and `team` must be present; any
other columns come through as-is. Rows that can't be imported get reported back to the admin,
and the rest of the file still imports.

`app/importer.py` has the stub and the contract.

The files come from the customer's own systems — HR exports, spreadsheets, whatever they've got —
so we don't control how they're produced.

There are tests in `tests/`. Run them with `python -m pytest tests/ -q`. They should pass when
you're done.

Don't add dependencies — standard library only.
