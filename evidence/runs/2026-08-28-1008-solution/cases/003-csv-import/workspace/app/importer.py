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

    # Customer-supplied files show up with stray UTF-8 BOMs; strip it before parsing.
    text = csv_text.lstrip("﻿")

    reader = csv.reader(io.StringIO(text))
    try:
        header = next(reader)
    except StopIteration:
        result.errors.append("The file is empty.")
        return result

    header = [column.strip() for column in header]
    # Required columns are matched case-insensitively (customer exports vary in casing),
    # and normalized to their canonical lowercase name so downstream lookups
    # (record.get("email"), ...) work regardless of how the header spelled them.
    normalized_header = [
        column.lower() if column.lower() in REQUIRED_COLUMNS else column
        for column in header
    ]

    missing = [column for column in REQUIRED_COLUMNS if column not in normalized_header]
    if missing:
        result.errors.append(
            f"Missing required column(s): {', '.join(missing)}"
        )
        return result

    seen_columns = set()
    duplicate_columns = []
    for column in normalized_header:
        if column in seen_columns and column not in duplicate_columns:
            duplicate_columns.append(column)
        seen_columns.add(column)
    if duplicate_columns:
        result.errors.append(
            f"Duplicate column(s) in header: {', '.join(duplicate_columns)}"
        )
        return result

    seen_emails: dict[str, int] = {}

    while True:
        try:
            row = next(reader)
        except StopIteration:
            break
        except csv.Error as exc:
            # e.g. a single field exceeding csv's size limit -- report it and keep
            # importing the rest of the file instead of aborting the whole upload.
            result.errors.append(f"Row {reader.line_num}: {exc}")
            continue

        line_number = reader.line_num

        if not row or all(not cell.strip() for cell in row):
            # Blank lines are common in exported spreadsheets; skip silently.
            continue

        if len(row) != len(header):
            result.errors.append(
                f"Row {line_number}: expected {len(header)} column(s), got {len(row)}"
            )
            continue

        record = {
            name: _sanitize_cell(value.strip())
            for name, value in zip(normalized_header, row)
        }

        row_errors = []
        if not record.get("email"):
            row_errors.append("missing email")
        elif "@" not in record["email"]:
            row_errors.append("invalid email")
        if not record.get("name"):
            row_errors.append("missing name")
        if not record.get("team"):
            row_errors.append("missing team")

        if row_errors:
            result.errors.append(f"Row {line_number}: {', '.join(row_errors)}")
            continue

        email_key = record["email"].lower()
        if email_key in seen_emails:
            result.errors.append(
                f"Row {line_number}: duplicate email (already imported in row {seen_emails[email_key]})"
            )
            continue
        seen_emails[email_key] = line_number

        result.users.append(record)

    return result


_FORMULA_TRIGGER_CHARS = ("=", "+", "-", "@")


def _sanitize_cell(value: str) -> str:
    """Neutralize CSV/spreadsheet formula injection in a cell value.

    A leading apostrophe tells spreadsheet software to treat the cell as text,
    matching the standard CSV-injection mitigation.
    """
    if value and value[0] in _FORMULA_TRIGGER_CHARS:
        return "'" + value
    return value
