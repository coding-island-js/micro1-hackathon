"""Bulk user import from an uploaded CSV.

Implement import_users.
"""
from __future__ import annotations

import csv
import io
import re
from collections import Counter
from dataclasses import dataclass, field


@dataclass
class ImportResult:
    """PROVIDED. Do not change the field names -- the admin UI renders them."""

    users: list[dict] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


REQUIRED_COLUMNS = ("email", "name", "team")

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


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
    reader = csv.reader(io.StringIO(csv_text))

    try:
        header = next(reader)
    except StopIteration:
        result.errors.append("File is empty.")
        return result

    # Customer exports vary -- strip stray whitespace and a leading BOM on the first
    # column, and fold case so "Email"/"EMAIL"/"email" all line up with each other.
    header = [column.strip().lstrip("﻿").lower() for column in header]

    duplicate_columns = sorted({c for c, count in Counter(header).items() if count > 1})
    if duplicate_columns:
        result.errors.append(
            f"Duplicate column(s) in header: {', '.join(duplicate_columns)}"
        )
        return result

    missing_columns = [c for c in REQUIRED_COLUMNS if c not in header]
    if missing_columns:
        result.errors.append(
            f"Missing required column(s): {', '.join(missing_columns)}"
        )
        return result

    seen_emails: dict[str, int] = {}

    for line_number, row in enumerate(reader, start=2):
        if not row or all(cell.strip() == "" for cell in row):
            continue

        if len(row) != len(header):
            result.errors.append(
                f"Row {line_number}: expected {len(header)} columns, got {len(row)}"
            )
            continue

        record = dict(zip(header, row))

        blank_fields = [c for c in REQUIRED_COLUMNS if not record[c].strip()]
        if blank_fields:
            result.errors.append(
                f"Row {line_number}: missing value(s) for {', '.join(blank_fields)}"
            )
            continue

        email = record["email"].strip()
        if not EMAIL_RE.match(email):
            result.errors.append(f"Row {line_number}: invalid email address '{email}'")
            continue

        email_key = email.lower()
        if email_key in seen_emails:
            result.errors.append(
                f"Row {line_number}: duplicate email '{email}' "
                f"(already imported on row {seen_emails[email_key]})"
            )
            continue
        seen_emails[email_key] = line_number

        result.users.append(record)

    return result
