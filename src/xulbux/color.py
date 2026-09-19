"""
Provides color manipulation across RGBA, HSLA, and hex spaces.
<br>
Includes dedicated classes for each color model, conversions, parsing,
luminance calculation, color adjustments, and gradient generation.
"""

from __future__ import annotations

from . import regex as _regex_module
from .base.types import Hexa, HexaDict, Hsla, HslaDict, Rgba, RgbaDict, is_dict, is_seq
from .regex import LazyRegex

import math as _math
from typing import TYPE_CHECKING, Any, Final, Literal, TypeGuard, cast, overload

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence


_PATTERNS: Final[LazyRegex] = LazyRegex(
    rgba_allow_alpha=_regex_module.rgba_str(fix_sep=None, allow_alpha=True),
    rgba_no_alpha=_regex_module.rgba_str(fix_sep=None, allow_alpha=False),
    hsla_allow_alpha=_regex_module.hsla_str(fix_sep=None, allow_alpha=True),
    hsla_no_alpha=_regex_module.hsla_str(fix_sep=None, allow_alpha=False),
    hexa_allow_alpha=_regex_module.hexa_str(allow_alpha=True),
    hexa_no_alpha=_regex_module.hexa_str(allow_alpha=False),
)


_SRGB_LINEAR_LUT: tuple[float, ...] = tuple([
    ((ch / 255.0) / 12.92) if (ch / 255.0) <= 0.04045 else (((ch / 255.0) + 0.055) / 1.055) ** 2.4 for ch in range(256)
])
"""Lookup table mapping 8-bit sRGB channel values in range [0, 255] to linear RGB space values."""


class _ColorBase:
    """Internal base class providing common operator overloading and conversions for color models."""

    __slots__: tuple[str, ...] = ("alpha",)
    alpha: float | None

    def __len__(self) -> int:
        """The number of components in the color (3 or 4)."""

        return 3 if self.alpha is None else 4

    def has_alpha(self) -> bool:
        """Returns `True` if the color has an alpha channel and `False` otherwise."""

        return self.alpha is not None

    def is_opaque(self) -> bool:
        """Returns `True` if the color has no transparency."""

        return self.alpha == 1 or self.alpha is None


class rgba(_ColorBase):
    """An RGB/RGBA color object that includes a bunch of methods to manipulate the color.\n
    ----------------------------------------------------------------------------------------------------
    *   `red` – The red channel in range [0, 255] inclusive.
    *   `green` – The green channel in range [0, 255] inclusive.
    *   `blue` – The blue channel in range [0, 255] inclusive.
    *   `alpha` – The alpha channel in range [0.0, 1.0] inclusive
        or `None` if the color has no alpha channel.\n
    ----------------------------------------------------------------------------------------------------
    #### Example Usage

    ```python
    from xulbux import rgba

    color = rgba(30, 144, 255)  # Dodger Blue

    # Adjust color properties:
    lighter = color.lighten(0.2)
    darker = color.darken(0.15)
    blended = color.blend(rgba(255, 0, 0), ratio=0.5)

    # Convert to other color spaces:
    hex_str = color.as_hexa()  # #1E90FF
    hsl_obj = color.as_hsla()  # hsla(210°, 100%, 56%)
    ```"""

    __slots__: tuple[str, ...] = ("blue", "green", "red")

    def __init__(self, red: int, green: int, blue: int, alpha: float | None = None, /, *, _validate: bool = True) -> None:
        self.red: int
        """The red channel in range [0, 255] inclusive."""
        self.green: int
        """The green channel in range [0, 255] inclusive."""
        self.blue: int
        """The blue channel in range [0, 255] inclusive."""
        self.alpha: float | None
        """The alpha channel in range [0.0, 1.0] inclusive or `None` if not set."""

        if not _validate:
            self.red, self.green, self.blue, self.alpha = red, green, blue, alpha
            return

        elif not (0 <= red <= 255 and 0 <= green <= 255 and 0 <= blue <= 255):
            raise ValueError(
                "The 'red', 'green' and 'blue' parameters must be integers "
                f"in range [0, 255] inclusive, got {red=!r} {green=!r} {blue=!r}"
            )
        elif alpha is not None and not (0.0 <= alpha <= 1.0):
            raise ValueError(f"The 'alpha' parameter must be in range [0.0, 1.0] inclusive, got {alpha!r}")

        self.red, self.green, self.blue = red, green, blue
        self.alpha = None if alpha is None else float(alpha)

    def __iter__(self) -> Iterator[int | float]:
        yield self.red
        yield self.green
        yield self.blue

        if self.alpha is not None:
            yield self.alpha

    @overload
    def __getitem__(self, idx: Literal[0, 1, 2], /) -> int: ...
    @overload
    def __getitem__(self, idx: Literal[3], /) -> float: ...
    @overload
    def __getitem__(self, idx: int, /) -> int | float: ...

    def __getitem__(self, idx: int, /) -> int | float:
        if idx == 0 or (idx == -3 and self.alpha is None) or (idx == -4 and self.alpha is not None):
            return self.red
        elif idx == 1 or (idx == -2 and self.alpha is None) or (idx == -3 and self.alpha is not None):
            return self.green
        elif idx == 2 or (idx == -1 and self.alpha is None) or (idx == -2 and self.alpha is not None):
            return self.blue
        elif (idx == 3 or idx == -1) and self.alpha is not None:
            return self.alpha

        raise IndexError(f"{type(self).__name__!r} index {idx!r} out of range")

    def __eq__(self, other: object, /) -> bool:
        """Check if two `rgba` objects are the same color."""

        if not isinstance(other, rgba):
            return False
        return (self.red, self.green, self.blue, self.alpha) == (other.red, other.green, other.blue, other.alpha)

    def __repr__(self) -> str:
        return f"rgba({self.red}, {self.green}, {self.blue}{'' if self.alpha is None else f', {self.alpha}'})"

    def __str__(self) -> str:
        return self.__repr__()

    def as_tuple(self) -> tuple[int, int, int, float | None]:
        """Returns the color components as a tuple `(red, green, blue, alpha)`."""

        return self.red, self.green, self.blue, self.alpha

    def as_dict(self) -> RgbaDict:
        """Returns the color components as a dictionary with keys `"red"`, `"green"`, `"blue"` and optionally `"alpha"`."""

        if self.alpha is None:
            return RgbaDict(red=self.red, green=self.green, blue=self.blue)

        return RgbaDict(red=self.red, green=self.green, blue=self.blue, alpha=self.alpha)

    def as_rgba(self) -> rgba:
        """Returns the color as `rgba()` color object."""

        return self

    def as_hsla(self) -> hsla:
        """Returns the color as `hsla()` color object."""

        hue, sat, light = self._rgb_to_hsl(self.red, self.green, self.blue)
        return hsla(hue, sat, light, self.alpha, _validate=False)

    def as_hexa(self) -> hexa:
        """Returns the color as `hexa()` color object."""

        return hexa(_red=self.red, _green=self.green, _blue=self.blue, _alpha=self.alpha)

    def lighten(self, amount: float, /) -> rgba:
        """Increases the colors lightness by the specified amount in range [0.0, 1.0] inclusive."""

        if not (0.0 <= amount <= 1.0):
            raise ValueError(f"The 'amount' parameter must be in range [0.0, 1.0] inclusive, got {amount!r}")

        return self.as_hsla().lighten(amount).as_rgba()

    def darken(self, amount: float, /) -> rgba:
        """Decreases the colors lightness by the specified amount in range [0.0, 1.0] inclusive."""

        if not (0.0 <= amount <= 1.0):
            raise ValueError(f"The 'amount' parameter must be in range [0.0, 1.0] inclusive, got {amount!r}")

        return self.as_hsla().darken(amount).as_rgba()

    def saturate(self, amount: float, /) -> rgba:
        """Increases the colors saturation by the specified amount in range [0.0, 1.0] inclusive."""

        if not (0.0 <= amount <= 1.0):
            raise ValueError(f"The 'amount' parameter must be in range [0.0, 1.0] inclusive, got {amount!r}")

        return self.as_hsla().saturate(amount).as_rgba()

    def desaturate(self, amount: float, /) -> rgba:
        """Decreases the colors saturation by the specified amount in range [0.0, 1.0] inclusive."""

        if not (0.0 <= amount <= 1.0):
            raise ValueError(f"The 'amount' parameter must be in range [0.0, 1.0] inclusive, got {amount!r}")

        return self.as_hsla().desaturate(amount).as_rgba()

    def rotate(self, degrees: int, /) -> rgba:
        """Rotates the colors hue by the specified number of degrees."""

        return self.as_hsla().rotate(degrees).as_rgba()

    def invert(self, *, invert_alpha: bool = False) -> rgba:
        """Inverts the color by rotating hue by 180 degrees and inverting lightness."""

        alpha = (1.0 - self.alpha if self.alpha is not None else None) if invert_alpha else self.alpha
        return rgba(255 - self.red, 255 - self.green, 255 - self.blue, alpha, _validate=False)

    def grayscale(self, *, method: Literal["wcag2", "wcag3", "simple", "bt601"] = "wcag2") -> rgba:
        """Converts the color to grayscale using the luminance formula.\n
        ----------------------------------------------------------------------------------------------------
        *   `method` – The luminance calculation method to use:
            -   `"wcag2"` WCAG 2.0 standard (default and most accurate for perception)
            -   `"wcag3"` draft WCAG 3.0 standard with improved coefficients
            -   `"simple"` simple arithmetic mean (less accurate)
            -   `"bt601"` ITU-R BT.601 standard (older TV standard)"""

        # The `method` param is validated in `get_luminance()`.

        gray = int(get_luminance(self.red, self.green, self.blue, method=method))
        return rgba(gray, gray, gray, self.alpha, _validate=False)

    def blend(self, other: Rgba, /, ratio: float = 0.5, *, additive_alpha: bool = False) -> rgba:
        """Blends the current color with another color
        using the specified ratio in range [0.0, 1.0] inclusive.\n
        ----------------------------------------------------------------------------------------------------
        *   `other` – The other RGBA color to blend with.
        *   `ratio` – The blend ratio between the two colors:
            -   If `ratio` is `0.0` it means 100% of the current color
                and 0% of the `other` color (2:0 mixture).
            -   If `ratio` is `0.5` it means 50% of both colors (1:1 mixture).
            -   If `ratio` is `1.0` it means 0% of the current color
                and 100% of the `other` color (0:2 mixture).
        *   `additive_alpha` – Whether to blend the alpha channels additively or not."""

        if not is_valid_rgba(other, allow_strings=False):
            raise TypeError(f"The 'other' parameter must be a valid RGBA color, got {other!r}")
        elif not (0.0 <= ratio <= 1.0):
            raise ValueError(f"The 'ratio' parameter must be in range [0.0, 1.0] inclusive, got {ratio!r}")

        other_rgba = to_rgba(other)

        red = int(max(0, min(255, int((self.red * (1 - ratio)) + (other_rgba.red * ratio) + 0.5))))
        green = int(max(0, min(255, int((self.green * (1 - ratio)) + (other_rgba.green * ratio) + 0.5))))
        blue = int(max(0, min(255, int((self.blue * (1 - ratio)) + (other_rgba.blue * ratio) + 0.5))))
        none_alpha = self.alpha is None and other_rgba.alpha is None

        if not none_alpha:
            self_a: float = 1.0 if self.alpha is None else self.alpha
            other_a: float = 1.0 if other_rgba.alpha is None else other_rgba.alpha

            if additive_alpha:
                # Additive blend calculation
                ratio2 = ratio * 2
                alpha = max(0.0, min(1.0, (self_a * (2 - ratio2)) + (other_a * ratio2)))
            else:
                alpha = max(0.0, min(1.0, (self_a * (1 - ratio)) + (other_a * ratio)))

        else:
            alpha = None

        return rgba(red, green, blue, alpha, _validate=False)

    def is_dark(self) -> bool:
        """Returns `True` if the color is considered dark (`lightness < 50%`)."""

        return self.as_hsla().is_dark()

    def is_light(self) -> bool:
        """Returns `True` if the color is considered light (`lightness >= 50%`)."""

        return not self.is_dark()

    def is_grayscale(self) -> bool:
        """Returns `True` if the color is grayscale."""

        return self.red == self.green == self.blue

    def with_alpha(self, alpha: float | None, /) -> rgba:
        """Returns a new color with the specified alpha value, or `None` to clear alpha."""

        if alpha is not None and not (0.0 <= alpha <= 1.0):
            raise ValueError(f"The 'alpha' parameter must be in range [0.0, 1.0] inclusive or None, got {alpha!r}")

        return rgba(self.red, self.green, self.blue, alpha, _validate=False)

    def complementary(self) -> rgba:
        """Returns the complementary color (180 degrees on the color wheel)."""

        return self.as_hsla().complementary().as_rgba()

    @staticmethod
    def _rgb_to_hsl(red: int, green: int, blue: int) -> tuple[int, int, int]:
        """Internal method to convert RGB to HSL color space."""

        red_norm, green_norm, blue_norm = red / 255.0, green / 255.0, blue / 255.0
        max_c, min_c = max(red_norm, green_norm, blue_norm), min(red_norm, green_norm, blue_norm)
        light = (max_c + min_c) / 2

        if max_c == min_c:
            hue = sat = 0.0

        else:
            delta = max_c - min_c
            sat = delta / (1 - abs(2 * light - 1))

            if max_c == red_norm:
                hue = ((green_norm - blue_norm) / delta) % 6
            elif max_c == green_norm:
                hue = ((blue_norm - red_norm) / delta) + 2
            else:
                hue = ((red_norm - green_norm) / delta) + 4

            hue /= 6

        return round(hue * 360), round(sat * 100), round(light * 100)


class hsla(_ColorBase):
    """A HSL/HSLA color object that includes a bunch of methods to manipulate the color.\n
    ----------------------------------------------------------------------------------------------------
    *   `hue` – The hue channel in range [0, 360] inclusive.
    *   `sat` – The saturation channel in range [0, 100] inclusive.
    *   `light` – The lightness channel in range [0, 100] inclusive.
    *   `alpha` – The alpha channel in range [0.0, 1.0] inclusive
        or `None` if the color has no alpha channel.\n
    ----------------------------------------------------------------------------------------------------
    #### Example Usage

    ```python
    from xulbux import hsla

    color = hsla(210, 100, 56)  # Dodger Blue

    # Rotate hue and adjust saturation:
    complementary = color.complementary()  # hsla(30°, 100%, 56%)
    saturated = color.saturate(0.2)
    desaturated = color.desaturate(0.3)

    # Convert to other color spaces:
    rgb_obj = color.as_rgba()  # rgba(30, 144, 255)
    hex_obj = color.as_hexa()  # #1E90FF
    ```"""

    __slots__: tuple[str, ...] = ("hue", "light", "sat")

    def __init__(self, hue: int, sat: int, light: int, alpha: float | None = None, /, *, _validate: bool = True) -> None:
        self.hue: int
        """The hue channel in range [0, 360] inclusive."""
        self.sat: int
        """The saturation channel in range [0, 100] inclusive."""
        self.light: int
        """The lightness channel in range [0, 100] inclusive."""
        self.alpha: float | None
        """The alpha channel in range [0.0, 1.0] inclusive or `None` if not set."""

        if not _validate:
            self.hue, self.sat, self.light, self.alpha = hue, sat, light, alpha
            return

        elif not (0 <= hue <= 360):
            raise ValueError(f"The 'hue' parameter must be in range [0, 360] inclusive, got {hue!r}")
        elif not (0 <= sat <= 100 and 0 <= light <= 100):
            raise ValueError(f"The 'sat' and 'light' parameters must be in range [0, 100] inclusive, got {sat=!r} {light=!r}")
        elif alpha is not None and not (0.0 <= alpha <= 1.0):
            raise ValueError(f"The 'alpha' parameter must be in range [0.0, 1.0] inclusive, got {alpha!r}")

        self.hue, self.sat, self.light = hue, sat, light
        self.alpha = None if alpha is None else float(alpha)

    def __iter__(self) -> Iterator[int | float]:
        yield self.hue
        yield self.sat
        yield self.light

        if self.alpha is not None:
            yield self.alpha

    @overload
    def __getitem__(self, idx: Literal[0, 1, 2], /) -> int: ...
    @overload
    def __getitem__(self, idx: Literal[3], /) -> float: ...
    @overload
    def __getitem__(self, idx: int, /) -> int | float: ...

    def __getitem__(self, idx: int, /) -> int | float:
        if idx == 0 or (idx == -3 and self.alpha is None) or (idx == -4 and self.alpha is not None):
            return self.hue
        elif idx == 1 or (idx == -2 and self.alpha is None) or (idx == -3 and self.alpha is not None):
            return self.sat
        elif idx == 2 or (idx == -1 and self.alpha is None) or (idx == -2 and self.alpha is not None):
            return self.light
        elif (idx == 3 or idx == -1) and self.alpha is not None:
            return self.alpha

        raise IndexError(f"{type(self).__name__!r} index {idx!r} out of range")

    def __eq__(self, other: object, /) -> bool:
        """Check if two `hsla` objects are the same color."""

        if not isinstance(other, hsla):
            return False
        return (self.hue, self.sat, self.light, self.alpha) == (other.hue, other.sat, other.light, other.alpha)

    def __repr__(self) -> str:
        return f"hsla({self.hue}°, {self.sat}%, {self.light}%{'' if self.alpha is None else f', {self.alpha}'})"

    def __str__(self) -> str:
        return self.__repr__()

    def as_tuple(self) -> tuple[int, int, int, float | None]:
        """Returns the color components as a tuple `(hue, sat, light, alpha)`."""

        return self.hue, self.sat, self.light, self.alpha

    def as_dict(self) -> HslaDict:
        """Returns the color components as a dictionary with keys `"hue"`, `"sat"`, `"light"` and optionally `"alpha"`."""

        if self.alpha is None:
            return HslaDict(hue=self.hue, sat=self.sat, light=self.light)

        return HslaDict(hue=self.hue, sat=self.sat, light=self.light, alpha=self.alpha)

    def as_rgba(self) -> rgba:
        """Returns the color as `rgba()` color object."""

        red, green, blue = self._hsl_to_rgb(self.hue, self.sat, self.light)
        return rgba(red, green, blue, self.alpha, _validate=False)

    def as_hsla(self) -> hsla:
        """Returns the color as `hsla()` color object."""

        return self

    def as_hexa(self) -> hexa:
        """Returns the color as `hexa()` color object."""

        red, green, blue = self._hsl_to_rgb(self.hue, self.sat, self.light)
        return hexa(_red=red, _green=green, _blue=blue, _alpha=self.alpha)

    def lighten(self, amount: float, /) -> hsla:
        """Increases the colors lightness by the specified amount in range [0.0, 1.0] inclusive."""

        if not (0.0 <= amount <= 1.0):
            raise ValueError(f"The 'amount' parameter must be in range [0.0, 1.0] inclusive, got {amount!r}")

        return hsla(self.hue, self.sat, int(min(100, self.light + (100 - self.light) * amount)), self.alpha, _validate=False)

    def darken(self, amount: float, /) -> hsla:
        """Decreases the colors lightness by the specified amount in range [0.0, 1.0] inclusive."""

        if not (0.0 <= amount <= 1.0):
            raise ValueError(f"The 'amount' parameter must be in range [0.0, 1.0] inclusive, got {amount!r}")

        return hsla(self.hue, self.sat, int(max(0, self.light * (1 - amount))), self.alpha, _validate=False)

    def saturate(self, amount: float, /) -> hsla:
        """Increases the colors saturation by the specified amount in range [0.0, 1.0] inclusive."""

        if not (0.0 <= amount <= 1.0):
            raise ValueError(f"The 'amount' parameter must be in range [0.0, 1.0] inclusive, got {amount!r}")

        return hsla(self.hue, int(min(100, self.sat + (100 - self.sat) * amount)), self.light, self.alpha, _validate=False)

    def desaturate(self, amount: float, /) -> hsla:
        """Decreases the colors saturation by the specified amount in range [0.0, 1.0] inclusive."""

        if not (0.0 <= amount <= 1.0):
            raise ValueError(f"The 'amount' parameter must be in range [0.0, 1.0] inclusive, got {amount!r}")

        return hsla(self.hue, int(max(0, self.sat * (1 - amount))), self.light, self.alpha, _validate=False)

    def rotate(self, degrees: int, /) -> hsla:
        """Rotates the colors hue by the specified number of degrees."""

        return hsla((self.hue + degrees) % 360, self.sat, self.light, self.alpha, _validate=False)

    def invert(self, *, invert_alpha: bool = False) -> hsla:
        """Inverts the color by rotating hue by 180 degrees and inverting lightness."""

        alpha = (1.0 - self.alpha if self.alpha is not None else None) if invert_alpha else self.alpha
        return hsla((self.hue + 180) % 360, self.sat, 100 - self.light, alpha, _validate=False)

    def grayscale(self, *, method: Literal["wcag2", "wcag3", "simple", "bt601"] = "wcag2") -> hsla:
        """Converts the color to grayscale using the luminance formula.\n
        ----------------------------------------------------------------------------------------------------
        *   `method` – The luminance calculation method to use:
            -   `"wcag2"` WCAG 2.0 standard (default and most accurate for perception)
            -   `"wcag3"` draft WCAG 3.0 standard with improved coefficients
            -   `"simple"` simple arithmetic mean (less accurate)
            -   `"bt601"` ITU-R BT.601 standard (older TV standard)"""

        # The `method` param is validated in `get_luminance()`.

        red, green, blue = self._hsl_to_rgb(self.hue, self.sat, self.light)
        light = int(get_luminance(red, green, blue, output_type=None, method=method))
        hue, sat, light_val, _ = rgba(light, light, light, _validate=False).as_hsla().as_tuple()
        return hsla(hue, sat, light_val, self.alpha, _validate=False)

    def blend(self, other: Hsla, /, ratio: float = 0.5, *, additive_alpha: bool = False) -> hsla:
        """Blends the current color with another color
        using the specified ratio in range [0.0, 1.0] inclusive.\n
        ----------------------------------------------------------------------------------------------------
        *   `other` – The other HSLA color to blend with.
        *   `ratio` – The blend ratio between the two colors:
            -   If `ratio` is `0.0` it means 100% of the current color
                and 0% of the `other` color (2:0 mixture).
            -   If `ratio` is `0.5` it means 50% of both colors (1:1 mixture).
            -   If `ratio` is `1.0` it means 0% of the current color
                and 100% of the `other` color (0:2 mixture).
        *   `additive_alpha` – whether to blend the alpha channels additively or not."""

        if not is_valid_hsla(other, allow_strings=False):
            raise TypeError(f"The 'other' parameter must be a valid HSLA color, got {other!r}")
        elif not (0.0 <= ratio <= 1.0):
            raise ValueError(f"The 'ratio' parameter must be in range [0.0, 1.0] inclusive, got {ratio!r}")

        return self.as_rgba().blend(to_rgba(other), ratio, additive_alpha=additive_alpha).as_hsla()

    def is_dark(self) -> bool:
        """Returns `True` if the color is considered dark (`lightness < 50%`)."""

        return self.light < 50

    def is_light(self) -> bool:
        """Returns `True` if the color is considered light (`lightness >= 50%`)."""

        return not self.is_dark()

    def is_grayscale(self) -> bool:
        """Returns `True` if the color is considered grayscale."""

        return self.sat == 0

    def with_alpha(self, alpha: float | None, /) -> hsla:
        """Returns a new color with the specified alpha value, or `None` to clear alpha."""

        if alpha is not None and not (0.0 <= alpha <= 1.0):
            raise ValueError(f"The 'alpha' parameter must be in range [0.0, 1.0] inclusive or None, got {alpha!r}")

        return hsla(self.hue, self.sat, self.light, alpha, _validate=False)

    def complementary(self) -> hsla:
        """Returns the complementary color (180 degrees on the color wheel)."""

        return hsla((self.hue + 180) % 360, self.sat, self.light, self.alpha, _validate=False)

    @classmethod
    def _hsl_to_rgb(cls, hue: int, sat: int, light: int) -> tuple[int, int, int]:
        """Internal method to convert HSL to RGB color space."""

        hue_norm, sat_norm, light_norm = hue / 360, sat / 100, light / 100

        if sat_norm == 0:
            red = green = blue = int(light_norm * 255)

        else:
            chroma_max = light_norm * (1 + sat_norm) if light_norm < 0.5 else light_norm + sat_norm - light_norm * sat_norm
            chroma_min = 2 * light_norm - chroma_max

            red = round(cls._hue_to_rgb(chroma_min, chroma_max, hue_norm + 1 / 3) * 255)
            green = round(cls._hue_to_rgb(chroma_min, chroma_max, hue_norm) * 255)
            blue = round(cls._hue_to_rgb(chroma_min, chroma_max, hue_norm - 1 / 3) * 255)

        return red, green, blue

    @staticmethod
    def _hue_to_rgb(chroma_min: float, chroma_max: float, hue_pos: float) -> float:
        """Internal helper to convert a hue position to an RGB channel value."""

        if hue_pos < 0:
            hue_pos += 1
        if hue_pos > 1:
            hue_pos -= 1
        if hue_pos < 1 / 6:
            return chroma_min + (chroma_max - chroma_min) * 6 * hue_pos
        elif hue_pos < 1 / 2:
            return chroma_max
        elif hue_pos < 2 / 3:
            return chroma_min + (chroma_max - chroma_min) * (2 / 3 - hue_pos) * 6

        return chroma_min


class hexa(_ColorBase):
    """A hex color object that includes a bunch of methods to manipulate the color.\n
    ----------------------------------------------------------------------------------------------------
    *   `color` – The hex color string (prefix optional) or hex integer, that can be in formats:
        -   `RGB` short format without alpha (only for strings)
        -   `RGBA` short format with alpha (only for strings)
        -   `RRGGBB` long format without alpha (for strings and hex integers)
        -   `RRGGBBAA` long format with alpha (for strings and hex integers)\n
    ----------------------------------------------------------------------------------------------------
    #### Example Usage

    ```python
    from xulbux import hexa

    color = hexa("#1E90FF")  # Dodger Blue

    # Manipulate hex color:
    lighter = color.lighten(0.2)
    inverted = color.invert()

    # Convert to other representations:
    rgb_obj = color.as_rgba()  # rgba(30, 144, 255)
    hsl_obj = color.as_hsla()  # hsla(210°, 100%, 56%)
    ```"""

    __slots__: tuple[str, ...] = ("blue", "green", "red")

    def __init__(
        self,
        color: Hexa | None = None,
        /,
        *,
        _red: int | None = None,
        _green: int | None = None,
        _blue: int | None = None,
        _alpha: float | None = None,
    ) -> None:
        self.red: int
        """The red channel in range [0, 255] inclusive."""
        self.green: int
        """The green channel in range [0, 255] inclusive."""
        self.blue: int
        """The blue channel in range [0, 255] inclusive."""
        self.alpha: float | None
        """The alpha channel in range [0.0, 1.0] inclusive or `None` if not set."""

        if _red is not None and _green is not None and _blue is not None:
            self.red, self.green, self.blue, self.alpha = _red, _green, _blue, _alpha
            return

        elif isinstance(color, hexa):
            self.red, self.green, self.blue, self.alpha = color.red, color.green, color.blue, color.alpha

        elif isinstance(color, str):
            if color.startswith("#"):
                color = color[1:].upper()
            elif color.startswith("0x"):
                color = color[2:].upper()

            if len(color) == 3:  # RGB
                self.red, self.green, self.blue, self.alpha = (
                    int(color[0] * 2, 16),
                    int(color[1] * 2, 16),
                    int(color[2] * 2, 16),
                    None,
                )
            elif len(color) == 4:  # RGBA
                self.red, self.green, self.blue, self.alpha = (
                    int(color[0] * 2, 16),
                    int(color[1] * 2, 16),
                    int(color[2] * 2, 16),
                    int(color[3] * 2, 16) / 255.0,
                )
            elif len(color) == 6:  # RRGGBB
                self.red, self.green, self.blue, self.alpha = (
                    int(color[0:2], 16),
                    int(color[2:4], 16),
                    int(color[4:6], 16),
                    None,
                )
            elif len(color) == 8:  # RRGGBBAA
                self.red, self.green, self.blue, self.alpha = (
                    int(color[0:2], 16),
                    int(color[2:4], 16),
                    int(color[4:6], 16),
                    int(color[6:8], 16) / 255.0,
                )
            else:
                raise ValueError(f"Invalid hex color string {color!r}\nMust be in formats RGB, RGBA, RRGGBB or RRGGBBAA")

        elif isinstance(color, int):
            self.red, self.green, self.blue, self.alpha = hex_int_to_rgba(color).as_tuple()

        elif color is not None and hasattr(color, "red") and hasattr(color, "green") and hasattr(color, "blue"):
            self.red, self.green, self.blue, self.alpha = (
                int(color.red),
                int(color.green),
                int(color.blue),
                getattr(color, "alpha", None),
            )

        else:
            raise ValueError(
                f"Could not initialize hexa() color object from {color!r}\n"
                "Must be a hex string, hex integer, or an object with 'red', 'green', 'blue', and optionally 'alpha' attrs"
            )

    def __iter__(self) -> Iterator[str]:
        yield f"{self.red:02X}"
        yield f"{self.green:02X}"
        yield f"{self.blue:02X}"

        if self.alpha is not None:
            yield f"{int(self.alpha * 255):02X}"

    def __getitem__(self, idx: int, /) -> str:
        if idx == 0 or (idx == -3 and self.alpha is None) or (idx == -4 and self.alpha is not None):
            return f"{self.red:02X}"
        elif idx == 1 or (idx == -2 and self.alpha is None) or (idx == -3 and self.alpha is not None):
            return f"{self.green:02X}"
        elif idx == 2 or (idx == -1 and self.alpha is None) or (idx == -2 and self.alpha is not None):
            return f"{self.blue:02X}"
        elif (idx == 3 or idx == -1) and self.alpha is not None:
            return f"{int(self.alpha * 255):02X}"

        raise IndexError(f"{type(self).__name__!r} index {idx!r} out of range")

    def __eq__(self, other: object, /) -> bool:
        """Check if two `hexa` objects are the same color."""

        if not isinstance(other, hexa):
            return False
        return (self.red, self.green, self.blue, self.alpha) == (other.red, other.green, other.blue, other.alpha)

    def __repr__(self) -> str:
        alpha = "" if self.alpha is None else f"{int(self.alpha * 255):02X}"
        return f"hexa(#{self.red:02X}{self.green:02X}{self.blue:02X}{alpha})"

    def __str__(self) -> str:
        alpha = "" if self.alpha is None else f"{int(self.alpha * 255):02X}"
        return f"#{self.red:02X}{self.green:02X}{self.blue:02X}{alpha}"

    def as_tuple(self, *, round_alpha: bool = True) -> tuple[int, int, int, float | None]:
        """Returns the color components as a tuple `(red, green, blue, alpha)`."""

        return (
            self.red,
            self.green,
            self.blue,
            None if self.alpha is None else (round(self.alpha, 2) if round_alpha else self.alpha),
        )

    def as_dict(self) -> HexaDict:
        """Returns the color components as a dictionary with hex string values
        for keys `"red"`, `"green"`, `"blue"` and optionally `"alpha"`."""

        if self.alpha is None:
            return HexaDict(red=f"{self.red:02X}", green=f"{self.green:02X}", blue=f"{self.blue:02X}")

        return HexaDict(
            red=f"{self.red:02X}", green=f"{self.green:02X}", blue=f"{self.blue:02X}", alpha=f"{int(self.alpha * 255):02X}"
        )

    def as_rgba(self, *, round_alpha: bool = True) -> rgba:
        """Returns the color as `rgba()` color object."""

        return rgba(
            self.red,
            self.green,
            self.blue,
            None if self.alpha is None else (round(self.alpha, 2) if round_alpha else self.alpha),
            _validate=False,
        )

    def as_hsla(self, *, round_alpha: bool = True) -> hsla:
        """Returns the color as `hsla()` color object."""

        return self.as_rgba(round_alpha=round_alpha).as_hsla()

    def as_hexa(self) -> hexa:
        """Returns the color as `hexa()` color object."""

        return self

    def lighten(self, amount: float, /) -> hexa:
        """Increases the colors lightness by the specified amount in range [0.0, 1.0] inclusive."""

        if not (0.0 <= amount <= 1.0):
            raise ValueError(f"The 'amount' parameter must be in range [0.0, 1.0] inclusive, got {amount!r}")

        red, green, blue, alpha = self.as_rgba(round_alpha=False).lighten(amount).as_tuple()
        return hexa(_red=red, _green=green, _blue=blue, _alpha=alpha)

    def darken(self, amount: float, /) -> hexa:
        """Decreases the colors lightness by the specified amount in range [0.0, 1.0] inclusive."""

        if not (0.0 <= amount <= 1.0):
            raise ValueError(f"The 'amount' parameter must be in range [0.0, 1.0] inclusive, got {amount!r}")

        red, green, blue, alpha = self.as_rgba(round_alpha=False).darken(amount).as_tuple()
        return hexa(_red=red, _green=green, _blue=blue, _alpha=alpha)

    def saturate(self, amount: float, /) -> hexa:
        """Increases the colors saturation by the specified amount in range [0.0, 1.0] inclusive."""

        if not (0.0 <= amount <= 1.0):
            raise ValueError(f"The 'amount' parameter must be in range [0.0, 1.0] inclusive, got {amount!r}")

        red, green, blue, alpha = self.as_rgba(round_alpha=False).saturate(amount).as_tuple()
        return hexa(_red=red, _green=green, _blue=blue, _alpha=alpha)

    def desaturate(self, amount: float, /) -> hexa:
        """Decreases the colors saturation by the specified amount in range [0.0, 1.0] inclusive."""

        if not (0.0 <= amount <= 1.0):
            raise ValueError(f"The 'amount' parameter must be in range [0.0, 1.0] inclusive, got {amount!r}")

        red, green, blue, alpha = self.as_rgba(round_alpha=False).desaturate(amount).as_tuple()
        return hexa(_red=red, _green=green, _blue=blue, _alpha=alpha)

    def rotate(self, degrees: int, /) -> hexa:
        """Rotates the colors hue by the specified number of degrees."""

        red, green, blue, alpha = self.as_rgba(round_alpha=False).rotate(degrees).as_tuple()
        return hexa(_red=red, _green=green, _blue=blue, _alpha=alpha)

    def invert(self, *, invert_alpha: bool = False) -> hexa:
        """Inverts the color by rotating hue by 180 degrees and inverting lightness."""

        red, green, blue, alpha = self.as_rgba(round_alpha=False).invert(invert_alpha=invert_alpha).as_tuple()
        return hexa(_red=red, _green=green, _blue=blue, _alpha=alpha)

    def grayscale(self, *, method: Literal["wcag2", "wcag3", "simple", "bt601"] = "wcag2") -> hexa:
        """Converts the color to grayscale using the luminance formula.\n
        ----------------------------------------------------------------------------------------------------
        *   `method` – The luminance calculation method to use:
            -   `"wcag2"` WCAG 2.0 standard (default and most accurate for perception)
            -   `"wcag3"` draft WCAG 3.0 standard with improved coefficients
            -   `"simple"` simple arithmetic mean (less accurate)
            -   `"bt601"` ITU-R BT.601 standard (older TV standard)"""

        # The `method` param is validated in `get_luminance()`.

        gray = int(get_luminance(self.red, self.green, self.blue, method=method))
        return hexa(_red=gray, _green=gray, _blue=gray, _alpha=self.alpha)

    def blend(self, other: Hexa, /, ratio: float = 0.5, *, additive_alpha: bool = False) -> hexa:
        """Blends the current color with another color
        using the specified ratio in range [0.0, 1.0] inclusive.\n
        ----------------------------------------------------------------------------------------------------
        *   `other` – The other hex color to blend with.
        *   `ratio` – The blend ratio between the two colors:
            -   If `ratio` is `0.0` it means 100% of the current color
                and 0% of the `other` color (2:0 mixture).
            -   If `ratio` is `0.5` it means 50% of both colors (1:1 mixture).
            -   If `ratio` is `1.0` it means 0% of the current color
                and 100% of the `other` color (0:2 mixture).
        *   `additive_alpha` – Whether to blend the alpha channels additively or not."""

        if not is_valid_hexa(other):
            raise TypeError(f"The 'other' parameter must be a valid hex color, got {other!r}")
        elif not (0.0 <= ratio <= 1.0):
            raise ValueError(f"The 'ratio' parameter must be in range [0.0, 1.0] inclusive, got {ratio!r}")

        red, green, blue, alpha = (
            self.as_rgba(round_alpha=False).blend(to_rgba(other), ratio, additive_alpha=additive_alpha).as_tuple()
        )
        return hexa(_red=red, _green=green, _blue=blue, _alpha=alpha)

    def is_dark(self) -> bool:
        """Returns `True` if the color is considered dark (`lightness < 50%`)."""

        return self.as_hsla(round_alpha=False).is_dark()

    def is_light(self) -> bool:
        """Returns `True` if the color is considered light (`lightness >= 50%`)."""

        return not self.is_dark()

    def is_grayscale(self) -> bool:
        """Returns `True` if the color is grayscale (`saturation == 0`)."""

        return self.red == self.green == self.blue

    def with_alpha(self, alpha: float | None, /) -> hexa:
        """Returns a new color with the specified alpha value, or `None` to clear alpha."""

        if alpha is not None and not (0.0 <= alpha <= 1.0):
            raise ValueError(f"The 'alpha' parameter must be in range [0.0, 1.0] inclusive or None, got {alpha!r}")

        return hexa(_red=self.red, _green=self.green, _blue=self.blue, _alpha=alpha)

    def complementary(self) -> hexa:
        """Returns the complementary color (180 degrees on the color wheel)."""

        return self.as_hsla(round_alpha=False).complementary().as_hexa()


@overload
def is_valid_rgba(
    color: object,
    /,
    *,
    allow_alpha: bool = True,
    allow_strings: Literal[True] = True,
) -> TypeGuard[Rgba | str]: ...
@overload
def is_valid_rgba(
    color: object,
    /,
    *,
    allow_alpha: bool = True,
    allow_strings: Literal[False],
) -> TypeGuard[Rgba]: ...
@overload
def is_valid_rgba(
    color: object,
    /,
    *,
    allow_alpha: bool = True,
    allow_strings: bool = True,
) -> TypeGuard[Rgba | str] | TypeGuard[Rgba]: ...


def is_valid_rgba(
    color: object,
    /,
    *,
    allow_alpha: bool = True,
    allow_strings: bool = True,
) -> TypeGuard[Rgba | str] | TypeGuard[Rgba]:
    """Check if the given color is a valid RGBA color.\n
    ----------------------------------------------------------------------------------------------------
    *   `color` – The color to check (can be in any supported format).
    *   `allow_alpha` – Whether to allow alpha channel in the color.
    *   `allow_strings` – Whether to allow color strings."""

    if isinstance(color, rgba):
        return True

    elif is_seq(color):
        if (
            allow_alpha
            and len(color) == 4
            and (isinstance(color[0], int) and isinstance(color[1], int) and isinstance(color[2], int))
            and isinstance(color[3], float)
        ):
            return 0 <= color[0] <= 255 and 0 <= color[1] <= 255 and 0 <= color[2] <= 255 and 0.0 <= color[3] <= 1.0
        elif len(color) == 3 and (isinstance(color[0], int) and isinstance(color[1], int) and isinstance(color[2], int)):
            return 0 <= color[0] <= 255 and 0 <= color[1] <= 255 and 0 <= color[2] <= 255
        else:
            return False

    elif is_dict(color):
        if (
            allow_alpha
            and len(color) == 4
            and (
                isinstance(color.get("red"), int)
                and isinstance(color.get("green"), int)
                and isinstance(color.get("blue"), int)
            )
            and isinstance(color.get("alpha"), float)
        ):
            return (
                0 <= color["red"] <= 255
                and 0 <= color["green"] <= 255
                and 0 <= color["blue"] <= 255
                and 0.0 <= color["alpha"] <= 1.0
            )
        elif len(color) == 3 and (
            isinstance(color.get("red"), int) and isinstance(color.get("green"), int) and isinstance(color.get("blue"), int)
        ):
            return 0 <= color["red"] <= 255 and 0 <= color["green"] <= 255 and 0 <= color["blue"] <= 255
        else:
            return False

    elif allow_strings and isinstance(color, str):
        pattern = _PATTERNS.rgba_allow_alpha if allow_alpha else _PATTERNS.rgba_no_alpha
        return bool(pattern.fullmatch(color))

    return False


@overload
def is_valid_hsla(
    color: object,
    /,
    *,
    allow_alpha: bool = True,
    allow_strings: Literal[True] = True,
) -> TypeGuard[Hsla | str]: ...
@overload
def is_valid_hsla(
    color: object,
    /,
    *,
    allow_alpha: bool = True,
    allow_strings: Literal[False],
) -> TypeGuard[Hsla]: ...
@overload
def is_valid_hsla(
    color: object,
    /,
    *,
    allow_alpha: bool = True,
    allow_strings: bool = True,
) -> TypeGuard[Hsla | str] | TypeGuard[Hsla]: ...


def is_valid_hsla(
    color: object,
    /,
    *,
    allow_alpha: bool = True,
    allow_strings: bool = True,
) -> TypeGuard[Hsla | str] | TypeGuard[Hsla]:
    """Check if the given color is a valid HSLA color.\n
    ----------------------------------------------------------------------------------------------------
    *   `color` – The color to check (can be in any supported format).
    *   `allow_alpha` – Whether to allow alpha channel in the color.
    *   `allow_strings` – Whether to allow color strings."""

    if isinstance(color, hsla):
        return True

    elif is_seq(color):
        if (
            allow_alpha
            and len(color) == 4
            and (isinstance(color[0], int) and isinstance(color[1], int) and isinstance(color[2], int))
            and isinstance(color[3], float)
        ):
            return 0 <= color[0] <= 360 and 0 <= color[1] <= 100 and 0 <= color[2] <= 100 and 0.0 <= color[3] <= 1.0
        elif len(color) == 3 and (isinstance(color[0], int) and isinstance(color[1], int) and isinstance(color[2], int)):
            return 0 <= color[0] <= 360 and 0 <= color[1] <= 100 and 0 <= color[2] <= 100
        else:
            return False

    elif is_dict(color):
        if (
            allow_alpha
            and len(color) == 4
            and (
                isinstance(color.get("hue"), int) and isinstance(color.get("sat"), int) and isinstance(color.get("light"), int)
            )
            and isinstance(color.get("alpha"), float)
        ):
            return (
                0 <= color["hue"] <= 360
                and 0 <= color["sat"] <= 100
                and 0 <= color["light"] <= 100
                and 0.0 <= color["alpha"] <= 1.0
            )
        elif len(color) == 3 and (
            isinstance(color.get("hue"), int) and isinstance(color.get("sat"), int) and isinstance(color.get("light"), int)
        ):
            return 0 <= color["hue"] <= 360 and 0 <= color["sat"] <= 100 and 0 <= color["light"] <= 100
        else:
            return False

    elif allow_strings and isinstance(color, str):
        pattern = _PATTERNS.hsla_allow_alpha if allow_alpha else _PATTERNS.hsla_no_alpha
        return bool(pattern.fullmatch(color))

    return False


@overload
def is_valid_hexa(
    color: object, /, *, allow_alpha: bool = True, get_prefix: Literal[True]
) -> tuple[bool, Literal["#", "0x"] | None]: ...
@overload
def is_valid_hexa(color: object, /, *, allow_alpha: bool = True, get_prefix: Literal[False] = False) -> TypeGuard[Hexa]: ...
@overload
def is_valid_hexa(
    color: object, /, *, allow_alpha: bool = True, get_prefix: bool = False
) -> TypeGuard[Hexa] | tuple[bool, Literal["#", "0x"] | None]: ...


def is_valid_hexa(
    color: object, /, *, allow_alpha: bool = True, get_prefix: bool = False
) -> TypeGuard[Hexa] | tuple[bool, Literal["#", "0x"] | None]:
    """Check if the given color is a valid hex color.\n
    ----------------------------------------------------------------------------------------------------
    *   `color` – The color to check (can be in any supported format).
    *   `allow_alpha` – Whether to allow alpha channel in the color.
    *   `get_prefix` – If true, the prefix used in the color (if any)
    *   is returned along with validity."""

    if isinstance(color, hexa):
        return (True, "#") if get_prefix else True

    elif isinstance(color, int):
        is_valid_int = 0x000000 <= color <= (0xFFFFFFFF if allow_alpha else 0xFFFFFF)
        return (is_valid_int, "0x") if get_prefix else is_valid_int

    elif isinstance(color, str):
        prefix: Literal["#", "0x"] | None
        color, prefix = (
            (color[1:], "#") if color.startswith("#") else (color[2:], "0x") if color.startswith("0x") else (color, None)
        )
        pattern = _PATTERNS.hexa_allow_alpha if allow_alpha else _PATTERNS.hexa_no_alpha
        is_match = bool(pattern.fullmatch(color))
        return (is_match, prefix) if get_prefix else is_match

    return (False, None) if get_prefix else False


def is_valid(color: object, /, *, allow_alpha: bool = True) -> TypeGuard[Rgba | Hsla | Hexa]:
    """Check if the given color is a valid RGBA, HSLA or hex color.\n
    ----------------------------------------------------------------------------------------------------
    *   `color` – The color to check (can be in any supported format).
    *   `allow_alpha` – Whether to allow alpha channel in the color."""

    return bool(
        is_valid_rgba(color, allow_alpha=allow_alpha)
        or is_valid_hsla(color, allow_alpha=allow_alpha)
        or is_valid_hexa(color, allow_alpha=allow_alpha)
    )


def has_alpha(color: Rgba | Hsla | Hexa, /) -> bool:
    """Check if the given color has an alpha channel.\n
    ----------------------------------------------------------------------------------------------------
    *   `color` – The color to check (can be in any supported format)."""

    if isinstance(color, (rgba, hsla, hexa)):
        return color.has_alpha()

    elif is_valid_hexa(color):
        if isinstance(color, str):
            if color.startswith("#"):
                color = color[1:]
            elif color.startswith("0x"):
                color = color[2:]
            return len(color) == 4 or len(color) == 8

        # It must be an int if it's a valid hex and not a string (`hexa` object handled above).
        # Integers <= 0xFFFFFF represent 24-bit RGB (no alpha); integers > 0xFFFFFF represent 32-bit RGBA:
        return cast("int", color) > 0xFFFFFF

    elif isinstance(color, str):
        if parsed_rgba := extract_rgba(color, only_first=True):
            return parsed_rgba.has_alpha()
        elif parsed_hsla := extract_hsla(color, only_first=True):
            return parsed_hsla.has_alpha()

    elif (is_seq(color) and len(color) == 4) or (is_dict(color) and len(color) == 4):
        return True

    return False


def to_rgba(color: Rgba | Hsla | Hexa, /) -> rgba:
    """Will try to convert any color type to a color of type RGBA.\n
    ----------------------------------------------------------------------------------------------------
    *   `color` – The color to convert (can be in any supported format)."""

    if isinstance(color, (rgba, hsla, hexa)):
        return color.as_rgba()
    elif is_valid_rgba(color):
        return _parse_rgba(color)
    elif is_valid_hsla(color):
        return _parse_hsla(color).as_rgba()
    elif is_valid_hexa(color):
        return hexa(color).as_rgba()

    raise ValueError(f"Could not convert color {color!r} to RGBA\nMust be a valid RGBA, HSLA, or hex color")


def to_hsla(color: Rgba | Hsla | Hexa, /) -> hsla:
    """Will try to convert any color type to a color of type HSLA.\n
    ----------------------------------------------------------------------------------------------------
    *   `color` – The color to convert (can be in any supported format)."""

    if isinstance(color, (rgba, hsla, hexa)):
        return color.as_hsla()
    elif is_valid_hsla(color):
        return _parse_hsla(color)
    elif is_valid_rgba(color):
        return _parse_rgba(color).as_hsla()
    elif is_valid_hexa(color):
        return hexa(color).as_hsla()

    raise ValueError(f"Could not convert color {color!r} to HSLA\nMust be a valid RGBA, HSLA, or hex color")


def to_hexa(color: Rgba | Hsla | Hexa, /) -> hexa:
    """Will try to convert any color type to a color of type hex.\n
    ----------------------------------------------------------------------------------------------------
    *   `color` – The color to convert (can be in any supported format)."""

    if isinstance(color, (rgba, hsla, hexa)):
        return color.as_hexa()
    elif is_valid_hexa(color):
        return hexa(color)
    elif is_valid_rgba(color):
        return _parse_rgba(color).as_hexa()
    elif is_valid_hsla(color):
        return _parse_hsla(color).as_hexa()

    raise ValueError(f"Could not convert color {color!r} to hex\nMust be a valid RGBA, HSLA, or hex color")


@overload
def extract_rgba(string: str, /, *, only_first: Literal[True]) -> rgba | None: ...
@overload
def extract_rgba(string: str, /, *, only_first: Literal[False] = False) -> list[rgba] | None: ...
@overload
def extract_rgba(string: str, /, *, only_first: bool = False) -> rgba | list[rgba] | None: ...


def extract_rgba(string: str, /, *, only_first: bool = False) -> rgba | list[rgba] | None:
    """Will try to recognize RGBA colors inside a string and output the found ones as RGBA objects.\n
    ----------------------------------------------------------------------------------------------------
    *   `string` – The string to search for RGBA colors.
    *   `only_first` – If true, only the first found color will be returned,
        otherwise a list of all found colors."""

    if only_first:
        if not (match := _PATTERNS.rgba_allow_alpha.search(string)):
            return None

        groups = match.groups()
        return rgba(
            int(groups[0]),
            int(groups[1]),
            int(groups[2]),
            ((int(groups[3]) if "." not in groups[3] else float(groups[3])) if groups[3] else None),
            _validate=False,
        )

    else:
        if not (matches := _PATTERNS.rgba_allow_alpha.findall(string)):
            return None

        return [
            rgba(
                int(match[0]),
                int(match[1]),
                int(match[2]),
                ((int(match[3]) if "." not in match[3] else float(match[3])) if match[3] else None),
                _validate=False,
            )
            for match in matches
        ]


@overload
def extract_hsla(string: str, /, *, only_first: Literal[True]) -> hsla | None: ...
@overload
def extract_hsla(string: str, /, *, only_first: Literal[False] = False) -> list[hsla] | None: ...
@overload
def extract_hsla(string: str, /, *, only_first: bool = False) -> hsla | list[hsla] | None: ...


def extract_hsla(string: str, /, *, only_first: bool = False) -> hsla | list[hsla] | None:
    """Will try to recognize HSLA colors inside a string and output the found ones as HSLA objects.\n
    ----------------------------------------------------------------------------------------------------
    *   `string` – The string to search for HSLA colors.
    *   `only_first` – If true, only the first found color will be returned,
        otherwise a list of all found colors."""

    if only_first:
        if not (match := _PATTERNS.hsla_allow_alpha.search(string)):
            return None

        groups = match.groups()
        return hsla(
            int(groups[0]),
            int(groups[1]),
            int(groups[2]),
            ((int(groups[3]) if "." not in groups[3] else float(groups[3])) if groups[3] else None),
            _validate=False,
        )

    else:
        if not (matches := _PATTERNS.hsla_allow_alpha.findall(string)):
            return None

        return [
            hsla(
                int(match[0]),
                int(match[1]),
                int(match[2]),
                ((int(match[3]) if "." not in match[3] else float(match[3])) if match[3] else None),
                _validate=False,
            )
            for match in matches
        ]


def _parse_rgba(color: Rgba | str, /) -> rgba:
    """Internal method to parse a color to an RGBA object."""

    if isinstance(color, rgba):
        return color

    elif is_seq(color):
        if len(color) == 4:
            return rgba(int(color[0]), int(color[1]), int(color[2]), float(color[3]), _validate=False)
        elif len(color) == 3:
            return rgba(int(color[0]), int(color[1]), int(color[2]), None, _validate=False)
        raise ValueError(f"Could not parse RGBA color: {color!r}")

    elif is_dict(color):
        try:
            return rgba(
                int(color["red"]),
                int(color["green"]),
                int(color["blue"]),
                color.get("alpha"),
                _validate=False,
            )
        except (KeyError, ValueError):
            raise ValueError(f"Could not parse RGBA color: {color!r}") from None

    elif isinstance(color, str) and (parsed := extract_rgba(color, only_first=True)):
        return parsed

    raise ValueError(f"Could not parse RGBA color: {color!r}")


def _parse_hsla(color: Hsla | str, /) -> hsla:
    """Internal method to parse a color to an HSLA object."""

    if isinstance(color, hsla):
        return color

    elif is_seq(color):
        if len(color) == 4:
            return hsla(int(color[0]), int(color[1]), int(color[2]), float(color[3]), _validate=False)
        elif len(color) == 3:
            return hsla(int(color[0]), int(color[1]), int(color[2]), None, _validate=False)
        raise ValueError(f"Could not parse HSLA color: {color!r}")

    elif is_dict(color):
        try:
            return hsla(
                int(color["hue"]),
                int(color["sat"]),
                int(color["light"]),
                color.get("alpha"),
                _validate=False,
            )
        except (KeyError, ValueError):
            raise ValueError(f"Could not parse HSLA color: {color!r}") from None

    elif isinstance(color, str) and (parsed := extract_hsla(color, only_first=True)):
        return parsed

    raise ValueError(f"Could not parse HSLA color: {color!r}")


def rgba_to_hex_int(red: int, green: int, blue: int, alpha: float | None = None, /, *, preserve_original: bool = False) -> int:
    """Convert RGBA channels to a hex integer (alpha is optional).\n
    ----------------------------------------------------------------------------------------------------
    *   `red`, `green`, `blue` – The red, green, and blue channels in range [0, 255] inclusive.
    *   `alpha` – The alpha channel in range [0.0, 1.0] inclusive or `None` if not set.
    *   `preserve_original` – Whether to preserve the original color exactly (explained below).\n
    ----------------------------------------------------------------------------------------------------
    To preserve leading zeros, the function will add a `1` at the beginning,
    if the hex integer would start with a `0`.<br>
    This could affect the color a little bit, but will make sure, that it won't be interpreted
    as a completely different color, when initializing it as a `hexa()` color or changing it
    back to RGBA using `hex_int_to_rgba()`."""

    if not (0 <= red <= 255 and 0 <= green <= 255 and 0 <= blue <= 255):
        raise ValueError(
            f"The 'red', 'green' and 'blue' parameters must be integers in [0, 255], got {red=!r} {green=!r} {blue=!r}"
        )
    elif alpha is not None and not (0.0 <= alpha <= 1.0):
        raise ValueError(f"The 'alpha' parameter must be a float in [0.0, 1.0] or None, got {alpha!r}")

    red = max(0, min(255, int(red)))
    green = max(0, min(255, int(green)))
    blue = max(0, min(255, int(blue)))

    if alpha is None:
        hex_int = (red << 16) | (green << 8) | blue
        if not preserve_original and (hex_int & 0xF00000) == 0:
            hex_int |= 0x010000
    else:
        alpha = max(0, min(255, int(alpha * 255)))
        hex_int = (red << 24) | (green << 16) | (blue << 8) | alpha
        if not preserve_original and red == 0:
            hex_int |= 0x01000000

    return hex_int


def hex_int_to_rgba(hex_int: int, /, *, preserve_original: bool = False) -> rgba:
    """Convert a hex integer to RGBA channels.\n
    ----------------------------------------------------------------------------------------------------
    *   `hex_int` – The hex integer to convert.
    *   `preserve_original` – Whether to preserve the original color exactly (explained below).\n
    ----------------------------------------------------------------------------------------------------
    If the red channel is `1` after conversion, it will be set to `0`, because when converting
    from RGBA to a hex integer, the first `0` will be set to `1` to preserve leading zeros.<br>
    This is the correction, so the color doesn't even look slightly different."""

    if not (0 <= hex_int <= 0xFFFFFFFF):
        raise ValueError(f"Expected hex integer in range [0x000000, 0xFFFFFFFF] inclusive, got 0x{hex_int:X}")

    elif len(hex_str := f"{hex_int:X}") <= 6:
        hex_str = hex_str.zfill(6)
        return rgba(
            red if (red := int(hex_str[0:2], 16)) != 1 or preserve_original else 0,
            int(hex_str[2:4], 16),
            int(hex_str[4:6], 16),
            None,
            _validate=False,
        )

    else:
        hex_str = hex_str.zfill(8)
        return rgba(
            red if (red := int(hex_str[0:2], 16)) != 1 or preserve_original else 0,
            int(hex_str[2:4], 16),
            int(hex_str[4:6], 16),
            int(hex_str[6:8], 16) / 255.0,
            _validate=False,
        )


@overload
def get_luminance(
    red: int,
    green: int,
    blue: int,
    /,
    *,
    output_type: type[int],
    method: Literal["wcag2", "wcag3", "simple", "bt601"] = "wcag2",
) -> int: ...
@overload
def get_luminance(
    red: int,
    green: int,
    blue: int,
    /,
    *,
    output_type: type[float],
    method: Literal["wcag2", "wcag3", "simple", "bt601"] = "wcag2",
) -> float: ...
@overload
def get_luminance(
    red: int,
    green: int,
    blue: int,
    /,
    *,
    output_type: None = None,
    method: Literal["wcag2", "wcag3", "simple", "bt601"] = "wcag2",
) -> int: ...
@overload
def get_luminance(
    red: int,
    green: int,
    blue: int,
    /,
    *,
    output_type: type[int | float] | None = None,
    method: Literal["wcag2", "wcag3", "simple", "bt601"] = "wcag2",
) -> int | float: ...


def get_luminance(
    red: int,
    green: int,
    blue: int,
    /,
    *,
    output_type: type[int | float] | None = None,
    method: Literal["wcag2", "wcag3", "simple", "bt601"] = "wcag2",
) -> int | float:
    """Calculates the relative luminance of a color according to various standards.\n
    ----------------------------------------------------------------------------------------------------
    *   `red`, `green`, `blue` – The red, green and blue channels in range [0, 255] inclusive.
    *   `output_type` – The range of the returned luminance value:
        -   `int` returns integer in range [0, 100] inclusive.
        -   `float` returns float in range [0.0, 1.0] inclusive.
        -   `None` returns integer in range [0, 255] inclusive.
    *   `method` – The luminance calculation method to use:
        -   `"wcag2"` WCAG 2.0 standard (default and most accurate for perception)
        -   `"wcag3"` draft WCAG 3.0 standard with improved coefficients
        -   `"simple"` simple arithmetic mean (less accurate)
        -   `"bt601"` ITU-R BT.601 standard (older TV standard)"""

    if not (0 <= red <= 255 and 0 <= green <= 255 and 0 <= blue <= 255):
        raise ValueError(
            f"The 'red', 'green' and 'blue' parameters must be integers in [0, 255], got {red=!r} {green=!r} {blue=!r}"
        )

    match method:
        case "simple":
            luminance = (red / 255.0 + green / 255.0 + blue / 255.0) / 3
        case "bt601":
            luminance = 0.299 * red / 255.0 + 0.587 * green / 255.0 + 0.114 * blue / 255.0
        case "wcag3":
            luminance = (
                0.2126729 * _SRGB_LINEAR_LUT[red] + 0.7151522 * _SRGB_LINEAR_LUT[green] + 0.0721750 * _SRGB_LINEAR_LUT[blue]
            )
        case _:
            luminance = 0.2126 * _SRGB_LINEAR_LUT[red] + 0.7152 * _SRGB_LINEAR_LUT[green] + 0.0722 * _SRGB_LINEAR_LUT[blue]

    if output_type is int:
        return round(luminance * 100)
    elif output_type is float:
        return luminance
    else:
        return round(luminance * 255)


@overload
def get_text_fg(text_bg_color: rgba, /) -> rgba: ...
@overload
def get_text_fg(text_bg_color: hexa, /) -> hexa: ...
@overload
def get_text_fg(text_bg_color: int, /) -> int: ...
@overload
def get_text_fg(text_bg_color: Rgba | Hexa, /) -> rgba | hexa | int: ...


def get_text_fg(text_bg_color: Rgba | Hexa, /) -> rgba | hexa | int:
    """Returns either black or white text color for optimal contrast on the given background color.\n
    ----------------------------------------------------------------------------------------------------
    *   `text_bg_color` – The background color (can be in RGBA or hex format)."""

    was_hexa, was_int = is_valid_hexa(text_bg_color), isinstance(text_bg_color, int)

    text_bg_rgba = to_rgba(text_bg_color)
    luminance = 0.2126 * text_bg_rgba[0] + 0.7152 * text_bg_rgba[1] + 0.0722 * text_bg_rgba[2]

    return (
        (
            (0xFFFFFF if was_int else hexa(_red=255, _green=255, _blue=255))
            if was_hexa
            else rgba(255, 255, 255, _validate=False)
        )
        if luminance < 128
        else ((0x000 if was_int else hexa(_red=0, _green=0, _blue=0)) if was_hexa else rgba(0, 0, 0, _validate=False))
    )


@overload
def adjust_lightness(color: rgba, light_change: float, /) -> rgba: ...
@overload
def adjust_lightness(color: hexa, light_change: float, /) -> hexa: ...
@overload
def adjust_lightness(color: Rgba | Hexa, light_change: float, /) -> rgba | hexa: ...


def adjust_lightness(color: Rgba | Hexa, light_change: float, /) -> rgba | hexa:
    """In- or decrease the lightness of the input color.\n
    ----------------------------------------------------------------------------------------------------
    *   `color` – The color to adjust (can be in RGBA or hex format).
    *   `light_change` – The amount to change the lightness by,
        in range `-1.0` (darken by 100%) and `1.0` (lighten by 100%)."""

    if not (-1.0 <= light_change <= 1.0):
        raise ValueError(f"The 'light_change' parameter must be in range [-1.0, 1.0] inclusive, got {light_change!r}")

    was_hexa = is_valid_hexa(color)
    hsla_color = to_hsla(color)

    hue, sat, light, alpha = (
        int(hsla_color[0]),
        int(hsla_color[1]),
        int(hsla_color[2]),
        hsla_color[3] if hsla_color.has_alpha() else None,
    )
    light = int(max(0, min(100, light + light_change * 100)))

    return (
        hsla(hue, sat, light, alpha, _validate=False).as_hexa()
        if was_hexa
        else hsla(hue, sat, light, alpha, _validate=False).as_rgba()
    )


@overload
def adjust_saturation(color: rgba, sat_change: float, /) -> rgba: ...
@overload
def adjust_saturation(color: hexa, sat_change: float, /) -> hexa: ...
@overload
def adjust_saturation(color: Rgba | Hexa, sat_change: float, /) -> rgba | hexa: ...


def adjust_saturation(color: Rgba | Hexa, sat_change: float, /) -> rgba | hexa:
    """In- or decrease the saturation of the input color.\n
    ----------------------------------------------------------------------------------------------------
    *   `color` – The color to adjust (can be in RGBA or hex format).
    *   `sat_change` – The amount to change the saturation by,
        in range `-1.0` (saturate by 100%) and `1.0` (desaturate by 100%)."""

    if not (-1.0 <= sat_change <= 1.0):
        raise ValueError(f"The 'sat_change' parameter must be in range [-1.0, 1.0] inclusive, got {sat_change!r}")

    was_hexa = is_valid_hexa(color)
    hsla_color = to_hsla(color)

    hue, sat, light, alpha = (
        int(hsla_color[0]),
        int(hsla_color[1]),
        int(hsla_color[2]),
        hsla_color[3] if hsla_color.has_alpha() else None,
    )
    sat = int(max(0, min(100, sat + sat_change * 100)))

    return (
        hsla(hue, sat, light, alpha, _validate=False).as_hexa()
        if was_hexa
        else hsla(hue, sat, light, alpha, _validate=False).as_rgba()
    )


def _linear_to_srgb(linear_val: float, /) -> int:
    """Converts a linear RGB float in range [0.0, 1.0] to an 8-bit sRGB integer in range [0, 255]."""

    srgb_val = linear_val * 12.92 if linear_val <= 0.0031308 else (1.055 * (linear_val ** (1.0 / 2.4)) - 0.055)
    return max(0, min(255, int(srgb_val * 255.0 + 0.5)))


def _interpolate_rgb(
    red1: int,
    green1: int,
    blue1: int,
    red2: int,
    green2: int,
    blue2: int,
    ratio: float,
    /,
) -> tuple[int, int, int]:
    """Internal function to linearly interpolate two RGB colors in naive sRGB space."""

    inv_ratio = 1.0 - ratio
    return (
        max(0, min(255, int(red1 * inv_ratio + red2 * ratio + 0.5))),
        max(0, min(255, int(green1 * inv_ratio + green2 * ratio + 0.5))),
        max(0, min(255, int(blue1 * inv_ratio + blue2 * ratio + 0.5))),
    )


def _interpolate_linear_rgb(
    red1: int,
    green1: int,
    blue1: int,
    red2: int,
    green2: int,
    blue2: int,
    ratio: float,
    /,
) -> tuple[int, int, int]:
    """Internal function to interpolate two RGB colors in gamma-corrected linear RGB space."""

    inv_ratio = 1.0 - ratio
    lin_red = _SRGB_LINEAR_LUT[red1] * inv_ratio + _SRGB_LINEAR_LUT[red2] * ratio
    lin_green = _SRGB_LINEAR_LUT[green1] * inv_ratio + _SRGB_LINEAR_LUT[green2] * ratio
    lin_blue = _SRGB_LINEAR_LUT[blue1] * inv_ratio + _SRGB_LINEAR_LUT[blue2] * ratio

    return (_linear_to_srgb(lin_red), _linear_to_srgb(lin_green), _linear_to_srgb(lin_blue))


def _rgb_to_hsl(red: int, green: int, blue: int, /) -> tuple[float, float, float]:
    """Internal function to convert an RGB color to HSL floats (hue in [0, 360), sat and light in [0, 1])."""

    norm_red = red / 255.0
    norm_green = green / 255.0
    norm_blue = blue / 255.0

    max_val = max(norm_red, norm_green, norm_blue)
    min_val = min(norm_red, norm_green, norm_blue)
    delta_val = max_val - min_val
    light_val = (max_val + min_val) / 2.0

    if delta_val < 1e-6:
        return (0.0, 0.0, light_val)

    sat_val = delta_val / (1.0 - abs(2.0 * light_val - 1.0)) if (0.0 < light_val < 1.0) else 0.0

    if max_val == norm_red:
        hue_val = 60.0 * (((norm_green - norm_blue) / delta_val) % 6.0)
    elif max_val == norm_green:
        hue_val = 60.0 * (((norm_blue - norm_red) / delta_val) + 2.0)
    else:
        hue_val = 60.0 * (((norm_red - norm_green) / delta_val) + 4.0)

    return (hue_val % 360.0, sat_val, light_val)


def _hsl_to_rgb(hue: float, sat: float, light: float, /) -> tuple[int, int, int]:
    """Internal function to convert HSL floats (hue in [0, 360), sat and light in [0, 1]) to RGB integers."""

    chroma_val = (1.0 - abs(2.0 * light - 1.0)) * sat
    hue_sector = (hue % 360.0) / 60.0
    second_comp = chroma_val * (1.0 - abs((hue_sector % 2.0) - 1.0))
    light_match = light - chroma_val / 2.0

    if hue_sector < 1.0:
        red_part, green_part, blue_part = chroma_val, second_comp, 0.0
    elif hue_sector < 2.0:
        red_part, green_part, blue_part = second_comp, chroma_val, 0.0
    elif hue_sector < 3.0:
        red_part, green_part, blue_part = 0.0, chroma_val, second_comp
    elif hue_sector < 4.0:
        red_part, green_part, blue_part = 0.0, second_comp, chroma_val
    elif hue_sector < 5.0:
        red_part, green_part, blue_part = second_comp, 0.0, chroma_val
    else:
        red_part, green_part, blue_part = chroma_val, 0.0, second_comp

    return (
        max(0, min(255, int((red_part + light_match) * 255.0 + 0.5))),
        max(0, min(255, int((green_part + light_match) * 255.0 + 0.5))),
        max(0, min(255, int((blue_part + light_match) * 255.0 + 0.5))),
    )


def _interpolate_hsl(
    red1: int,
    green1: int,
    blue1: int,
    red2: int,
    green2: int,
    blue2: int,
    ratio: float,
    /,
    *,
    long_path: bool = False,
) -> tuple[int, int, int]:
    """Internal function to interpolate two RGB colors in HSL space."""

    hue1, sat1, light1 = _rgb_to_hsl(red1, green1, blue1)
    hue2, sat2, light2 = _rgb_to_hsl(red2, green2, blue2)

    # If one color is achromatic, inherit hue from the chromatic color:
    if sat1 < 1e-6 and sat2 >= 1e-6:
        hue1 = hue2
    elif sat2 < 1e-6 and sat1 >= 1e-6:
        hue2 = hue1

    delta_hue = hue2 - hue1

    if not long_path:
        if delta_hue > 180.0:
            delta_hue -= 360.0
        elif delta_hue < -180.0:
            delta_hue += 360.0
    else:
        if 0.0 < delta_hue < 180.0:
            delta_hue -= 360.0
        elif -180.0 < delta_hue <= 0.0:
            delta_hue += 360.0

    interp_hue = (hue1 + delta_hue * ratio) % 360.0
    interp_sat = sat1 * (1.0 - ratio) + sat2 * ratio
    interp_light = light1 * (1.0 - ratio) + light2 * ratio

    return _hsl_to_rgb(interp_hue, interp_sat, interp_light)


def _interpolate_oklab(
    red1: int,
    green1: int,
    blue1: int,
    red2: int,
    green2: int,
    blue2: int,
    ratio: float,
    /,
) -> tuple[int, int, int]:
    """Internal function to interpolate two RGB colors in perceptually uniform Oklab space."""

    # [1] Convert sRGB to linear RGB:
    lin_red1 = _SRGB_LINEAR_LUT[red1]
    lin_green1 = _SRGB_LINEAR_LUT[green1]
    lin_blue1 = _SRGB_LINEAR_LUT[blue1]
    lin_red2 = _SRGB_LINEAR_LUT[red2]
    lin_green2 = _SRGB_LINEAR_LUT[green2]
    lin_blue2 = _SRGB_LINEAR_LUT[blue2]

    # [2] Linear RGB to LMS:
    lms_l1 = 0.4122214708 * lin_red1 + 0.5363325363 * lin_green1 + 0.0514459929 * lin_blue1
    lms_m1 = 0.2119034982 * lin_red1 + 0.6806995451 * lin_green1 + 0.1073969566 * lin_blue1
    lms_s1 = 0.0883024619 * lin_red1 + 0.2817188376 * lin_green1 + 0.6299787005 * lin_blue1
    lms_l2 = 0.4122214708 * lin_red2 + 0.5363325363 * lin_green2 + 0.0514459929 * lin_blue2
    lms_m2 = 0.2119034982 * lin_red2 + 0.6806995451 * lin_green2 + 0.1073969566 * lin_blue2
    lms_s2 = 0.0883024619 * lin_red2 + 0.2817188376 * lin_green2 + 0.6299787005 * lin_blue2

    # Cube root:
    l1_cbrt = _math.cbrt(lms_l1)
    m1_cbrt = _math.cbrt(lms_m1)
    s1_cbrt = _math.cbrt(lms_s1)
    l2_cbrt = _math.cbrt(lms_l2)
    m2_cbrt = _math.cbrt(lms_m2)
    s2_cbrt = _math.cbrt(lms_s2)

    # [3] LMS to Oklab:
    lab_l1 = 0.2104542553 * l1_cbrt + 0.7936177850 * m1_cbrt - 0.0040720468 * s1_cbrt
    lab_a1 = 1.9779984951 * l1_cbrt - 2.4285922050 * m1_cbrt + 0.4505937099 * s1_cbrt
    lab_b1 = 0.0259040371 * l1_cbrt + 0.7827717662 * m1_cbrt - 0.8086757660 * s1_cbrt
    lab_l2 = 0.2104542553 * l2_cbrt + 0.7936177850 * m2_cbrt - 0.0040720468 * s2_cbrt
    lab_a2 = 1.9779984951 * l2_cbrt - 2.4285922050 * m2_cbrt + 0.4505937099 * s2_cbrt
    lab_b2 = 0.0259040371 * l2_cbrt + 0.7827717662 * m2_cbrt - 0.8086757660 * s2_cbrt

    # [4] Interpolate in Oklab:
    inv_ratio = 1.0 - ratio
    interp_l = lab_l1 * inv_ratio + lab_l2 * ratio
    interp_a = lab_a1 * inv_ratio + lab_a2 * ratio
    interp_b = lab_b1 * inv_ratio + lab_b2 * ratio

    # [5] Inverse Oklab to LMS:
    out_l_cbrt = interp_l + 0.3963377774 * interp_a + 0.2158037573 * interp_b
    out_m_cbrt = interp_l - 0.1055613458 * interp_a - 0.0638541728 * interp_b
    out_s_cbrt = interp_l - 0.0894841775 * interp_a - 1.2914855480 * interp_b

    out_l = out_l_cbrt * out_l_cbrt * out_l_cbrt
    out_m = out_m_cbrt * out_m_cbrt * out_m_cbrt
    out_s = out_s_cbrt * out_s_cbrt * out_s_cbrt

    # [6] LMS to Linear RGB:
    lin_red = +4.0767439362 * out_l - 3.3077115913 * out_m + 0.2309699295 * out_s
    lin_green = -1.2684380046 * out_l + 2.6097574011 * out_m - 0.3413193965 * out_s
    lin_blue = -0.0041960863 * out_l - 0.7034186147 * out_m + 1.7076147010 * out_s

    return (_linear_to_srgb(lin_red), _linear_to_srgb(lin_green), _linear_to_srgb(lin_blue))


def _interpolate_color(
    red1: int,
    green1: int,
    blue1: int,
    red2: int,
    green2: int,
    blue2: int,
    /,
    *,
    ratio: float,
    space: Literal["rgb", "hsl", "hsl_long", "linear_rgb", "oklab"] = "hsl",
) -> tuple[int, int, int]:
    """Internal function to interpolate two RGB colors using the specified color space."""

    clamped_ratio = max(0.0, min(1.0, ratio))

    match space:
        case "rgb":
            return _interpolate_rgb(red1, green1, blue1, red2, green2, blue2, clamped_ratio)
        case "linear_rgb":
            return _interpolate_linear_rgb(red1, green1, blue1, red2, green2, blue2, clamped_ratio)
        case "hsl":
            return _interpolate_hsl(red1, green1, blue1, red2, green2, blue2, clamped_ratio, long_path=False)
        case "hsl_long":
            return _interpolate_hsl(red1, green1, blue1, red2, green2, blue2, clamped_ratio, long_path=True)
        case "oklab":
            return _interpolate_oklab(red1, green1, blue1, red2, green2, blue2, clamped_ratio)
        case _:
            raise ValueError(f"Unsupported color space {space!r}")


def _resolve_color_stop(
    stops: tuple[tuple[tuple[int, int, int], float], ...],
    position: float,
    /,
    *,
    space: Literal["rgb", "hsl", "hsl_long", "linear_rgb", "oklab"] = "hsl",
) -> tuple[int, int, int]:
    """Internal helper to resolve an RGB color at ratio `position` across stops without alpha overhead."""

    if not stops:
        return (0, 0, 0)
    elif len(stops) == 1 or position <= stops[0][1]:
        return stops[0][0]
    elif position >= stops[-1][1]:
        return stops[-1][0]

    for i in range(len(stops) - 1):
        rgb1, pos1 = stops[i]
        rgb2, pos2 = stops[i + 1]

        if pos1 <= position <= pos2:
            seg_ratio = (position - pos1) / seg_len if (seg_len := pos2 - pos1) > 1e-9 else 0.0
            return _interpolate_color(rgb1[0], rgb1[1], rgb1[2], rgb2[0], rgb2[1], rgb2[2], ratio=seg_ratio, space=space)

    return stops[-1][0]  # coverage:ignore[defensive-return]


def _distribute_color_stops[T](raw_stops: Sequence[tuple[T, float | None]], /) -> tuple[tuple[T, float], ...]:
    """Calculate and distribute stop positions across normalized color stops.\n
    ----------------------------------------------------------------------------------------------------
    *   `raw_stops` – Sequence of `(color_payload, position_or_none)` tuples.\n
    ----------------------------------------------------------------------------------------------------
    Assumes color data is already fully normalized and validated."""

    if (total_count := len(raw_stops)) == 1:
        return ((raw_stops[0][0], 0.0),)

    has_explicit_positions = False
    for _, pos_val in raw_stops:
        if pos_val is not None:
            has_explicit_positions = True
            break

    if not has_explicit_positions:
        step_factor = 1.0 / (total_count - 1)
        return tuple([(color_val, i * step_factor) for i, (color_val, _) in enumerate(raw_stops)])

    resolved: list[tuple[T, float]] = []
    for color_val, pos_val in raw_stops:
        resolved.append((color_val, 0.0 if pos_val is None else max(0.0, min(1.0, pos_val))))

    resolved.sort(key=lambda item: item[1])

    if resolved[0][1] > 0.0:
        resolved.insert(0, (resolved[0][0], 0.0))
    if resolved[-1][1] < 1.0:
        resolved.append((resolved[-1][0], 1.0))

    return tuple(resolved)


def _calculate_gradient(
    stops: tuple[tuple[tuple[int, int, int], float], ...],
    /,
    *,
    steps: int,
    space: Literal["rgb", "hsl", "hsl_long", "linear_rgb", "oklab"] = "hsl",
) -> tuple[tuple[int, int, int], ...]:
    """Internal calculation helper to generate `steps` interpolated RGB colors from normalized stops."""

    if steps == 1:
        return (stops[0][0],)

    result: list[tuple[int, int, int]] = []
    inv_steps = 1.0 / (steps - 1)

    for i in range(steps):
        result.append(_resolve_color_stop(stops, i * inv_steps, space=space))

    return tuple(result)


def _extract_rgb_fast(color: _ColorBase | Rgba | Hsla | Hexa, /) -> tuple[int, int, int]:
    """Internal helper to extract plain `(red, green, blue)` integers from any color representation without object creation."""

    if isinstance(color, (rgba, hexa)):
        return (color.red, color.green, color.blue)

    elif isinstance(color, hsla):
        return hsla._hsl_to_rgb(color.hue, color.sat, color.light)

    elif is_seq(color) and len(color) in {3, 4}:
        return (int(color[0]), int(color[1]), int(color[2]))

    elif isinstance(color, int):
        if not (0x000000 <= color <= 0xFFFFFF):
            raise ValueError(f"Expected 24-bit hex integer in range [0x000000, 0xFFFFFF] inclusive, got 0x{color:X}")
        return ((color >> 16) & 0xFF, (color >> 8) & 0xFF, color & 0xFF)

    elif isinstance(color, str):
        if (hex_clean := color.strip().lstrip("#")).lower().startswith("0x"):
            hex_clean = hex_clean[2:]

        if len(hex_clean) == 3:
            return (
                int(hex_clean[0] * 2, 16),
                int(hex_clean[1] * 2, 16),
                int(hex_clean[2] * 2, 16),
            )
        elif len(hex_clean) == 6:
            return (
                int(hex_clean[0:2], 16),
                int(hex_clean[2:4], 16),
                int(hex_clean[4:6], 16),
            )

        color_obj = to_rgba(color)
        return (color_obj.red, color_obj.green, color_obj.blue)

    color_obj = to_rgba(cast("Any", color))
    return (color_obj.red, color_obj.green, color_obj.blue)


def _extract_alpha_fast(color: _ColorBase | Rgba | Hsla | Hexa, /) -> float | None:
    """Internal helper to extract alpha from a color representation without object creation."""

    if isinstance(color, (rgba, hsla, hexa)):
        return color.alpha
    elif is_seq(color) and len(color) == 4:
        return float(color[3])
    elif is_dict(color) and "alpha" in color:
        return float(color["alpha"])

    return None


type ColorStop = Rgba | Hsla | Hexa | tuple[Rgba | Hsla | Hexa, float | int]
"""A color stop for gradient generation: a color value or a `(color, position)` tuple."""


def _parse_color_stops(colors: Sequence[ColorStop], /) -> tuple[tuple[tuple[int, int, int], float | None, float], ...]:
    """Internal helper to parse and sort color stops into `((red, green, blue), alpha, position)` tuples."""

    raw_items: list[tuple[tuple[tuple[int, int, int], float | None], float | None]] = []

    for item in colors:
        if isinstance(item, tuple) and len(item) == 2:
            raw_color = item[0]
            raw_items.append(((_extract_rgb_fast(raw_color), _extract_alpha_fast(raw_color)), float(item[1])))
        else:
            raw_items.append(((_extract_rgb_fast(item), _extract_alpha_fast(item)), None))

    return tuple([(item[0][0], item[0][1], item[1]) for item in _distribute_color_stops(raw_items)])


def _resolve_color_stop_with_alpha(
    stops: tuple[tuple[tuple[int, int, int], float | None, float], ...],
    position: float,
    /,
    *,
    space: Literal["rgb", "hsl", "hsl_long", "linear_rgb", "oklab"] = "hsl",
) -> tuple[tuple[int, int, int], float | None]:
    """Internal helper to resolve an RGB color and alpha value at the given position `position`."""

    if not stops:
        return ((0, 0, 0), None)
    elif len(stops) == 1 or position <= stops[0][2]:
        return (stops[0][0], stops[0][1])
    elif position >= stops[-1][2]:
        return (stops[-1][0], stops[-1][1])

    interp_rgb = _resolve_color_stop(tuple([(item[0], item[2]) for item in stops]), position, space=space)

    for i in range(len(stops) - 1):
        _, alpha1, pos1 = stops[i]
        _, alpha2, pos2 = stops[i + 1]

        if pos1 <= position <= pos2:
            if alpha1 is None and alpha2 is None:
                return (interp_rgb, None)

            seg_ratio = (position - pos1) / seg_len if (seg_len := pos2 - pos1) > 1e-9 else 0.0
            val1, val2 = 1.0 if alpha1 is None else alpha1, 1.0 if alpha2 is None else alpha2

            return (interp_rgb, round(val1 * (1.0 - seg_ratio) + val2 * seg_ratio, 4))

    return (interp_rgb, None)  # coverage:ignore[defensive-return]


def interpolate_color(
    color1: Rgba | Hsla | Hexa,
    color2: Rgba | Hsla | Hexa,
    /,
    *,
    ratio: float = 0.5,
    space: Literal["rgb", "hsl", "hsl_long", "linear_rgb", "oklab"] = "hsl",
) -> rgba:
    """Linearly interpolates between two colors in the specified color space.\n
    ----------------------------------------------------------------------------------------------------
    *   `color1` – The starting color (RGBA, HSLA, hex, or tuple).
    *   `color2` – The ending color (RGBA, HSLA, hex, or tuple).
    *   `ratio` – The blend ratio between `0.0` (100% `color1`) and `1.0` (100% `color2`).
    *   `space` – The color space to interpolate in
        (`"rgb"`, `"hsl"`, `"hsl_long"`, `"linear_rgb"`, or `"oklab"`). Default is `"hsl"`.\n
    ----------------------------------------------------------------------------------------------------
    Raises `ValueError` if `space` is invalid."""

    if space not in {"rgb", "hsl", "hsl_long", "linear_rgb", "oklab"}:
        raise ValueError(f"Unsupported color space {space!r}")

    clamped_ratio = max(0.0, min(1.0, ratio))
    rgb1 = _extract_rgb_fast(color1)
    rgb2 = _extract_rgb_fast(color2)

    red, green, blue = _interpolate_color(
        rgb1[0], rgb1[1], rgb1[2], rgb2[0], rgb2[1], rgb2[2], ratio=clamped_ratio, space=space
    )

    alpha1 = _extract_alpha_fast(color1)
    alpha2 = _extract_alpha_fast(color2)
    alpha: float | None = None

    if alpha1 is not None or alpha2 is not None:
        val1, val2 = 1.0 if alpha1 is None else alpha1, 1.0 if alpha2 is None else alpha2
        alpha = round(val1 * (1.0 - clamped_ratio) + val2 * clamped_ratio, 4)

    return rgba(red, green, blue, alpha, _validate=False)


def create_gradient(
    colors: Sequence[ColorStop],
    /,
    *,
    steps: int = 10,
    space: Literal["rgb", "hsl", "hsl_long", "linear_rgb", "oklab"] = "hsl",
) -> tuple[rgba, ...]:
    """Creates a tuple of `steps` smoothly interpolated colors across the given color stops.\n
    ----------------------------------------------------------------------------------------------------
    *   `colors` – Sequence of colors or `(color, position)` tuples defining the gradient stops.
    *   `steps` – Total number of color steps to generate. Default is `10`.
    *   `space` – The color space to interpolate in
        (`"rgb"`, `"hsl"`, `"hsl_long"`, `"linear_rgb"`, or `"oklab"`). Default is `"hsl"`.\n
    ----------------------------------------------------------------------------------------------------
    Raises `ValueError` if `steps < 1`, `colors` is empty, or `space` is invalid."""

    if steps < 1:
        raise ValueError(f"The 'steps' parameter must be an integer >= 1, got {steps!r}")
    elif not colors:
        raise ValueError("At least one color stop must be provided for a gradient")
    elif space not in {"rgb", "hsl", "hsl_long", "linear_rgb", "oklab"}:
        raise ValueError(f"Unsupported color space {space!r}")

    parsed_stops = _parse_color_stops(colors)

    if steps == 1:
        first_rgb, first_alpha, _ = parsed_stops[0]
        return (rgba(first_rgb[0], first_rgb[1], first_rgb[2], first_alpha, _validate=False),)

    has_alpha = False
    for _, alpha_val, _ in parsed_stops:
        if alpha_val is not None:
            has_alpha = True
            break

    if not has_alpha:
        pure_stops = tuple([(item[0], item[2]) for item in parsed_stops])
        calc_rgbs = _calculate_gradient(pure_stops, steps=steps, space=space)
        return tuple([rgba(rgb[0], rgb[1], rgb[2], None, _validate=False) for rgb in calc_rgbs])

    result: list[rgba] = []
    inv_steps = 1.0 / (steps - 1)
    for i in range(steps):
        pos = i * inv_steps
        rgb, alpha = _resolve_color_stop_with_alpha(parsed_stops, pos, space=space)
        result.append(rgba(rgb[0], rgb[1], rgb[2], alpha, _validate=False))

    return tuple(result)
