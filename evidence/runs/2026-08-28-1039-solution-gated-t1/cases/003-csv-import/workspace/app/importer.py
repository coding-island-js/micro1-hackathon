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

    text = csv_text.lstrip("﻿")

    lines = text.splitlines()

    while lines and not lines[-1].strip():
        lines.pop()

    if not lines:
        result.errors.append("file is empty")
        return result

    try:
        header_row = next(csv.reader(io.StringIO(lines[0])), [])
    except csv.Error as exc:
        result.errors.append(f"could not parse header: {exc}")
        return result

    header = []
    for cell in header_row:
        stripped = cell.strip()
        lowered = stripped.lower()
        header.append(lowered if lowered in REQUIRED_COLUMNS else stripped)

    missing = [col for col in REQUIRED_COLUMNS if col not in header]
    if missing:
        result.errors.append(
            "missing required column(s): " + ", ".join(missing)
        )
        return result

    seen = set()
    duplicates = []
    for col in header:
        if col in seen and col not in duplicates:
            duplicates.append(col)
        seen.add(col)
    if duplicates:
        result.errors.append(
            "duplicate column(s) in header: " + ", ".join(duplicates)
        )
        return result

    for line_no, line in enumerate(lines[1:], start=2):
        try:
            row = next(csv.reader(io.StringIO(line)), [])
        except csv.Error as exc:
            result.errors.append(f"row {line_no}: could not parse row ({exc})")
            continue

        if not any(cell.strip() for cell in row):
            continue

        if len(row) != len(header):
            result.errors.append(
                f"row {line_no}: expected {len(header)} columns, got {len(row)}"
            )
            continue

        record = {col: value.strip() for col, value in zip(header, row)}

        missing_fields = [col for col in REQUIRED_COLUMNS if not record.get(col)]
        if missing_fields:
            result.errors.append(
                f"row {line_no}: missing value for {', '.join(missing_fields)}"
            )
            continue

        email = record["email"]
        if "@" not in email or email.startswith("@") or email.endswith("@"):
            result.errors.append(f"row {line_no}: invalid email address {email!r}")
            continue

        result.users.append(record)

    return result
