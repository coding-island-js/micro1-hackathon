"""Hidden evaluator tests for case 003.

Every assertion traces to a numbered rule in RFC 4180 section 2, "Definition of the CSV
Format", quoted in each test's docstring and recorded in benchmark/MANIFEST.md.

NEVER shown to an implementation agent.
"""
from app.importer import import_users


def only(result):
    assert result.errors == [], "unexpected errors: %r" % (result.errors,)
    assert len(result.users) == 1, "expected exactly one row, got %r" % (result.users,)
    return result.users[0]


def test_quoted_field_may_contain_a_comma():
    """RFC 4180 rule 6 -- "Fields containing line breaks (CRLF), double quotes, and commas
    should be enclosed in double-quotes".

    The naive line.split(",") passes every happy-path test and silently mangles the first
    customer whose team name has a comma in it.
    """
    row = only(import_users(
        'email,name,team\r\n'
        'ada@example.com,"Lovelace, Ada",Engineering\r\n'
    ))
    assert row["name"] == "Lovelace, Ada", (
        "a quoted field containing a comma was split into two fields"
    )
    assert row["team"] == "Engineering"


def test_doubled_quote_inside_a_quoted_field_is_a_literal_quote():
    """RFC 4180 rule 7 -- "a double-quote appearing inside a field must be escaped by
    preceding it with another double quote"."""
    row = only(import_users(
        'email,name,team\r\n'
        'ada@example.com,"Ada ""The Analyst"" Lovelace",Engineering\r\n'
    ))
    assert row["name"] == 'Ada "The Analyst" Lovelace', (
        "an escaped double-quote was not unescaped correctly"
    )


def test_quoted_field_may_span_lines():
    """RFC 4180 rule 6 -- fields containing line breaks (CRLF) are enclosed in
    double-quotes; the record continues across the physical line break."""
    result = import_users(
        'email,name,team\r\n'
        'ada@example.com,"Ada\r\nLovelace",Engineering\r\n'
    )
    assert result.errors == [], (
        "a record with a newline inside a quoted field was treated as broken: %r"
        % (result.errors,)
    )
    assert len(result.users) == 1, (
        "a quoted field containing CRLF was split into two records"
    )
    assert result.users[0]["name"] == "Ada\r\nLovelace"


def test_final_line_break_is_optional():
    """RFC 4180 rule 2 -- "The last record in the file may or may not have an ending line
    break"."""
    result = import_users(
        'email,name,team\r\n'
        'ada@example.com,Ada Lovelace,Engineering\r\n'
        'grace@example.com,Grace Hopper,Research'
    )
    assert result.errors == []
    assert len(result.users) == 2, (
        "the last record was dropped because the file had no trailing line break"
    )
    assert result.users[1]["email"] == "grace@example.com"


def test_header_row_is_not_imported_as_a_user():
    """RFC 4180 rule 3 -- "an optional header line appearing as the first line of the file
    with the same format as normal record lines"."""
    result = import_users(
        'email,name,team\r\n'
        'ada@example.com,Ada Lovelace,Engineering\r\n'
    )
    assert len(result.users) == 1, "the header row was imported as a user"
    assert result.users[0]["email"] != "email"


def test_spaces_are_part_of_the_field():
    """RFC 4180 rule 4 -- "Spaces are considered part of a field and should not be
    ignored"."""
    row = only(import_users(
        'email,name,team\r\n'
        'ada@example.com, Ada Lovelace ,Engineering\r\n'
    ))
    assert row["name"] == " Ada Lovelace ", (
        "surrounding spaces were stripped from a field; they are data"
    )
