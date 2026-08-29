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

    if csv_text.startswith("﻿"):
        csv_text = csv_text[1:]

    reader = csv.reader(io.StringIO(csv_text))
    try:
        header = next(reader)
    except StopIteration:
        result.errors.append("file is empty -- no header row found")
        return result

    header = [column.strip() for column in header]
    lower_header = [column.lower() for column in header]
    missing = [column for column in REQUIRED_COLUMNS if column not in lower_header]
    if missing:
        result.errors.append(
            f"missing required column(s): {', '.join(missing)}"
        )
        return result

    # Map each required column to the actual header cell (whatever case it's in)
    # so record lookups below hit the right key regardless of how it was spelled.
    column_lookup = {
        column: header[lower_header.index(column)] for column in REQUIRED_COLUMNS
    }

    seen_emails = set()

    for row_number, row in enumerate(reader, start=2):
        if not row or all(not cell.strip() for cell in row):
            continue

        if len(row) != len(header):
            result.errors.append(
                f"row {row_number}: expected {len(header)} column(s), got {len(row)}"
            )
            continue

        record = dict(zip(header, row))

        email_key = column_lookup["email"]
        name_key = column_lookup["name"]
        team_key = column_lookup["team"]

        email = record.get(email_key, "").strip()
        name = record.get(name_key, "").strip()
        team = record.get(team_key, "").strip()

        row_errors = []
        if not email:
            row_errors.append("email is required")
        elif "@" not in email:
            row_errors.append(f"invalid email: {email!r}")
        if not name:
            row_errors.append("name is required")
        if not team:
            row_errors.append("team is required")

        if row_errors:
            result.errors.append(f"row {row_number}: {'; '.join(row_errors)}")
            continue

        if email in seen_emails:
            result.errors.append(f"row {row_number}: duplicate email: {email!r}")
            continue
        seen_emails.add(email)

        record[email_key] = email
        record[name_key] = name
        record[team_key] = team

        result.users.append(record)

    return result
