import json
from unittest.mock import MagicMock, patch
from xulbux import __version__
from xulbux.cli.help import get_latest_version, is_latest_version, show_help
import pytest


def test_get_latest_version_successful_response() -> None:
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.__enter__.return_value = mock_response

    with (
        patch("urllib.request.urlopen", return_value=mock_response),
        patch("json.load", return_value={"info": {"version": "v2.0.0"}}),
    ):
        assert get_latest_version() == "2.0.0"


def test_get_latest_version_empty_version() -> None:
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.__enter__.return_value = mock_response

    with (
        patch("urllib.request.urlopen", return_value=mock_response),
        patch("json.load", return_value={"info": {"version": ""}}),
    ):
        assert get_latest_version() is None


def test_get_latest_version_invalid_json() -> None:
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.__enter__.return_value = mock_response

    with (
        patch("urllib.request.urlopen", return_value=mock_response),
        patch("json.load", side_effect=json.JSONDecodeError("msg", "doc", 0)),
    ):
        assert get_latest_version() is None


def test_get_latest_version_network_error() -> None:
    with patch("urllib.request.urlopen", side_effect=OSError("Connection reset by peer")):
        assert get_latest_version() is None


def test_get_latest_version_timeout() -> None:
    import time

    def _slow_urlopen(*_args: object, **_kwargs: object) -> None:
        time.sleep(0.05)

    with patch("urllib.request.urlopen", side_effect=_slow_urlopen):
        assert get_latest_version(timeout=0.005) is None


def test_get_latest_version_thread_creation_failure() -> None:
    with patch("threading.Thread", side_effect=RuntimeError("thread creation failed")):
        assert get_latest_version() is None


@pytest.mark.parametrize(
    "latest_version_ret, expected",
    [
        (None, None),
        ("", None),
        ("v1.0.0", True),
        ("v99.0.0", False),
        ("invalid_semver", None),
    ],
)
def test_is_latest_version_evaluations(latest_version_ret: str | None, expected: bool | None) -> None:
    with (
        patch("xulbux.cli.help.__version__", "1.0.0"),
        patch("xulbux.cli.help.get_latest_version", return_value=latest_version_ret),
    ):
        assert is_latest_version() is expected


@pytest.mark.parametrize(
    "provided_version, expected",
    [
        ("1.0.0", True),
        ("2.0.0", False),
        ("0.9.0", True),
    ],
)
def test_is_latest_version_with_provided_version(provided_version: str, expected: bool) -> None:
    with patch("xulbux.cli.help.__version__", "1.0.0"):
        assert is_latest_version(provided_version) is expected


def test_show_help_prints_and_pauses(capsys: pytest.CaptureFixture[str]) -> None:
    mock_pause = MagicMock()
    with patch("xulbux.console.pause_exit", mock_pause):
        show_help()

    captured = capsys.readouterr()
    assert __version__ in captured.out
    assert "Commands:" in captured.out
    assert "Modules:" in captured.out
    assert "Resources:" in captured.out
    mock_pause.assert_called_once()


def test_show_help_with_update_notice(capsys: pytest.CaptureFixture[str]) -> None:
    mock_pause = MagicMock()
    with (
        patch("xulbux.cli.help.get_latest_version", return_value="99.0.0"),
        patch("xulbux.console.pause_exit", mock_pause),
    ):
        show_help()

    captured = capsys.readouterr()
    assert "99.0.0" in captured.out
    assert "available" in captured.out
    mock_pause.assert_called_once()


def test_show_help_when_not_latest_but_get_version_none(capsys: pytest.CaptureFixture[str]) -> None:
    mock_pause = MagicMock()
    with (
        patch("xulbux.cli.help.get_latest_version", return_value=None),
        patch("xulbux.console.pause_exit", mock_pause),
    ):
        show_help()

    captured = capsys.readouterr()
    assert __version__ in captured.out
    assert "available" not in captured.out
    mock_pause.assert_called_once()
