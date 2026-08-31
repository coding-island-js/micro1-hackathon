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

_FORMULA_TRIGGERS = ("=", "+", "-", "@")


def _sanitize(value: str) -> str:
    """Neutralize spreadsheet-formula-triggering values (CSV injection)."""
    if value.startswith(_FORMULA_TRIGGERS):
        return "'" + value
    return value


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

    # Customer exports vary -- tolerate a leading BOM from Excel-saved CSVs, and
    # normalize line endings (some legacy export tools still use bare \r) so the
    # csv module doesn't choke on them.
    text = csv_text.lstrip("﻿")
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    try:
        rows = list(csv.reader(io.StringIO(text)))
    except csv.Error as exc:
        result.errors.append(f"could not parse file: {exc}")
        return result

    reader = iter(rows)

    try:
        header = next(reader)
    except StopIteration:
        result.errors.append("file is empty")
        return result

    columns = [c.strip() for c in header]
    columns_lower = [c.lower() for c in columns]
    missing = [c for c in REQUIRED_COLUMNS if c not in columns_lower]
    if missing:
        result.errors.append(f"missing required column(s): {', '.join(missing)}")
        return result

    # Required columns are matched case-insensitively but keyed canonically (lowercase)
    # so downstream code can rely on record["email"]/["name"]/["team"]. Other columns
    # are carried through with their original name/case.
    canonical_columns = [
        c.lower() if c.lower() in REQUIRED_COLUMNS else c for c in columns
    ]

    seen_columns = set()
    duplicate_columns = []
    for c in canonical_columns:
        if c in seen_columns and c not in duplicate_columns:
            duplicate_columns.append(c)
        seen_columns.add(c)
    if duplicate_columns:
        result.errors.append(
            f"duplicate column(s) in header: {', '.join(duplicate_columns)}"
        )
        return result

    seen_emails = set()

    for line_number, row in enumerate(reader, start=2):
        if not row or all(not cell.strip() for cell in row):
            continue  # blank line -- common in hand-edited exports

        if len(row) != len(canonical_columns):
            result.errors.append(
                f"row {line_number}: expected {len(canonical_columns)} columns, got {len(row)}"
            )
            continue

        record = dict(zip(canonical_columns, (cell.strip() for cell in row)))

        if not record.get("email"):
            result.errors.append(f"row {line_number}: missing email")
            continue
        if not _EMAIL_RE.match(record["email"]):
            result.errors.append(f"row {line_number}: invalid email '{record['email']}'")
            continue
        if not record.get("name"):
            result.errors.append(f"row {line_number}: missing name")
            continue
        if not record.get("team"):
            result.errors.append(f"row {line_number}: missing team")
            continue

        email_key = record["email"].lower()
        if email_key in seen_emails:
            result.errors.append(
                f"row {line_number}: duplicate email '{record['email']}'"
            )
            continue
        seen_emails.add(email_key)

        for key, value in record.items():
            if key != "email":
                record[key] = _sanitize(value)

        result.users.append(record)

    return result
