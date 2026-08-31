"""The tests that shipped with the ticket."""
from app.importer import import_users


def test_imports_a_simple_file():
    result = import_users(
        "email,name,team\n"
        "ada@example.com,Ada Lovelace,Engineering\n"
        "grace@example.com,Grace Hopper,Engineering\n"
    )
    assert result.errors == []
    assert len(result.users) == 2
    assert result.users[0]["email"] == "ada@example.com"
    assert result.users[1]["name"] == "Grace Hopper"


def test_missing_required_column_is_an_error():
    result = import_users("email,name\nada@example.com,Ada Lovelace\n")
    assert result.errors
    assert result.users == []


def test_extra_columns_are_kept():
    result = import_users(
        "email,name,team,title\nada@example.com,Ada Lovelace,Engineering,Analyst\n"
    )
    assert result.errors == []
    assert result.users[0]["title"] == "Analyst"
