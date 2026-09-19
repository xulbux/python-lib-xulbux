from xulbux.cli.true_color import _parse_color_arg, show_true_color
import pytest


@pytest.mark.parametrize(
    "raw_color, expected_hue",
    [
        ("#FF0000", 0),
        ("00FF00", 120),
        ("#00F", 240),
        ("0xFF00FF", 300),
        ("rgb(255, 0, 0)", 0),
        ("0, 255, 0", 120),
        ("0 0 255", 240),
        ("180", 180),
        ("240deg", 240),
    ],
)
def test_parse_color_arg_valid(raw_color: str, expected_hue: int) -> None:
    result = _parse_color_arg(raw_color)
    assert result is not None
    assert result.hue == expected_hue


@pytest.mark.parametrize(
    "raw_color",
    [
        "rgb(300, 0, 0)",
        "not_a_valid_color",
        "",
        "0xINVALID",
    ],
)
def test_parse_color_arg_invalid(raw_color: str) -> None:
    assert _parse_color_arg(raw_color) is None


def test_show_true_color_full_spectrum(capsys: pytest.CaptureFixture[str]) -> None:
    show_true_color()
    captured = capsys.readouterr()
    assert "▄" in captured.out


def test_show_true_color_with_color(capsys: pytest.CaptureFixture[str]) -> None:
    show_true_color("#1E90FF")
    captured = capsys.readouterr()
    assert "▄" in captured.out


def test_show_true_color_with_invalid_color_fallback(capsys: pytest.CaptureFixture[str]) -> None:
    show_true_color("invalid_color")
    captured = capsys.readouterr()
    assert "▄" in captured.out
