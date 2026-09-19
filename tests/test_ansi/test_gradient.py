from xulbux.ansi import (
    S,
    _color_obj_to_rgb,
    _GradientStyle,
    _rgb_to_ansi256,
    is_any_style,
    is_base_style,
    is_bg_color_style,
    is_color_style,
    is_fg_color_style,
)
from xulbux.color import hexa, hsla, rgba
import pytest


def test_gradient_creation_and_properties() -> None:
    fg_grad = S.gradient("#ff0000", "#0000ff")
    assert isinstance(fg_grad, _GradientStyle)
    assert fg_grad._bg is False
    assert is_base_style(fg_grad) is True
    assert is_color_style(fg_grad) is False
    assert is_fg_color_style(fg_grad) is False
    assert is_bg_color_style(fg_grad) is False
    assert is_any_style(fg_grad) is True

    bg_grad = S.BG.gradient("#ff0000", "#0000ff")
    assert isinstance(bg_grad, _GradientStyle)
    assert bg_grad._bg is True
    assert is_bg_color_style(bg_grad) is False
    assert is_fg_color_style(bg_grad) is False

    # `as_fg` and `as_bg`:
    assert fg_grad.as_fg() == fg_grad
    assert fg_grad.as_bg()._bg is True
    assert bg_grad.as_bg() == bg_grad
    assert bg_grad.as_fg()._bg is False

    fg_explicit = S.gradient("#ff0000", "#0000ff", skip_whitespace=False)
    assert fg_explicit.as_bg() == bg_grad
    assert bg_grad.as_fg() == fg_explicit

    # Equality and hashing:
    same_grad = S.gradient("#ff0000", "#0000ff")
    diff_grad = S.gradient("#00ff00", "#0000ff")
    assert fg_grad == same_grad
    assert fg_grad != diff_grad
    assert fg_grad != bg_grad
    assert fg_grad != "not_a_gradient"
    assert hash(fg_grad) == hash(same_grad)


def test_gradient_empty_and_single_char() -> None:
    grad = S.gradient("#ff0000", "#0000ff", color_depth="truecolor")

    empty_res = grad("")
    assert isinstance(empty_res, S)
    assert empty_res.raw == ""
    assert empty_res.ansi == ""

    single_char = grad("A")
    assert single_char.raw == "A"
    assert "\x1b[38;2;255;0;0mA\x1b[39m" in single_char.ansi


def test_gradient_char_granularity() -> None:
    grad = S.gradient("#ff0000", "#0000ff", angle=0.0, color_depth="truecolor")
    styled_text = grad("AB")
    assert styled_text.raw == "AB"
    # First char should be red (255, 0, 0), second char blue (0, 0, 255):
    assert "\x1b[38;2;255;0;0mA" in styled_text.ansi
    assert "\x1b[38;2;0;0;255mB" in styled_text.ansi

    # Background gradient:
    bg_grad = S.BG.gradient("#ff0000", "#0000ff", angle=0.0, color_depth="truecolor")
    bg_styled = bg_grad("AB")
    assert "\x1b[48;2;255;0;0mA" in bg_styled.ansi
    assert "\x1b[48;2;0;0;255mB" in bg_styled.ansi


def test_gradient_word_granularity() -> None:
    grad = S.gradient("#ff0000", "#0000ff", granularity="word", angle=0.0, color_depth="truecolor")
    styled_text = grad("A B")
    assert styled_text.raw == "A B"
    # Word 1 is at 0 (start color), Word 2 is at 2 (end color), and space in between:
    assert "\x1b[38;2;255;0;0mA\x1b[39m" in styled_text.ansi
    assert " " in styled_text.ansi
    assert "\x1b[38;2;0;0;255mB\x1b[39m" in styled_text.ansi


def test_gradient_line_granularity() -> None:
    grad = S.gradient("#ff0000", "#0000ff", granularity="line", angle=90.0, color_depth="truecolor")
    multiline_text = "Line One\nLine Two"
    styled_text = grad(multiline_text)
    assert styled_text.raw == multiline_text
    lines = styled_text.ansi.split("\n")
    assert len(lines) == 2
    assert lines[0].startswith("\x1b[38;2;255;0;0mLine One\x1b[39m")
    assert lines[1].startswith("\x1b[38;2;0;0;255mLine Two\x1b[39m")


def test_gradient_angles_and_2d() -> None:
    # 90 degrees; vertical top-to-bottom:
    grad_90 = S.gradient("#ff0000", "#0000ff", angle=90.0, color_depth="truecolor")
    styled_text = grad_90("A\nB")
    assert styled_text.raw == "A\nB"
    lines = styled_text.ansi.split("\n")
    assert "\x1b[38;2;255;0;0mA" in lines[0]
    assert "\x1b[38;2;0;0;255mB" in lines[1]

    # 135 degrees diagonal:
    grad_diag = S.gradient("#ff0000", "#0000ff", angle=135.0, color_depth="truecolor")
    styled_diag = grad_diag("AB\nCD")
    assert styled_diag.raw == "AB\nCD"


def test_gradient_skip_whitespace() -> None:
    # `skip_whitespace=True` (default); spaces should not get colored codes:
    grad_skip = S.gradient("#ff0000", "#0000ff", skip_whitespace=True, color_depth="truecolor")
    styled_skip = grad_skip("A B")
    assert styled_skip.raw == "A B"
    assert styled_skip.ansi == "\x1b[38;2;255;0;0mA\x1b[39m \x1b[38;2;0;0;255mB\x1b[39m"

    # `skip_whitespace=False`; spaces should have color codes:
    grad_keep = S.gradient("#ff0000", "#0000ff", skip_whitespace=False, color_depth="truecolor")
    styled_keep = grad_keep("A B")
    assert styled_keep.raw == "A B"
    assert styled_keep.ansi.startswith("\x1b[38;2;255;0;0mA")
    assert styled_keep.ansi.endswith("B\x1b[39m")
    assert " \x1b[39m" not in styled_keep.ansi
    assert "\x1b[39m " not in styled_keep.ansi


def test_gradient_color_depth_256() -> None:
    grad_256 = S.gradient("#ff0000", "#0000ff", color_depth="256")
    styled_256 = grad_256("AB")
    assert "\x1b[38;5;" in styled_256.ansi

    bg_grad_256 = S.BG.gradient("#ff0000", "#0000ff", color_depth="256")
    bg_styled_256 = bg_grad_256("AB")
    assert "\x1b[48;5;" in bg_styled_256.ansi


def test_gradient_color_depth_auto(monkeypatch: pytest.MonkeyPatch) -> None:
    grad_auto = S.gradient("#ff0000", "#0000ff", color_depth="auto")
    styled_auto = grad_auto("AB")
    assert isinstance(styled_auto, S)
    assert styled_auto.raw == "AB"

    # [1] On Unix without COLORTERM, auto falls back to 256 colors:
    monkeypatch.setattr("sys.platform", "linux")
    monkeypatch.delenv("COLORTERM", raising=False)
    styled_256 = grad_auto("AB")
    assert "\x1b[38;5;" in styled_256.ansi

    # [2] On Unix with COLORTERM="truecolor" (or "24bit"), auto uses 24-bit truecolor:
    monkeypatch.setenv("COLORTERM", "truecolor")
    styled_truecolor = grad_auto("AB")
    assert "\x1b[38;2;" in styled_truecolor.ansi

    # [3] On Windows, auto uses 24-bit truecolor:
    monkeypatch.setattr("sys.platform", "win32")
    monkeypatch.delenv("COLORTERM", raising=False)
    styled_win = grad_auto("AB")
    assert "\x1b[38;2;" in styled_win.ansi


def test_gradient_color_inputs_and_stops() -> None:
    # Various color types; tuple, rgba, hexa, hsla:
    stops = [
        (rgba(255, 0, 0), 0.0),
        (hsla(120, 100, 50), 0.5),
        (hexa("#0000ff"), 1.0),
    ]
    grad_stops = S.gradient(stops, angle=0.0, color_depth="truecolor")
    styled_stops = grad_stops("ABC")
    assert styled_stops.raw == "ABC"
    assert "\x1b[38;2;255;0;0mA" in styled_stops.ansi
    assert "\x1b[38;2;0;255;0mB" in styled_stops.ansi
    assert "\x1b[38;2;0;0;255mC" in styled_stops.ansi

    # Single stop gradient:
    single_stop_grad = S.gradient("#ff0000", color_depth="truecolor")
    styled_single = single_stop_grad("Hello")
    assert "\x1b[38;2;255;0;0mH" in styled_single.ansi


def test_gradient_composition_and_operators() -> None:
    grad = S.gradient("#ff0000", "#0000ff")
    combined = S.BOLD | grad
    styled_text = combined("Hello")
    assert isinstance(styled_text, S)
    assert styled_text.raw == "Hello"
    assert "\x1b[1m" in styled_text.ansi
    assert styled_text.ansi.endswith("\x1b[22m")

    # Reverse composition order:
    combined_rev = grad | S.UNDERLINE
    styled_rev = combined_rev("Hello")
    assert "\x1b[4m" in styled_rev.ansi

    # Matmul operator:
    matmul_res = grad("Hello")
    assert isinstance(matmul_res, S)
    assert matmul_res.raw == "Hello"


def test_gradient_with_existing_ansi() -> None:
    grad = S.gradient("#ff0000", "#0000ff", angle=0.0, color_depth="truecolor")
    input_text = f"{S.BOLD('A')}B"
    styled_text = grad(input_text)
    assert styled_text.raw == "AB"
    assert "\x1b[1m" in styled_text.ansi


def test_gradient_validation_errors() -> None:
    with pytest.raises(ValueError, match="At least one color"):
        S.gradient()

    with pytest.raises(ValueError, match="Invalid granularity"):
        S.gradient("#ff0000", "#0000ff", granularity="character")  # type:ignore[arg-type]  # pyright:ignore[reportArgumentType]

    with pytest.raises(ValueError, match="Invalid color_depth"):
        S.gradient("#ff0000", "#0000ff", color_depth="16")  # type:ignore[arg-type]  # pyright:ignore[reportArgumentType]

    with pytest.raises(ValueError, match="parameter must be positive"):
        S.gradient("#ff0000", "#0000ff", cell_aspect_ratio=0.0)

    with pytest.raises(ValueError, match="Invalid gradient space"):
        S.gradient("#ff0000", "#0000ff", space="cmyk")  # type:ignore[arg-type]  # pyright:ignore[reportArgumentType]

    with pytest.raises(ValueError, match="Invalid gradient space"):
        S.BG.gradient("#ff0000", "#0000ff", space="cmyk")  # type:ignore[arg-type]  # pyright:ignore[reportArgumentType]

    with pytest.raises(ValueError, match="Invalid granularity"):
        S.BG.gradient("#ff0000", "#0000ff", granularity="bad")  # type:ignore[arg-type]  # pyright:ignore[reportArgumentType]

    with pytest.raises(ValueError, match="Invalid color_depth"):
        S.BG.gradient("#ff0000", "#0000ff", color_depth="bad")  # type:ignore[arg-type]  # pyright:ignore[reportArgumentType]

    with pytest.raises(ValueError, match="parameter must be positive"):
        S.BG.gradient("#ff0000", "#0000ff", cell_aspect_ratio=-1.0)


def test_gradient_color_resolution_and_styles() -> None:
    # `_ColorStyle` and `_Color256Style`:
    grad_color_styles = S.gradient(S.hex("#ff0000"), S.color256(21))
    assert isinstance(grad_color_styles("A"), S)

    # `_Style` instances (standard foreground, background, bright background):
    grad_ansi_styles = S.gradient(S.RED, S.BG.BLUE, S.BG.BR.GREEN)
    assert isinstance(grad_ansi_styles("A"), S)

    # Int hex and out-of-bounds error:
    grad_int_hex = S.gradient(0xFF0000, 0x0000FF)
    assert isinstance(grad_int_hex("A"), S)
    with pytest.raises(ValueError, match="Expected 24-bit hex integer"):
        S.gradient(-1, 0xFF0000)

    # String variations; 0x prefix, 3-digit hex, rgb() format:
    grad_str_variations = S.gradient("0xFF0000", "#0F0", "rgb(0, 0, 255)")
    assert isinstance(grad_str_variations("A"), S)

    # 4-element tuple:
    grad_tuple = S.gradient((255, 0, 0, 1.0), (0, 0, 255, 1.0))
    assert isinstance(grad_tuple("A"), S)

    # Explicit stops requiring clamping at ends (stops[0] > 0.0, stops[-1] < 1.0):
    grad_clamped_stops = S.gradient([("#ff0000", 0.2), ("#0000ff", 0.8)])
    assert isinstance(grad_clamped_stops("ABC"), S)


def test_gradient_additional_branches_and_operators() -> None:
    grad = S.gradient("#ff0000", "#0000ff")

    # Combining with `_StyleGroup`:
    group_one = grad | (S.BOLD | S.ITALIC)
    assert isinstance(group_one("A"), S)
    group_two = (S.BOLD | S.ITALIC) | grad
    assert isinstance(group_two("A"), S)

    # Comparison with non-`_SBase` and non-str:
    assert (grad == 42) is False

    # Line gradient with empty lines:
    line_grad = S.gradient("#ff0000", "#0000ff", granularity="line")
    styled_lines = line_grad("Line1\n\nLine2")
    assert styled_lines.raw == "Line1\n\nLine2"

    # Word gradient with ANSI token inside word:
    word_grad = S.gradient("#ff0000", "#0000ff", granularity="word")
    styled_word_ansi = word_grad(f"{S.BOLD('Hello')} World")
    assert styled_word_ansi.raw == "Hello World"

    # Word gradient with `skip_whitespace=False`:
    word_grad_no_skip = S.gradient("#ff0000", "#0000ff", granularity="word", skip_whitespace=False)
    styled_word_no_skip = word_grad_no_skip("Hello World")
    assert styled_word_no_skip.raw == "Hello World"

    # Text containing only whitespace/newlines (max_width < 1):
    styled_newlines = grad("\n\n")
    assert styled_newlines.raw == "\n\n"


def test_rgb_to_ansi256_mapping() -> None:
    # Grayscale extremes:
    assert _rgb_to_ansi256(1, 1, 1) == 16
    assert _rgb_to_ansi256(250, 250, 250) == 231
    assert _rgb_to_ansi256(128, 128, 128) == 244

    # Cube index coverage:
    assert 16 <= _rgb_to_ansi256(100, 140, 180) <= 231
    assert 16 <= _rgb_to_ansi256(220, 250, 40) <= 231

    # Style fallback for non-color `_Style`:
    assert _color_obj_to_rgb(S.BOLD) == (255, 255, 255)


def test_gradient_remaining_branches() -> None:
    # Unwrapping stops:

    # [1] Single RGB tuple:
    single_tuple_grad = S.gradient((255, 0, 0))
    assert isinstance(single_tuple_grad("A"), S)

    # [2] Single list of 3 strings (len 3, but not ints):
    list_str_grad = S.gradient(["#ff0000", "#00ff00", "#0000ff"])
    assert isinstance(list_str_grad("ABC"), S)

    # [3] Single list of tuples:
    list_tuple_grad = S.gradient([("#ff0000", 0.0), ("#0000ff", 1.0)])
    assert isinstance(list_tuple_grad("AB"), S)

    # `__ror__` direct call:
    grad = S.gradient("#ff0000", "#0000ff")
    result_ror = grad.__ror__(S.BOLD)
    assert isinstance(result_ror("A"), S)

    # Word gradient with line starting with space:
    word_grad = S.gradient("#ff0000", "#0000ff", granularity="word")
    styled_leading_space = word_grad("  hello")
    assert styled_leading_space.raw == "  hello"

    # Word gradient with line containing only spaces:
    styled_only_spaces = word_grad("   ")
    assert styled_only_spaces.raw == "   "

    # Word gradient with uniform color (color_seq == current_color):
    uniform_word_grad = S.gradient("#ff0000", granularity="word", skip_whitespace=False)
    styled_uniform = uniform_word_grad("A B")
    assert styled_uniform.raw == "A B"

    # Word gradient with uniform color and `skip_whitespace=True`:
    uniform_word_skip = S.gradient("#ff0000", granularity="word", skip_whitespace=True)
    styled_uniform_skip = uniform_word_skip("A B")
    assert styled_uniform_skip.raw == "A B"

    # Char gradient with line starting with space:
    styled_char_leading = grad("  AB")
    assert styled_char_leading.raw == "  AB"

    # Char gradient with line containing only spaces:
    styled_char_spaces = grad("   ")
    assert styled_char_spaces.raw == "   "

    # Char gradient with uniform color (color_seq == current_color):
    uniform_char_grad = S.gradient("#ff0000")
    styled_uniform_char = uniform_char_grad("AA")
    assert styled_uniform_char.raw == "AA"
