import sys
import tomllib
from pathlib import Path
from unittest.mock import patch
from xulbux.cli._main import main
import pytest

ROOT_DIR = Path(__file__).parent.parent.parent
PYPROJECT_PATH = ROOT_DIR / "pyproject.toml"


def test_cli_entrypoint_registered_in_pyproject() -> None:
    with open(PYPROJECT_PATH, "rb") as file:
        pyproject_data = tomllib.load(file)

    scripts = pyproject_data.get("project", {}).get("scripts", {})
    assert "xulbux-lib" in scripts
    assert scripts["xulbux-lib"] == "xulbux.cli:main"


@pytest.mark.parametrize(
    "args, expected_outputs",
    [
        (["xulbux-lib", "ansi"], ["Text Styles", "Foreground Colors"]),
        (["xulbux-lib", "c256"], ["000", "255"]),
        (["xulbux-lib", "tc"], ["▄"]),
        (["xulbux-lib", "tc", "#FF0000"], ["▄"]),
    ],
)
def test_cli_main_subcommands(capsys: pytest.CaptureFixture[str], args: list[str], expected_outputs: list[str]) -> None:
    with patch.object(sys, "argv", args):
        main()
        captured = capsys.readouterr()
        for expected in expected_outputs:
            assert expected in captured.out


@pytest.mark.parametrize(
    "args, expected_outputs",
    [
        (["xulbux-lib"], ["Commands:", "xulbux-lib"]),
        (["xulbux-lib", "unknown_cmd"], ["Commands:"]),
    ],
)
def test_cli_main_help_subcommands(capsys: pytest.CaptureFixture[str], args: list[str], expected_outputs: list[str]) -> None:
    with patch.object(sys, "argv", args), patch("xulbux.console.pause_exit"):
        main()
        captured = capsys.readouterr()
        for expected in expected_outputs:
            assert expected in captured.out


def test_cli_main_keyboard_interrupt() -> None:
    with (
        patch.object(sys, "argv", ["xulbux-lib"]),
        patch("xulbux.cli.help.show_help", side_effect=KeyboardInterrupt),
        pytest.raises(SystemExit),
    ):
        main()
