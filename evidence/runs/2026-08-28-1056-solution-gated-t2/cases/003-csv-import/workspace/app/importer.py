"""Bulk user import from an uploaded CSV.

Implement import_users.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass, field
from io import StringIO


@dataclass
class ImportResult:
    """PROVIDED. Do not change the field names -- the admin UI renders them."""

    users: list[dict] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


REQUIRED_COLUMNS = ("email", "name", "team")


def import_users(csv_text: str) -> ImportResult:
    """Parse an uploaded CSV into user records.

    Contract (fixed -- the admin upload view calls it this way):

        result = import_users(csv_text)
        result.users   -> list of dicts, one per data row, keyed by the header column names
        result.errors  -> human-readable problems, one string each

    The first line is the header and names the columns. `REQUIRED_COLUMNS` must all be
    present; anything else in the header is carried through as-is.

    A row that cannot be imported goes in `errors` and is left out of `users`. A file with
    unimportable rows still imports the rows that are fine.
    """
    result = ImportResult()

    if csv_text.startswith("﻿"):
        csv_text = csv_text[1:]

    rows = list(csv.reader(StringIO(csv_text)))
    if not rows:
        result.errors.append("The file is empty.")
        return result

    header = [col.strip() for col in rows[0]]
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in header]
    if missing_columns:
        result.errors.append(
            f"Missing required column(s): {', '.join(missing_columns)}"
        )
        return result

    duplicate_columns = sorted({col for col in header if header.count(col) > 1})
    if duplicate_columns:
        result.errors.append(
            f"Duplicate column header(s): {', '.join(duplicate_columns)}"
        )
        return result

    for line_number, row in enumerate(rows[1:], start=2):
        if not row or all(not cell.strip() for cell in row):
            continue

        if len(row) != len(header):
            result.errors.append(
                f"Row {line_number}: expected {len(header)} columns, got {len(row)}"
            )
            continue

        record = dict(zip(header, row))
        missing_values = [
            col for col in REQUIRED_COLUMNS if not record.get(col, "").strip()
        ]
        if missing_values:
            result.errors.append(
                f"Row {line_number}: missing value for {', '.join(missing_values)}"
            )
            continue

        result.users.append(record)

    return result
