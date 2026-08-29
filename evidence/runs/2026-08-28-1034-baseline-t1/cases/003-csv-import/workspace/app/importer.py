"""Bulk user import from an uploaded CSV.

Implement import_users.
"""
from __future__ import annotations

import csv
import io
from dataclasses import dataclass, field


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

    # Customer files sometimes carry a UTF-8 BOM from Excel exports.
    text = csv_text.lstrip("﻿")

    reader = csv.reader(io.StringIO(text))

    try:
        header = next(reader)
    except StopIteration:
        result.errors.append("The file is empty.")
        return result

    columns = [column.strip() for column in header]
    missing_columns = [c for c in REQUIRED_COLUMNS if c not in columns]
    if missing_columns:
        result.errors.append(
            "Missing required column(s): " + ", ".join(missing_columns)
        )
        return result

    for line_number, row in enumerate(reader, start=2):
        if not row or all(cell.strip() == "" for cell in row):
            continue  # blank line -- ignore, not an error

        if len(row) != len(columns):
            result.errors.append(
                f"Row {line_number}: expected {len(columns)} column(s), found {len(row)}."
            )
            continue

        record = {columns[i]: row[i].strip() for i in range(len(columns))}

        empty_required = [c for c in REQUIRED_COLUMNS if not record.get(c)]
        if empty_required:
            result.errors.append(
                f"Row {line_number}: missing value for {', '.join(empty_required)}."
            )
            continue

        result.users.append(record)

    return result
