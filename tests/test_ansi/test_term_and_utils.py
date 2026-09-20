import io
from collections.abc import Callable
from pathlib import Path
from unittest.mock import MagicMock
import xulbux.ansi as _ansi_module
from xulbux.ansi import _ANSI_SEQ_RX, S, Term, _build_open_close, _config_terminal, _StyleGroup
from xulbux.color import hexa, rgba
import pytest


def test_term_control_constants() -> None:
    assert Term.CLEAR_LINE == "\x1b[2K"
    assert Term.CLEAR_LINE_TO_END == "\x1b[0K"
    assert Term.CLEAR_LINE_TO_START == "\x1b[1K"
    assert Term.CLEAR_SCREEN == "\x1b[2J"
    assert Term.CLEAR_SCREEN_TO_END == "\x1b[0J"
    assert Term.CLEAR_SCREEN_TO_START == "\x1b[1J"
    assert Term.CLEAR_SCROLLBACK == "\x1b[3J"
    assert Term.CUR_HIDE == "\x1b[?25l"
    assert Term.CUR_SHOW == "\x1b[?25h"
    assert Term.ALT_SCREEN == "\x1b[?1049h"
    assert Term.MAIN_SCREEN == "\x1b[?1049l"
    assert Term.BELL == "\x07"
    assert Term.BRACKETED_PASTE_ENABLE == "\x1b[?2004h"
    assert Term.BRACKETED_PASTE_DISABLE == "\x1b[?2004l"
    assert Term.LINE_WRAP_ENABLE == "\x1b[?7h"
    assert Term.LINE_WRAP_DISABLE == "\x1b[?7l"
    assert Term.RESET == "\x1bc"
    assert Term.SOFT_RESET == "\x1b[!p"
    assert Term.CUR_HOME == "\x1b[H"
    assert Term.CUR_SAVE == "\x1b[s"
    assert Term.CUR_RESTORE == "\x1b[u"
    assert Term.CUR_SAVE_DEC == "\x1b7"
    assert Term.CUR_RESTORE_DEC == "\x1b8"


def test_term_cursor_methods() -> None:
    assert Term.up(3) == "\x1b[3A"
    assert Term.down(2) == "\x1b[2B"
    assert Term.left(4) == "\x1b[4D"
    assert Term.right(5) == "\x1b[5C"
    assert Term.prev_line(1) == "\x1b[1F"
    assert Term.next_line(2) == "\x1b[2E"
    assert Term.row(10) == "\x1b[10d"
    assert Term.row() == "\x1b[1d"
    assert Term.col(10) == "\x1b[10G"
    assert Term.col() == "\x1b[1G"
    assert Term.move(10, 20) == "\x1b[10;20H"
    assert Term.insert_lines(2) == "\x1b[2L"
    assert Term.delete_lines(3) == "\x1b[3M"
    assert Term.insert_chars(4) == "\x1b[4@"
    assert Term.delete_chars(5) == "\x1b[5P"
    assert Term.scroll_up(2) == "\x1b[2S"
    assert Term.scroll_down(3) == "\x1b[3T"
    assert Term.title("Terminal Title") == "\x1b]2;Terminal Title\x07"


def test_term_cursor_shape() -> None:
    assert Term.cursor_shape("blinking_block") == "\x1b[1 q"
    assert Term.cursor_shape("steady_block") == "\x1b[2 q"
    assert Term.cursor_shape("blinking_underline") == "\x1b[3 q"
    assert Term.cursor_shape("steady_underline") == "\x1b[4 q"
    assert Term.cursor_shape("blinking_bar") == "\x1b[5 q"
    assert Term.cursor_shape("steady_bar") == "\x1b[6 q"
    assert Term.cursor_shape(1) == "\x1b[1 q"
    assert Term.cursor_shape(6) == "\x1b[6 q"

    with pytest.raises(ValueError, match="cursor shape"):
        Term.cursor_shape(0)  # type:ignore[arg-type]  # pyright:ignore[reportArgumentType]
    with pytest.raises(ValueError, match="cursor shape"):
        Term.cursor_shape(7)  # type:ignore[arg-type]  # pyright:ignore[reportArgumentType]
    with pytest.raises(ValueError, match="cursor shape"):
        Term.cursor_shape("invalid_shape")  # type:ignore[arg-type]  # pyright:ignore[reportArgumentType]


def test_term_clipboard_and_cwd() -> None:
    assert Term.clipboard_copy("hello world") == "\x1b]52;c;aGVsbG8gd29ybGQ=\x1b\\"
    assert Term.cwd("/custom/path") == "\x1b]7;/custom/path\x1b\\"
    cwd_path_res = Term.cwd(Path("tests/test_ansi"))
    assert "file://" in cwd_path_res
    assert cwd_path_res.startswith("\x1b]7;")
    assert cwd_path_res.endswith("\x1b\\")

    # Verify `_ANSI_SEQ_RX` pattern matching and stripping sequences in `S.raw`:
    assert _ANSI_SEQ_RX.search("\x1b[31mHello\x1b[0m") is not None
    assert S(Term.CUR_SAVE_DEC, "hello", Term.CUR_RESTORE_DEC).raw == "hello"


def test_rgb_and_hex_overloads() -> None:
    assert S.rgb(rgba(255, 0, 0))("text").ansi == "\x1b[38;2;255;0;0mtext\x1b[39m"
    assert S.hex(hexa("#00FF00"))("text").ansi == "\x1b[38;2;0;255;0mtext\x1b[39m"
    assert "tests/test_ansi" in S.link(Path("tests/test_ansi"))("Link").ansi


def test_terminal_configuration_windows(mock_os_windows: None, mock_ctypes_windll: Callable[..., MagicMock]) -> None:
    _ansi_module._terminal_configured = False
    mock_ctypes = mock_ctypes_windll()
    mock_ctypes.kernel32.GetStdHandle.return_value = 1
    mock_ctypes.kernel32.GetConsoleMode.return_value = 1
    mock_ctypes.kernel32.SetConsoleMode.return_value = 1
    _config_terminal()
    assert _ansi_module._terminal_configured is True


def test_terminal_configuration_posix(mock_os_linux: None) -> None:
    _ansi_module._terminal_configured = False
    _config_terminal()
    assert _ansi_module._terminal_configured is True


def test_terminal_configuration_repeated_calls_are_no_ops() -> None:
    _ansi_module._terminal_configured = True
    _config_terminal()
    assert _ansi_module._terminal_configured is True


def test_styled_text_print_stream_options() -> None:
    stream = io.StringIO()
    S("No flush").print(file=stream, flush=False)
    assert stream.getvalue() == "No flush\n"


def test_build_open_close_complex_groups() -> None:
    # Fast path for single standard code:
    single_opens, single_closes = _build_open_close(_StyleGroup(S.BOLD))
    assert single_opens == ("\x1b[1m",)
    assert single_closes == ("\x1b[22m",)

    # Duplicate resets deduplication check:
    dedup_opens, dedup_closes = _build_open_close(S.BOLD | S.DIM | S.RED | S.GREEN)
    assert dedup_opens == ("\x1b[1;2;31;32m",)
    assert dedup_closes == ("\x1b[22;39m",)

    # Link only group (no SGR opens):
    link_only_opens, link_only_closes = _build_open_close(_StyleGroup(S.link("https://example.com")))
    assert link_only_opens == ("\x1b]8;;https://example.com\x1b\\",)
    assert link_only_closes == ("\x1b]8;;\x1b\\",)

    # StyleGroup with multiple colors & resets:
    complex_group = S.BOLD | S.rgb(255, 0, 0) | S.BG.rgb(0, 0, 255) | S.link("https://example.com")
    opens, closes = _build_open_close(complex_group)

    assert opens == (
        "\x1b]8;;https://example.com\x1b\\",
        "\x1b[1;38;2;255;0;0;48;2;0;0;255m",
    )
    assert closes == (
        "\x1b[22;39;49m",
        "\x1b]8;;\x1b\\",
    )
