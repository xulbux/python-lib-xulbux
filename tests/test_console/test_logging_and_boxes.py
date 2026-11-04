import io
from unittest.mock import patch
from xulbux.ansi import S
from xulbux.console import (
    _LOG_TITLE_CACHE_MAX,
    _persist_style,
    _prepare_log_box,
    _render_log_title,
    _resolve_title_colors,
    _split_hr_parts,
    _to_bg_color_style,
    _to_fg_color_style,
    banner,
    box,
    debug,
    error,
    exit,
    info,
    log,
    success,
    warn,
)
import pytest


def test_log_functions_presets() -> None:
    stream = io.StringIO()
    with patch("sys.stdout", stream), patch("xulbux.console._read_single_key") as mock_read_key:
        # Basic log:
        log("TITLE", "Hello Log", title_bg_color=S.BG.RED, default_color=S.GREEN)

        # Presets:
        debug("Debug message", active=True, pause=False, exit_code=None)
        debug("Inactive debug", active=False, exit_code=10)
        info("Info message", pause=True, exit_code=None)
        success("Success message", pause=False, exit_code=None)
        warn("Warn message", pause=False, exit_code=None)
        error("Error message", pause=False)
        error("Error message none", pause=False, exit_code=None)

    mock_read_key.assert_called_once()
    output = stream.getvalue()
    assert "TITLE" in output
    assert "DEBUG" in output
    assert "INFO" in output
    assert "OKAY" in output
    assert "WARN" in output
    assert "ERROR" in output
    assert "Inactive debug" not in output


def test_log_error_presets_error_and_exit() -> None:
    # Error with system exit (explicit code):
    with pytest.raises(SystemExit) as exc_info:
        error("Fatal error", pause=False, exit_code=3)
    assert exc_info.value.code == 3

    with pytest.raises(SystemExit) as exc_info_one:
        error("Fatal error code 1", pause=False, exit_code=1)
    assert exc_info_one.value.code == 1

    # Exit preset with system exit (defaulting code):
    with pytest.raises(SystemExit) as exc_info_default:
        exit("Exiting program", pause=False)
    assert exc_info_default.value.code == 0

    # Exit preset with system exit (explicit code):
    with pytest.raises(SystemExit) as exc_info:
        exit("Exiting program", pause=False, exit_code=5)
    assert exc_info.value.code == 5

    # Presets with system exit:
    with pytest.raises(SystemExit) as exc_info:
        debug("Debug exit", active=True, pause=False, exit_code=10)
    assert exc_info.value.code == 10

    with pytest.raises(SystemExit) as exc_info:
        info("Info exit", pause=False, exit_code=11)
    assert exc_info.value.code == 11

    with pytest.raises(SystemExit) as exc_info:
        success("Success exit", pause=False, exit_code=12)
    assert exc_info.value.code == 12

    with pytest.raises(SystemExit) as exc_info:
        warn("Warn exit", pause=False, exit_code=13)
    assert exc_info.value.code == 13


def test_log_empty_title_and_colors() -> None:
    stream = io.StringIO()
    with patch("sys.stdout", stream):
        log(None, "No title message", title_bg_color=None, default_color=None)
        log("HEX_BG", "Message", title_bg_color=S.BG.hex("#FF0000"), default_color=S.hex("#00FF00"))
        log("DARK_BG", "Message", title_bg_color=S.BG.hex("#000000"), default_color=S.hex("#00FF00"))

    output = stream.getvalue()
    assert "No title message" in output
    assert "HEX_BG" in output
    assert "DARK_BG" in output


def test_log_invalid_arguments() -> None:
    with pytest.raises(ValueError, match="indent"):
        log("TITLE", "Msg", indent=-1)
    with pytest.raises(ValueError, match="tab_size"):
        log("TITLE", "Msg", tab_size=-1)
    with pytest.raises(ValueError, match="title_px"):
        log("TITLE", "Msg", title_px=-1)
    with pytest.raises(ValueError, match="title_mx"):
        log("TITLE", "Msg", title_mx=-1)
    with pytest.raises(ValueError, match="title_bg_color"):
        log("★", "Msg", compact=True, title_bg_color="invalid")  # type:ignore[arg-type]  # pyright:ignore[reportArgumentType]
    with pytest.raises(ValueError, match="default_color"):
        log("★", "Msg", compact=True, default_color="invalid")  # type:ignore[arg-type]  # pyright:ignore[reportArgumentType]


def test_log_compact_mode_and_presets() -> None:
    stream = io.StringIO()
    with patch("sys.stdout", stream), patch("xulbux.console.get_width", return_value=30):
        # Direct compact log variations:
        log("⚠", "Line one\nLine two", compact=True, default_color=S.BR.YELLOW)
        log("WARN", "Multi-char title truncates to one char", compact=True, title_bg_color=S.BG.BR.CYAN)
        log(None, "Empty title aligns on two spaces", compact=True)
        log("★", "Uncolored compact icon", compact=True)
        log("★", "Separate icon and text colors", compact=True, title_bg_color=S.BG.RED, default_color=S.WHITE)

        # Compact presets:
        debug("Compact debug", compact=True)
        debug("Inactive compact debug", active=False, compact=True)
        info("Compact info", compact=True)
        success("Compact success", compact=True)
        warn("Compact warn", compact=True)
        error("Compact error", compact=True)
        warn("Custom color warn", compact=True, default_color=S.WHITE)

    raw_output = S(stream.getvalue()).raw
    raw_lines = raw_output.splitlines()
    raw_lines_set = set(raw_lines)
    assert raw_lines[0] == "⚠ Line one"
    assert raw_lines[1] == "  Line two"
    assert raw_lines[2].startswith("W Multi-char")
    assert raw_lines[3].startswith("  ")
    assert "\n  Empty title" in raw_output
    assert "\n★ Uncolored compact icon" in raw_output
    assert "⚙ Compact debug" in raw_lines_set
    assert "🛈 Compact info" in raw_lines_set
    assert "✓ Compact success" in raw_lines_set
    assert "⚠ Compact warn" in raw_lines_set
    assert "✗ Compact error" in raw_lines_set
    assert "Inactive compact debug" not in raw_output

    # Compact exit preset:
    exit_stream = io.StringIO()
    with patch("sys.stdout", exit_stream), pytest.raises(SystemExit) as exc_info:
        exit("Compact exit", compact=True, exit_code=2)
    assert exc_info.value.code == 2
    assert S(exit_stream.getvalue()).raw.strip() == "⯃ Compact exit"


def test_log_indentation() -> None:
    stream = io.StringIO()
    with patch("sys.stdout", stream), patch("xulbux.console.get_width", return_value=40):
        success("Deleted item\nSecond line", compact=True, indent=2)
        warn("Indented warning", compact=True, indent=4, start="\n")
        log(None, "Indented untitled compact", compact=True, indent=2)
        log("INFO", "Badge first\nBadge second", indent=3, title_bg_color=S.BG.BR.BLUE)
        log(None, "Indented untitled badge", indent=3)

    raw_lines = S(stream.getvalue()).raw.splitlines()
    assert raw_lines[0] == "  ✓ Deleted item"
    assert raw_lines[1] == "    Second line"
    assert raw_lines[2] == ""
    assert raw_lines[3] == "    ⚠ Indented warning"
    assert raw_lines[4] == "    Indented untitled compact"
    assert raw_lines[5] == "      INFO         Badge first"
    assert raw_lines[6] == "                   Badge second"
    assert raw_lines[7] == "     Indented untitled badge"


def test_banner_rendering_and_options() -> None:
    # Default print=True writes to stdout and returns None:
    stream = io.StringIO()
    with patch("sys.stdout", stream), patch("xulbux.console.get_width", return_value=40):
        ret = banner("App Error", "Invalid flag '--foo'", bg=S.BG.BR.RED)
    assert ret is None
    printed_lines = S(stream.getvalue()).raw.splitlines()
    assert printed_lines[0] == "▄" * 40
    assert printed_lines[1] == "█ App Error" + " " * 28 + "█"
    assert printed_lines[2] == "█ Invalid flag '--foo'" + " " * 17 + "█"
    assert printed_lines[3] == "▀" * 40

    # Inline subtitle when fitting vs wrapping fallback:
    inline_fit = banner("Tool", "Fast utility", bg=True, inline_subtitle=True, width=40, print=False)
    fit_lines = inline_fit.raw.split("\n")
    assert len(fit_lines) == 3
    assert "Tool — Fast utility" in fit_lines[1]

    inline_overflow = banner(
        "Long Tool Title",
        "Long subtitle text that will exceed forty columns",
        bg=S.BG.hex("#112233"),
        inline_subtitle=True,
        width=30,
        print=False,
    )
    assert len(inline_overflow.raw.split("\n")) > 3

    # Shrinkwrap width=None, custom default_color, indent, alignment, and {hr}:
    shrunk = banner(
        "Header",
        "Top\n{hr}\nBottom",
        bg=S.BG.color256(21),
        default_color=S.BR.WHITE,
        width=None,
        align="center",
        indent=2,
        print=False,
    )
    shrunk_lines = shrunk.raw.split("\n")
    assert shrunk_lines[0].startswith("  ▄")
    assert shrunk_lines[1].startswith("  █ ")
    assert shrunk_lines[1].endswith(" █")
    assert shrunk_lines[3] == "  █ ────── █"
    assert shrunk_lines[-1].startswith("  ▀")

    # Styled S subtitle with {hr} and without {hr}, subtitle-only, and empty banner:
    styled_hr = banner("Styled", S("Part A\n{hr}\n", S.DIM("Part B")), width=24, print=False)
    assert "─" in styled_hr.raw

    styled_multiline = banner(None, S.ITALIC("Sub line 1\nSub line 2"), bg=True, default_color=S.CYAN, width=24, print=False)
    assert "Sub line 1" in styled_multiline.raw
    assert "Sub line 2" in styled_multiline.raw

    right_aligned = banner("Right", width=20, align="right", print=False)
    assert right_aligned.raw.split("\n")[1] == "█            Right █"

    empty_banner = banner(None, None, width=10, print=False)
    assert empty_banner.raw.split("\n") == ["▄" * 10, "▀" * 10]


def test_banner_validation() -> None:
    with pytest.raises(ValueError, match="bg"):
        banner("Err", bg=False)  # type:ignore[call-overload]  # pyright:ignore[reportArgumentType]
    with pytest.raises(ValueError, match="bg"):
        banner("Err", bg=None)  # type:ignore[call-overload]  # pyright:ignore[reportArgumentType]
    with pytest.raises(ValueError, match="bg"):
        banner("Err", bg=S.RED)  # type:ignore[call-overload]  # pyright:ignore[reportArgumentType]
    with pytest.raises(ValueError, match="default_color"):
        banner("Err", default_color=S.BG.RED)  # type:ignore[call-overload]  # pyright:ignore[reportArgumentType]
    with pytest.raises(ValueError, match="align"):
        banner("Err", align="invalid")  # type:ignore[call-overload]  # pyright:ignore[reportArgumentType]
    with pytest.raises(ValueError, match="indent"):
        banner("Err", indent=-1)
    with pytest.raises(ValueError, match="width"):
        banner("Err", width=4)
    with pytest.raises(ValueError, match="width"):
        banner("Err", width="invalid")  # type:ignore[call-overload]  # pyright:ignore[reportArgumentType]
    with pytest.raises(ValueError, match="width"):
        banner("Err", width=True)  # pyright:ignore[reportArgumentType]


def test_box_filled_and_bordered() -> None:
    stream = io.StringIO()
    with patch("sys.stdout", stream):
        # Filled box without border:
        box(
            "Line 1",
            "Line 2",
            bg=S.BG.BLUE,
            default_color=S.WHITE,
            width=None,
            indent=2,
        )

        # Inverted default background:
        box("Inverted box", bg=True, width="full")

        # Bordered box:
        box(
            "Section 1",
            "{hr}",
            "Section 2",
            border="rounded",
            border_style=S.CYAN,
            default_color=S.WHITE,
            width=None,
        )

        # Standard, strong, and double borders:
        box("Standard", border="standard")
        box("Strong", border="strong")
        box("Double", border="double")

        # Custom 11-character border:
        custom_borders = "+-+|+-+|+-+"
        box("Custom border", border_chars=custom_borders)

        # Border with None style:
        box("Border without style", border="rounded", border_style=None)

        # Borderless with background:
        box("Top BG Custom", "{hr}", "Bottom BG Custom", bg=S.BG.BLUE)

        # Borderless without background:
        box("Top", "{hr}", "Bottom", border=None, bg=None)

        # Fixed width bordered, filled, and plain boxes:
        box("Fixed width bordered", width=30)
        box("Fixed width filled", bg=S.BG.MAGENTA, width=30)
        box("Fixed width plain", border=None, bg=None, width=30)

        # Fixed width with text wrapping and HR:
        box(
            "This is a longer line of content that will definitely wrap across multiple lines inside the box.",
            "{hr}",
            "Second section with wrapped content as well.",
            width=30,
        )

        # Styled text wrapping:
        box(
            S.GREEN("Styled green text that should wrap cleanly into multiple lines without breaking styles."),
            width=25,
        )

    output = stream.getvalue()
    assert "Line 1" in output
    assert "Line 2" in output
    assert "Inverted box" in output
    assert "Section 1" in output
    assert "Section 2" in output
    assert "Standard" in output
    assert "Strong" in output
    assert "Double" in output
    assert "Custom border" in output
    assert "Top BG Custom" in output
    assert "Top" in output
    assert "Fixed width bordered" in output


def test_box_fixed_width_dimensions() -> None:
    # Bordered box with fixed width:
    res = box("Short text", width=40, print=False)
    for line in res.raw.split("\n"):
        assert len(line) == 40

    # Filled box with fixed width:
    res_filled = box("Short text", bg=S.BG.GREEN, width=40, print=False)
    for line in res_filled.raw.split("\n"):
        assert len(line) == 40

    # Plain box with fixed width:
    res_plain = box("Short text", border=None, bg=None, width=40, print=False)
    for line in res_plain.raw.split("\n"):
        assert len(line) == 40

    # Plain box without width has zero padding (no leading indentation):
    res_plain_zero_pad = box("No leading spaces", border=None, bg=None, print=False)
    assert res_plain_zero_pad.raw == "No leading spaces"

    # Auto width (width=None) caps at terminal width:
    with patch("xulbux.console.get_width", return_value=35):
        long_auto = "This line is very long and should automatically wrap at the terminal width without breaking the box."
        res_auto = box(long_auto, border="rounded", print=False)
        for line in res_auto.raw.split("\n"):
            assert len(line) <= 35

    # Multiline wrapping with fixed width:
    long_text = "This is a long sentence that should be wrapped onto multiple lines cleanly."
    res_wrapped = box(long_text, width=30, print=False)
    lines = res_wrapped.raw.split("\n")
    assert len(lines) > 3
    for line in lines:
        assert len(line) == 30

    # Styled content wrapping:
    styled_long = S.RED("This is a styled sentence that will wrap onto multiple lines inside the box.")
    res_styled = box(styled_long, width=25, print=False)
    for line in res_styled.raw.split("\n"):
        assert len(line) == 25

    # Full width:
    res_full = box("Full width box", width="full", print=False)
    assert len(res_full.raw.split("\n")[0]) > 0


def test_box_return_s_object() -> None:
    res = box("Returned Box", "{hr}", "Line 2", border="rounded", print=False)
    assert isinstance(res, S)
    assert "Returned Box" in res.raw
    assert "Line 2" in res.raw

    res_filled = box("Filled Returned", bg=S.BG.GREEN, print=False)
    assert isinstance(res_filled, S)
    assert "Filled Returned" in res_filled.raw


def test_box_validation() -> None:
    with pytest.raises(ValueError, match="indent"):
        box("Error", indent=-1)
    with pytest.raises(ValueError, match="exactly 11 characters"):
        box("Error", border_chars="+-")
    with pytest.raises(ValueError, match="border_style"):
        box("Error", border_style=S.BG.RED)
    with pytest.raises(ValueError, match="border_style"):
        box("Error", border_style=object())  # type:ignore[call-overload]  # pyright:ignore[reportArgumentType]
    with pytest.raises(ValueError, match="border"):
        box("Error", border="invalid")  # type:ignore[call-overload]  # pyright:ignore[reportArgumentType]
    with pytest.raises(ValueError, match="bg"):
        box("Error", bg="invalid")  # type:ignore[call-overload]  # pyright:ignore[reportArgumentType]
    with pytest.raises(ValueError, match="width"):
        box("Error", width=-1)
    with pytest.raises(ValueError, match="width"):
        box("Error", width=3)  # too small: min is 2 + 2*1 + 1 = 5
    with pytest.raises(ValueError, match="width"):
        box("Error", width="invalid")  # type:ignore[call-overload]  # pyright:ignore[reportArgumentType]
    with pytest.raises(ValueError, match="width"):
        box("Error", width=True)  # pyright:ignore[reportArgumentType]
    with pytest.raises(ValueError, match="align"):
        box("Error", align="invalid")  # type:ignore[call-overload]  # pyright:ignore[reportArgumentType]


def test_box_alignment() -> None:
    # Left, center, right alignment in bordered box:
    res_l = box("Hi", width=20, align="left", print=False)
    line_l = res_l.raw.split("\n")[1]
    assert line_l == "│ Hi               │"

    res_r = box("Hi", width=20, align="right", print=False)
    line_r = res_r.raw.split("\n")[1]
    assert line_r == "│               Hi │"

    res_c = box("Hi", width=20, align="center", print=False)
    line_c = res_c.raw.split("\n")[1]
    assert line_c == "│        Hi        │"

    # Trailing whitespace stripped on right and center alignment:
    res_r_spaces = box("Hi   ", width=20, align="right", print=False)
    assert res_r_spaces.raw.split("\n")[1] == "│               Hi │"

    res_c_spaces = box("Hi   ", width=20, align="center", print=False)
    assert res_c_spaces.raw.split("\n")[1] == "│        Hi        │"

    # Styled trailing whitespace stripped on right alignment:
    res_r_styled = box(S.RED("Hi   "), width=20, align="right", print=False)
    assert res_r_styled.raw.split("\n")[1] == "│               Hi │"

    # Wrapped lines strip trailing whitespace on right alignment:
    long_txt = "This is a sentence that wraps nicely across lines."
    res_wrap_r = box(long_txt, width=25, align="right", print=False)
    for line in res_wrap_r.raw.split("\n")[1:-1]:
        assert line.endswith(" │")
        assert not line.endswith("  │")

    # Alignment in filled box:
    res_filled_c = box("Hi", bg=S.BG.GREEN, width=20, align="center", print=False)
    line_fc = res_filled_c.raw.split("\n")[1]
    assert line_fc == "         Hi         "

    res_filled_r = box("Hi", bg=S.BG.GREEN, width=20, align="right", print=False)
    line_fr = res_filled_r.raw.split("\n")[1]
    assert line_fr == "                Hi  "

    # Alignment in plain box:
    res_plain_c = box("Hi", border=None, bg=None, width=20, align="center", print=False)
    assert res_plain_c.raw == "         Hi         "

    res_plain_r = box("Hi", border=None, bg=None, width=20, align="right", print=False)
    assert res_plain_r.raw == "                  Hi"


def test_style_resolution_and_persistence_helpers() -> None:
    # _resolve_title_colors:
    bg_style, fg_style = _resolve_title_colors(S.BG.RED)
    assert bg_style == S.BG.RED and fg_style == S.hex(0x000000)
    assert _resolve_title_colors(S.BG.BR.BLACK)[1] == S.hex(0xFFFFFF)

    bg_color_dark, fg_color_dark = _resolve_title_colors(S.BG.hex("#000000"))
    assert bg_color_dark is not None and fg_color_dark == S.hex(0xFFFFFF)

    bg_color_light, fg_color_light = _resolve_title_colors(S.BG.hex("#FFFFFF"))
    assert bg_color_light is not None and fg_color_light == S.hex(0x000000)

    # 256-color testing (base, cube dark/light, grayscale dark/light, and cache hit):
    assert _resolve_title_colors(S.BG.color256(0))[1] == S.hex(0xFFFFFF)
    assert _resolve_title_colors(S.BG.color256(1))[1] == S.hex(0x000000)
    assert _resolve_title_colors(S.BG.color256(16))[1] == S.hex(0xFFFFFF)
    assert _resolve_title_colors(S.BG.color256(16))[1] == S.hex(0xFFFFFF)  # Cache hit
    assert _resolve_title_colors(S.BG.color256(231))[1] == S.hex(0x000000)
    assert _resolve_title_colors(S.BG.color256(232))[1] == S.hex(0xFFFFFF)
    assert _resolve_title_colors(S.BG.color256(255))[1] == S.hex(0x000000)

    with pytest.raises(ValueError, match="title_bg_color"):
        _resolve_title_colors("invalid_color")
    with pytest.raises(ValueError, match="title_bg_color"):
        _resolve_title_colors(S.RED)

    # _to_bg_color_style:
    assert _to_bg_color_style(S.BG.BLUE) == S.BG.BLUE
    assert _to_bg_color_style(S.BG.rgb(10, 20, 30)) is not None
    with pytest.raises(ValueError, match="box_bg_color"):
        _to_bg_color_style(S.BLUE)
    with pytest.raises(ValueError, match="box_bg_color"):
        _to_bg_color_style(object())

    # _to_fg_color_style:
    assert _to_fg_color_style(S.GREEN) == S.GREEN
    assert _to_fg_color_style(S.hex("#ff00ff")) is not None
    with pytest.raises(ValueError, match="color"):
        _to_fg_color_style(S.BG.GREEN)
    with pytest.raises(ValueError, match="color"):
        _to_fg_color_style(object())

    # _persist_style:
    assert _persist_style("plain text", "\x1b[31m") == "plain text"
    assert _persist_style("plain text", "") == "plain text"
    persisted = _persist_style("hello \x1b[32mworld\x1b[0m", "\x1b[41m")
    assert "\x1b[41m" in persisted

    # _render_log_title caching and cached hit:
    res1 = _render_log_title("HIT_TEST", S.BG.GREEN)
    res2 = _render_log_title("HIT_TEST", S.BG.GREEN)
    assert res1 == res2

    # _render_log_title cache limit fill:
    for idx in range(_LOG_TITLE_CACHE_MAX + 10):
        _ = _render_log_title(f"CACHE_TEST_{idx}", S.BG.RED)
    # Extra call with full cache and new key:
    res_overflow = _render_log_title("OVERFLOW_TITLE", S.BG.YELLOW)
    assert res_overflow is not None


def test_split_hr_parts_and_prepare_log_box() -> None:
    # _split_hr_parts edge cases:
    parts_1 = _split_hr_parts("pre{hr}post")
    assert len(parts_1) == 3
    parts_2 = _split_hr_parts("{hr}start")
    assert len(parts_2) == 2
    parts_3 = _split_hr_parts("end{hr}")
    assert len(parts_3) == 2
    parts_4 = _split_hr_parts("alone\n{hr}\nalone")
    assert len(parts_4) >= 1
    parts_5 = _split_hr_parts("{hr}")
    assert len(parts_5) == 1
    parts_6 = _split_hr_parts("")
    assert len(parts_6) == 1
    parts_7 = _split_hr_parts("pre{hr}{hr}post")
    assert len(parts_7) == 4

    # _prepare_log_box with S and tuple items:
    ansi_lines, _, max_w = _prepare_log_box(
        [S.RED("Styled line 1\nStyled line 2"), ("Tuple line 1",), "Plain line"],
        has_rules=True,
    )
    assert len(ansi_lines) == 4
    assert max_w > 0

    # _prepare_log_box with wrap_width:
    ansi_w, plain_w, max_len_w = _prepare_log_box(
        [S.RED("Styled line that is very long"), "A plain string that is very long", "{hr}"],
        has_rules=True,
        wrap_width=10,
    )
    assert len(ansi_w) > 3
    assert len(plain_w) == len(ansi_w)
    assert max_len_w <= 10
