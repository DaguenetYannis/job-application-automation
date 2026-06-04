from src.latex_utils import escape_latex, escape_latex_data


def test_escape_latex_escapes_sensitive_characters() -> None:
    assert escape_latex("A&B 50% x_y #1 $2") == r"A\&B 50\% x\_y \#1 \$2"


def test_escape_latex_does_not_modify_normal_text() -> None:
    assert escape_latex("normal text") == "normal text"


def test_escape_latex_data_recursively_escapes_nested_values() -> None:
    data = {
        "title": "A&B",
        "items": [{"text": "x_y", "url": "https://example.com/a_b"}],
    }

    assert escape_latex_data(data) == {
        "title": r"A\&B",
        "items": [{"text": r"x\_y", "url": "https://example.com/a_b"}],
    }
