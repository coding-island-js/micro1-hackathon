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

# Guards against pathological uploads (accidental multi-GB files, etc.) on an
# admin-facing endpoint that accepts arbitrary customer-produced files.
MAX_FILE_BYTES = 5 * 1024 * 1024  # 5 MB
MAX_ROWS = 50_000


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

    if len(csv_text.encode("utf-8", errors="ignore")) > MAX_FILE_BYTES:
        result.errors.append(
            f"File is too large to import (max {MAX_FILE_BYTES // (1024 * 1024)} MB)."
        )
        return result

    # Customer exports frequently carry a UTF-8 BOM from Excel/Windows tools.
    text = csv_text.lstrip("﻿")

    # Customer exports don't all use commas -- e.g. Excel in many European
    # locales defaults to semicolons. Sniff the delimiter instead of assuming.
    try:
        dialect = csv.Sniffer().sniff(text[:4096], delimiters=",;\t|")
    except csv.Error:
        dialect = csv.excel  # fall back to comma-delimited

    reader = csv.reader(io.StringIO(text), dialect)
    try:
        raw_header = next(reader)
    except StopIteration:
        result.errors.append("File is empty.")
        return result

    header = [column.strip() for column in raw_header]
    normalized = [column.lower() for column in header]

    seen_columns = set()
    duplicate_columns = set()
    for column in normalized:
        if column in seen_columns:
            duplicate_columns.add(column)
        seen_columns.add(column)
    if duplicate_columns:
        result.errors.append(
            "Duplicate column(s) in header: " + ", ".join(sorted(duplicate_columns))
        )
        return result

    missing = [column for column in REQUIRED_COLUMNS if column not in normalized]
    if missing:
        result.errors.append(
            "Missing required column(s): " + ", ".join(missing)
        )
        return result

    # Required columns are keyed by their canonical lowercase name regardless
    # of how they were cased in the source file; other columns keep their
    # original header text.
    canonical_header = [
        column.lower() if column.lower() in REQUIRED_COLUMNS else column
        for column in header
    ]

    seen_emails = set()
    row_count = 0
    for line_number, row in enumerate(reader, start=2):
        if not row or all(not cell.strip() for cell in row):
            continue  # blank line, common in exports -- skip silently

        row_count += 1
        if row_count > MAX_ROWS:
            result.errors.append(
                f"File exceeds the maximum of {MAX_ROWS} rows; remaining rows were not imported."
            )
            break

        if len(row) != len(canonical_header):
            result.errors.append(
                f"Row {line_number}: expected {len(canonical_header)} column(s), got {len(row)}."
            )
            continue

        record = {column: value.strip() for column, value in zip(canonical_header, row)}

        empty_required = [
            column for column in REQUIRED_COLUMNS if not record.get(column)
        ]
        if empty_required:
            result.errors.append(
                f"Row {line_number}: missing value for {', '.join(empty_required)}."
            )
            continue

        email_key = record["email"].lower()
        if email_key in seen_emails:
            result.errors.append(
                f"Row {line_number}: duplicate email '{record['email']}' (already imported from this file)."
            )
            continue
        seen_emails.add(email_key)

        result.users.append(record)

    return result
