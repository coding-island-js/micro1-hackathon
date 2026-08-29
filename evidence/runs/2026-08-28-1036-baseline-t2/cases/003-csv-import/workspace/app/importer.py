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

    # Customer exports (Excel etc.) commonly carry a leading BOM.
    text = csv_text.lstrip("﻿")
    reader = csv.reader(io.StringIO(text))

    try:
        header = next(reader)
    except StopIteration:
        result.errors.append("File is empty.")
        return result

    header = [column.strip() for column in header]
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in header]
    if missing_columns:
        result.errors.append(
            f"Missing required column(s): {', '.join(missing_columns)}."
        )
        return result

    seen_emails: set[str] = set()
    row_number = 1  # the header occupies row 1

    for row in reader:
        row_number += 1

        if not row or all(cell.strip() == "" for cell in row):
            continue  # blank line in the file, not a data row

        if len(row) != len(header):
            result.errors.append(
                f"Row {row_number}: expected {len(header)} columns, got {len(row)}."
            )
            continue

        record = {column: value.strip() for column, value in zip(header, row)}

        missing_fields = [column for column in REQUIRED_COLUMNS if not record.get(column)]
        if missing_fields:
            result.errors.append(
                f"Row {row_number}: missing {', '.join(missing_fields)}."
            )
            continue

        email = record["email"]
        if "@" not in email or email.startswith("@") or email.endswith("@"):
            result.errors.append(f"Row {row_number}: '{email}' is not a valid email address.")
            continue

        email_key = email.lower()
        if email_key in seen_emails:
            result.errors.append(f"Row {row_number}: duplicate email '{email}'.")
            continue
        seen_emails.add(email_key)

        result.users.append(record)

    return result
