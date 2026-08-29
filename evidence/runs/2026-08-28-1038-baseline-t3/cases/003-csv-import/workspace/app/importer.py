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

    # Customer-produced files often carry a UTF-8 BOM from spreadsheet exports.
    text = csv_text.lstrip("﻿")

    reader = csv.reader(io.StringIO(text))
    try:
        header = next(reader)
    except StopIteration:
        result.errors.append("CSV file is empty.")
        return result

    columns = [col.strip() for col in header]
    missing = [col for col in REQUIRED_COLUMNS if col not in columns]
    if missing:
        result.errors.append(
            "Missing required column(s): " + ", ".join(missing)
        )
        return result

    seen = set()
    duplicates = {col for col in columns if col in seen or seen.add(col)}
    if duplicates:
        result.errors.append(
            "Duplicate column(s) in header: " + ", ".join(sorted(duplicates))
        )
        return result

    for line_number, row in enumerate(reader, start=2):
        if not row or all(not cell.strip() for cell in row):
            continue  # blank line -- not a real data row

        if len(row) != len(columns):
            result.errors.append(
                f"Row {line_number}: expected {len(columns)} columns, got {len(row)}."
            )
            continue

        record = {col: value.strip() for col, value in zip(columns, row)}

        empty_required = [col for col in REQUIRED_COLUMNS if not record[col]]
        if empty_required:
            result.errors.append(
                f"Row {line_number}: missing value for {', '.join(empty_required)}."
            )
            continue

        result.users.append(record)

    return result
