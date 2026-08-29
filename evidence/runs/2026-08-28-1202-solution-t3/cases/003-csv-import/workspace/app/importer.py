"""Bulk user import from an uploaded CSV.

Implement import_users.
"""
from __future__ import annotations

import csv
import io
import re
from dataclasses import dataclass, field


@dataclass
class ImportResult:
    """PROVIDED. Do not change the field names -- the admin UI renders them."""

    users: list[dict] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


REQUIRED_COLUMNS = ("email", "name", "team")

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


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

    reader = csv.reader(io.StringIO(csv_text))
    try:
        raw_header = next(reader)
    except StopIteration:
        result.errors.append("file is empty")
        return result

    header = [column.strip() for column in raw_header]
    normalized = [column.lower() for column in header]

    seen_columns = set()
    duplicate_columns = []
    for name in normalized:
        if name in seen_columns and name not in duplicate_columns:
            duplicate_columns.append(name)
        seen_columns.add(name)
    if duplicate_columns:
        result.errors.append(
            f"duplicate column(s) in header: {', '.join(duplicate_columns)}"
        )
        return result

    missing = [column for column in REQUIRED_COLUMNS if column not in normalized]
    if missing:
        result.errors.append(
            f"missing required column(s): {', '.join(missing)}"
        )
        return result

    # Required columns are keyed by their canonical lowercase name so callers can
    # rely on record["email"] regardless of how the source file cased its header.
    keys = [
        name if name in REQUIRED_COLUMNS else original
        for name, original in zip(normalized, header)
    ]

    seen_emails = set()

    for row in reader:
        line_number = reader.line_num

        if not row or (len(row) == 1 and row[0].strip() == ""):
            continue

        if len(row) != len(header):
            result.errors.append(
                f"row {line_number}: expected {len(header)} columns, got {len(row)}"
            )
            continue

        record = dict(zip(keys, (value.strip() for value in row)))

        empty_required = [
            column for column in REQUIRED_COLUMNS if not record.get(column)
        ]
        if empty_required:
            result.errors.append(
                f"row {line_number}: missing value for {', '.join(empty_required)}"
            )
            continue

        if not _EMAIL_RE.match(record["email"]):
            result.errors.append(f"row {line_number}: invalid email '{record['email']}'")
            continue

        email_key = record["email"].lower()
        if email_key in seen_emails:
            result.errors.append(
                f"row {line_number}: duplicate email '{record['email']}'"
            )
            continue
        seen_emails.add(email_key)

        result.users.append(record)

    return result
