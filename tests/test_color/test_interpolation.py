import math
from typing import Any, cast
import xulbux.color as _color_module
from xulbux.color import hexa, hsla, rgba
import pytest


def test_interpolate_color_rgb() -> None:
    red_color = rgba(255, 0, 0)
    blue_color = rgba(0, 0, 255)

    start_res = _color_module.interpolate_color(red_color, blue_color, ratio=0.0, space="rgb")
    assert start_res.red == 255
    assert start_res.green == 0
    assert start_res.blue == 0
    assert start_res.alpha is None

    end_res = _color_module.interpolate_color(red_color, blue_color, ratio=1.0, space="rgb")
    assert end_res.red == 0
    assert end_res.green == 0
    assert end_res.blue == 255

    mid_res = _color_module.interpolate_color(red_color, blue_color, ratio=0.5, space="rgb")
    assert mid_res.red == 128
    assert mid_res.green == 0
    assert mid_res.blue == 128


def test_interpolate_color_clamping() -> None:
    red_color = rgba(255, 0, 0)
    blue_color = rgba(0, 0, 255)

    below_res = _color_module.interpolate_color(red_color, blue_color, ratio=-0.5, space="rgb")
    assert below_res.red == 255
    assert below_res.blue == 0

    above_res = _color_module.interpolate_color(red_color, blue_color, ratio=1.5, space="rgb")
    assert above_res.red == 0
    assert above_res.blue == 255


def test_interpolate_color_linear_rgb() -> None:
    black_color = rgba(0, 0, 0)
    white_color = rgba(255, 255, 255)

    mid_res = _color_module.interpolate_color(black_color, white_color, ratio=0.5, space="linear_rgb")
    # In sRGB space, 50% linear intensity is around 188
    assert 185 <= mid_res.red <= 190
    assert 185 <= mid_res.green <= 190
    assert 185 <= mid_res.blue <= 190


def test_interpolate_color_hsl() -> None:
    # Red (hue 0) to Green (hue 120)
    color_one = rgba(255, 0, 0)
    color_two = rgba(0, 255, 0)

    mid_hsl = _color_module.interpolate_color(color_one, color_two, ratio=0.5, space="hsl")
    # Hue 60 is yellow: red 255, green 255, blue 0
    assert mid_hsl.red > 200
    assert mid_hsl.green > 200
    assert mid_hsl.blue < 50

    # Short path across wrap-around: 350 deg to 10 deg (diff is 20 deg across 0)
    color_wrap_start = hsla(350, 100, 50)
    color_wrap_end = hsla(10, 100, 50)
    mid_wrap = _color_module.interpolate_color(color_wrap_start, color_wrap_end, ratio=0.5, space="hsl")
    # Midpoint should be hue 0 (pure red)
    assert mid_wrap.red == 255
    assert mid_wrap.green == 0
    assert mid_wrap.blue == 0

    # Reverse direction short path: 10 deg to 350 deg
    mid_wrap_rev = _color_module.interpolate_color(color_wrap_end, color_wrap_start, ratio=0.5, space="hsl")
    assert mid_wrap_rev.red == 255
    assert mid_wrap_rev.green == 0
    assert mid_wrap_rev.blue == 0

    # Test identical hues:
    same_hue_one = hsla(180, 50, 50)
    same_hue_two = hsla(180, 100, 50)
    mid_same = _color_module.interpolate_color(same_hue_one, same_hue_two, ratio=0.5, space="hsl")
    assert mid_same.red < 50

    # Test achromatic colors (saturation 0):
    gray_color = rgba(128, 128, 128)
    mid_gray = _color_module.interpolate_color(gray_color, color_one, ratio=0.5, space="hsl")
    assert isinstance(mid_gray, rgba)


def test_interpolate_color_hsl_long() -> None:
    # Long path: 350 deg to 10 deg should go the long way around (through 180 deg cyan)
    color_wrap_start = hsla(350, 100, 50)
    color_wrap_end = hsla(10, 100, 50)

    mid_long = _color_module.interpolate_color(color_wrap_start, color_wrap_end, ratio=0.5, space="hsl_long")
    # Midpoint of 350 -> 10 long way: (350 + 10 + 360)/2 = 360 -> 180 deg (Cyan: red 0, green 255, blue 255)
    assert mid_long.red == 0
    assert mid_long.green == 255
    assert mid_long.blue == 255

    # Reverse direction long path:
    mid_long_rev = _color_module.interpolate_color(color_wrap_end, color_wrap_start, ratio=0.5, space="hsl_long")
    assert mid_long_rev.red == 0
    assert mid_long_rev.green == 255
    assert mid_long_rev.blue == 255

    # Test when diff is small (< 180) in standard order: 10 to 50 long way
    mid_small_diff = _color_module.interpolate_color(hsla(10, 100, 50), hsla(50, 100, 50), ratio=0.5, space="hsl_long")
    assert isinstance(mid_small_diff, rgba)


def test_interpolate_color_oklab() -> None:
    blue_color = rgba(0, 0, 255)
    yellow_color = rgba(255, 255, 0)

    mid_oklab = _color_module.interpolate_color(blue_color, yellow_color, ratio=0.5, space="oklab")
    assert isinstance(mid_oklab, rgba)
    assert 0 <= mid_oklab.red <= 255
    assert 0 <= mid_oklab.green <= 255
    assert 0 <= mid_oklab.blue <= 255


def test_interpolate_color_alpha_handling() -> None:
    # Both have alpha:
    color_alpha_start = rgba(255, 0, 0, 0.2)
    color_alpha_end = rgba(0, 0, 255, 0.8)
    mid_res = _color_module.interpolate_color(color_alpha_start, color_alpha_end, ratio=0.5)
    assert mid_res.alpha is not None
    assert math.isclose(mid_res.alpha, 0.5, abs_tol=1e-3)

    # Start has alpha, end does not (defaults to 1.0):
    mid_res_start_alpha = _color_module.interpolate_color(color_alpha_start, rgba(0, 0, 255), ratio=0.5)
    assert mid_res_start_alpha.alpha is not None
    assert math.isclose(mid_res_start_alpha.alpha, 0.6, abs_tol=1e-3)

    # End has alpha, start does not:
    mid_res_end_alpha = _color_module.interpolate_color(rgba(255, 0, 0), color_alpha_end, ratio=0.5)
    assert mid_res_end_alpha.alpha is not None
    assert math.isclose(mid_res_end_alpha.alpha, 0.9, abs_tol=1e-3)

    # Neither has alpha:
    mid_no_alpha = _color_module.interpolate_color(rgba(255, 0, 0), rgba(0, 0, 255), ratio=0.5)
    assert mid_no_alpha.alpha is None


def test_interpolate_color_input_types() -> None:
    # Hex string, tuple, hexa object, hsla object
    res_one = _color_module.interpolate_color("#ff0000", "#0000ff", ratio=0.5, space="rgb")
    assert res_one.red == 128
    assert res_one.blue == 128

    res_two = _color_module.interpolate_color((255, 0, 0), (0, 0, 255), ratio=0.5, space="rgb")
    assert res_two.red == 128
    assert res_two.blue == 128

    res_three = _color_module.interpolate_color(hexa("#ff0000"), hexa("#0000ff"), ratio=0.5, space="rgb")
    assert res_three.red == 128
    assert res_three.blue == 128


def test_interpolate_color_errors() -> None:
    with pytest.raises(ValueError, match="Unsupported color space"):
        _color_module.interpolate_color(rgba(255, 0, 0), rgba(0, 0, 255), ratio=0.5, space="invalid_space")  # type:ignore[arg-type]  # pyright:ignore[reportArgumentType]

    with pytest.raises(ValueError):
        _color_module.interpolate_color("invalid_color_1", rgba(0, 0, 255), ratio=0.5)

    with pytest.raises(ValueError):
        _color_module.interpolate_color(rgba(255, 0, 0), "invalid_color_2", ratio=0.5)


def test_create_gradient_basic() -> None:
    gradient_colors = _color_module.create_gradient(["#ff0000", "#0000ff"], steps=3, space="rgb")
    assert len(gradient_colors) == 3
    assert gradient_colors[0].red == 255
    assert gradient_colors[0].blue == 0
    assert gradient_colors[1].red == 128
    assert gradient_colors[1].blue == 128
    assert gradient_colors[2].red == 0
    assert gradient_colors[2].blue == 255


def test_create_gradient_single_step() -> None:
    single_res = _color_module.create_gradient(["#ff0000", "#0000ff"], steps=1)
    assert len(single_res) == 1
    assert single_res[0].red == 255
    assert single_res[0].blue == 0


def test_create_gradient_custom_stops() -> None:
    # Stops with explicit positions:
    # 0.0 -> Red, 0.5 -> Green, 1.0 -> Blue
    stops = [("#ff0000", 0.0), ("#00ff00", 0.5), ("#0000ff", 1.0)]
    gradient_colors = _color_module.create_gradient(stops, steps=5, space="rgb")
    assert len(gradient_colors) == 5
    # steps=5: t = 0.0, 0.25, 0.5, 0.75, 1.0
    assert gradient_colors[0].red == 255  # t=0.0
    assert gradient_colors[2].green == 255  # t=0.5
    assert gradient_colors[4].blue == 255  # t=1.0

    # Stops not starting at 0 or ending at 1:
    partial_stops = [("#ff0000", 0.3), ("#0000ff", 0.7)]
    partial_gradient = _color_module.create_gradient(partial_stops, steps=5, space="rgb")
    # t=0.0 and t=0.25 should be clamped to red (#ff0000)
    assert partial_gradient[0].red == 255
    assert partial_gradient[0].blue == 0
    # t=0.75 and t=1.0 should be clamped to blue (#0000ff)
    assert partial_gradient[4].red == 0
    assert partial_gradient[4].blue == 255

    # Stops out of order:
    unordered_stops = [("#0000ff", 1.0), ("#ff0000", 0.0)]
    ordered_res = _color_module.create_gradient(unordered_stops, steps=2)
    assert ordered_res[0].red == 255
    assert ordered_res[1].blue == 255


def test_create_gradient_errors() -> None:
    with pytest.raises(ValueError, match="parameter must be an integer >= 1"):
        _color_module.create_gradient(["#ff0000", "#0000ff"], steps=0)

    with pytest.raises(ValueError, match="At least one color stop"):
        _color_module.create_gradient([], steps=5)

    with pytest.raises(ValueError, match="Unsupported color space"):
        _color_module.create_gradient(["#ff0000", "#0000ff"], steps=3, space=cast("Any", "unknown"))


def test_interpolation_edge_cases_and_branches() -> None:
    # First chromatic, second achromatic:
    mid_achromatic = _color_module.interpolate_color(rgba(255, 0, 0), rgba(128, 128, 128), ratio=0.5, space="hsl")
    assert isinstance(mid_achromatic, rgba)

    # Negative delta_hue in hsl_long (-180 < delta_hue <= 0):
    mid_neg_delta = _color_module.interpolate_color(hsla(200, 100, 50), hsla(100, 100, 50), ratio=0.5, space="hsl_long")
    assert isinstance(mid_neg_delta, rgba)

    # Empty stops in internal helpers:
    assert _color_module._resolve_color_stop((), 0.5) == (0, 0, 0)
    assert _color_module._resolve_color_stop_with_alpha((), 0.5) == ((0, 0, 0), None)

    # _calculate_gradient:
    test_stops = (((255, 0, 0), 0.0), ((0, 0, 255), 1.0))
    assert _color_module._calculate_gradient(test_stops, steps=1) == ((255, 0, 0),)
    calc_res = _color_module._calculate_gradient(test_stops, steps=3)
    assert len(calc_res) == 3
    assert calc_res[0] == (255, 0, 0)
    assert calc_res[2] == (0, 0, 255)

    # Single stop gradient in create_gradient:
    single_res = _color_module.create_gradient(["#ff0000"], steps=3)
    assert len(single_res) == 3
    assert single_res[0].red == 255
    assert single_res[1].red == 255
    assert single_res[2].red == 255

    # Alpha gradient in create_gradient:
    alpha_grad = _color_module.create_gradient([rgba(255, 0, 0, 0.2), rgba(0, 0, 255, 0.8)], steps=3)
    assert len(alpha_grad) == 3
    assert alpha_grad[0].alpha is not None
    assert alpha_grad[1].alpha is not None
    assert alpha_grad[2].alpha is not None

    # Mixed alpha gradient (first two stops opaque, third has alpha):
    mixed_alpha_grad = _color_module.create_gradient(
        [rgba(255, 0, 0), rgba(0, 255, 0), rgba(0, 0, 255, 0.5)],
        steps=5,
    )
    assert len(mixed_alpha_grad) == 5
    assert mixed_alpha_grad[0].alpha is None
    assert mixed_alpha_grad[4].alpha == pytest.approx(0.5)

    # _extract_rgb_fast edge cases:
    # 1. 4-element numeric tuple:
    assert _color_module._extract_rgb_fast((255, 0, 0, 1.0)) == (255, 0, 0)
    with pytest.raises((ValueError, TypeError)):
        _color_module._extract_rgb_fast(cast("Any", (None, 0, 0)))
    # 2. Dict falling through to as_rgba:
    assert _color_module._extract_rgb_fast(cast("Any", {"red": 255, "green": 0, "blue": 0})) == (255, 0, 0)
    # 3. Invalid int hex:
    with pytest.raises(ValueError, match="Expected 24-bit hex integer"):
        _color_module._extract_rgb_fast(-1)
    with pytest.raises(ValueError, match="Expected 24-bit hex integer"):
        _color_module._extract_rgb_fast(0x1000000)

    # _extract_alpha_fast edge cases:
    assert _color_module._extract_alpha_fast((255, 0, 0, 0.5)) == pytest.approx(0.5)
    assert _color_module._extract_alpha_fast((255, 0, 0)) is None
    assert _color_module._extract_alpha_fast({"red": 255, "green": 0, "blue": 0, "alpha": 0.7}) == pytest.approx(0.7)
    assert _color_module._extract_alpha_fast({"red": 255, "green": 0, "blue": 0}) is None
    assert _color_module._extract_alpha_fast(0xFF0000) is None

    # _interpolate_color invalid space:
    with pytest.raises(ValueError, match="Unsupported color space"):
        _color_module._interpolate_color(255, 0, 0, 0, 0, 255, ratio=0.5, space=cast("Any", "invalid"))
