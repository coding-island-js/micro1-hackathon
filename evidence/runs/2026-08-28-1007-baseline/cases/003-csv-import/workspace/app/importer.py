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

    rows = list(csv.reader(io.StringIO(csv_text)))
    if not rows:
        result.errors.append("File is empty.")
        return result

    header = [column.strip() for column in rows[0]]
    missing = [column for column in REQUIRED_COLUMNS if column not in header]
    if missing:
        result.errors.append(
            f"Missing required column(s): {', '.join(missing)}."
        )
        return result

    for line_number, row in enumerate(rows[1:], start=2):
        if not row or all(field.strip() == "" for field in row):
            continue

        if len(row) != len(header):
            result.errors.append(
                f"Row {line_number}: expected {len(header)} column(s), got {len(row)}."
            )
            continue

        record = dict(zip(header, (value.strip() for value in row)))

        empty_required = [column for column in REQUIRED_COLUMNS if not record.get(column)]
        if empty_required:
            result.errors.append(
                f"Row {line_number}: missing value for {', '.join(empty_required)}."
            )
            continue

        if "@" not in record["email"] or record["email"].startswith("@") or record["email"].endswith("@"):
            result.errors.append(f"Row {line_number}: invalid email '{record['email']}'.")
            continue

        result.users.append(record)

    return result
