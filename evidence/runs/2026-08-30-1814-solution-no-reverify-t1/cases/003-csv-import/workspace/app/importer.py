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

# Simple sanity check, not full RFC 5322 validation.
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# Guardrails against pathological input; generous enough for any realistic HR export.
MAX_INPUT_CHARS = 20_000_000
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

    if len(csv_text) > MAX_INPUT_CHARS:
        result.errors.append(
            f"file is too large to import (max {MAX_INPUT_CHARS} characters)"
        )
        return result

    # Excel's "CSV UTF-8" export prepends a BOM to the first field.
    csv_text = csv_text.lstrip("﻿")

    reader = csv.reader(io.StringIO(csv_text))

    try:
        header = next(reader)
    except StopIteration:
        result.errors.append("file is empty")
        return result
    except csv.Error as exc:
        result.errors.append(f"could not parse header row: {exc}")
        return result

    header = [column.strip() for column in header]
    header_norm = [column.lower() for column in header]

    duplicate_columns = sorted(
        {name for name, count in Counter(header_norm).items() if count > 1}
    )
    if duplicate_columns:
        result.errors.append(
            f"duplicate column name(s): {', '.join(duplicate_columns)}"
        )
        return result

    missing_columns = [c for c in REQUIRED_COLUMNS if c not in header_norm]
    if missing_columns:
        result.errors.append(
            f"missing required column(s): {', '.join(missing_columns)}"
        )
        return result

    # header is unique now, so this is a safe 1:1 lookup from required column -> actual header cell.
    required_header_names = {
        c: header[header_norm.index(c)] for c in REQUIRED_COLUMNS
    }
    email_header_name = required_header_names["email"]

    seen_emails: dict[str, int] = {}
    row_num = 1  # header is logical row 1

    while True:
        try:
            row = next(reader)
        except StopIteration:
            break
        except csv.Error as exc:
            row_num += 1
            result.errors.append(f"row {row_num}: could not parse ({exc})")
            continue

        row_num += 1

        if row_num - 1 > MAX_ROWS:
            result.errors.append(
                f"import stopped after {MAX_ROWS} rows; remaining rows were not processed"
            )
            break

        if not row or all(not cell.strip() for cell in row):
            continue  # blank line, not an error

        if len(row) != len(header):
            result.errors.append(
                f"row {row_num}: expected {len(header)} columns, got {len(row)}"
            )
            continue

        record = {h: v.strip() for h, v in zip(header, row)}

        empty_required = [
            c for c in REQUIRED_COLUMNS if not record[required_header_names[c]]
        ]
        if empty_required:
            result.errors.append(
                f"row {row_num}: missing value for {', '.join(empty_required)}"
            )
            continue

        email = record[email_header_name]
        if not _EMAIL_RE.match(email):
            result.errors.append(f"row {row_num}: invalid email address: {email}")
            continue

        email_key = email.lower()
        if email_key in seen_emails:
            result.errors.append(
                f"row {row_num}: duplicate email (already used on row {seen_emails[email_key]}): {email}"
            )
            continue
        seen_emails[email_key] = row_num

        result.users.append(record)

    return result
