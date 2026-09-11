"""
This module provides the `S` and `Term` classes for building richly styled<br>
terminal output using a typed, operator-based syntax.

---

### The Easy Styling

First, let's take a look at a small example of what a highly styled output could look like using this module:

```python
S(
    ("First normal & unstyled text. ", \
(S.BOLD | S.UNDERLINE | S.BR.BLUE)("Bright blue, bold, and underlined text.")),
    ((S.hex("#000") | S.BG.hex("#F67"))("Black text with a red background."), \
" And then ", S.ITALIC("(boring)"), " plain text again."),
    sep="\\n",
).print()
```

<!-- DOCS: <TerminalOutput>
First normal & unstyled text. <span class="b u br-blue">Bright blue, bold, and underlined text.</span>
<span class="#000 bg-#F67">Black text with a red background.</span> And then (<span class="i">boring</span>) plain text again.
</TerminalOutput> -->

How all of this exactly works is explained in the sections below. 🠫


### Styles and Groups

In this module, you apply styles and colors using `S` attributes.<br>
Every style attribute supports two operators:

*   `|` combines two or more styles into a single immutable group, e.g., `S.BOLD | S.RED` → bold + red foreground
*   `()` applies the style (or group) to the given text and auto-resets the style after it, e.g.,
    `S.BOLD("hello")` → bold "hello", reset back to normal afterwards `(S.BOLD | S.RED)("hello")` → same idea, combined

A list of all possible style attributes can be found below.


### Auto Resetting Styles

Every `_Style`, `_StyleGroup`, `_ColorStyle` or `_Link` call automatically generates the<br>
matching reset sequence behind its text, just like shown in the following example:

```python
S(
    ("This is plain text, ", S.BR.BLUE("which is bright blue now.")),
    "Now it was automatically reset to plain again.",
    sep="\\n",
).print()
```

<!-- DOCS: <TerminalOutput>
This is plain text, <span class="br-blue">which is bright blue now.</span>
Now it was automatically reset to plain again.
</TerminalOutput> -->

Only the specific styles that were applied are reset; other styling in scope is left intact:

```python
S.CYAN(
    "This is cyan text, ", S.DIM("which is dimmed now."),
    "\\nNow it's not dimmed any more but still cyan.",
).print()
```

<!-- DOCS: <TerminalOutput>
<span class="cyan">This is cyan text, <span class="dim">which is dimmed now.</span></span>
<span class="cyan">Now it's not dimmed any more but still cyan.</span>
</TerminalOutput> -->


### Bare (Open-Only) Styles

Passing a style object *without calling it* emits only its opening ANSI sequence at that position,
with no matching close/reset appended.<br>
This is the typed equivalent of `[…]` (open bracket without closing braces) from the legacy string syntax:

```python
S(
    S.RED, "[ERROR] Something went wrong!",
    S.RESET, " Back to normal.",
).print()
```

<!-- DOCS: <TerminalOutput>
<span class="red">[ERROR] Something went wrong!</span> Back to normal.
</TerminalOutput> -->

Any style type supports bare usage: `S.RED` (`_Style`), `S.hex("#F67")` (`_ColorStyle`),
`S.link("url")` (`_Link`), and `S.BOLD | S.RED` (`_StyleGroup`).<br>
Bare styles can also appear inside tuples and nested calls:

```python
S.ITALIC("a", S.MAGENTA, "B", S.RESET_FG, "c").print()
```

<!-- DOCS: <TerminalOutput>
<span class="i">a<span class="magenta">B</span>c</span>
</TerminalOutput> -->


### Nesting and Multi-Segment Groups

A style call accepts either a single piece of text or any number of mixed segments.<br>
Strings, `S` objects, bare style objects, and raw tuples can be mixed freely:

*   `S.X("text")`               – Apply `X` to `"text"`, auto-reset after.
*   `S.X | S.Y`                 – Combine `X` and `Y` into a single group.
*   `(S.X | S.Y)("text")`       – Apply the group to `"text"`.
*   `S.X("a", S.Y("b"), "c")`   – Nested multi-segment: `Y` is applied only to `"b"`.
*   `S.X`                       – Bare: emit only the opening sequence, no auto-reset.
*   `("a", S.X("b"), "c")`      – Same-line group; passed as a single tuple to `S(…)`.

Inside `S(*segments, sep="\\n")`, every positional argument is treated as one logical line and joined by `sep`.<br>
An empty string argument `""` therefore produces a blank line.


### All Possible Style Attributes

*   Text styles:
    -   `S.BOLD`
    -   `S.DIM`
    -   `S.ITALIC`
    -   `S.UNDERLINE`
    -   `S.INVERSE`
    -   `S.BLINK`
    -   `S.HIDDEN`
    -   `S.STRIKE`
    -   `S.DOUBLE_UNDERLINE`
*   Standard foreground colors:
    -   `S.BLACK`, `S.RED`, `S.GREEN`, `S.YELLOW`,
        `S.BLUE`, `S.MAGENTA`, `S.CYAN`, `S.WHITE`
*   Bright foreground colors (`S.BR.*`):
    -   `S.BR.BLACK`, `S.BR.RED`, `S.BR.GREEN`, …
*   Standard background colors (`S.BG.*`):
    -   `S.BG.BLACK`, `S.BG.RED`, `S.BG.GREEN`, …
*   Bright background colors (`S.BG.BR.*`):
    -   `S.BG.BR.RED`, `S.BG.BR.GREEN`, …
*   24-bit true-color (foreground / background):
    -   `S.rgb(255, 96, 112)`
    -   `S.hex("#FF6070")`  or  `S.hex("F67")`
    -   `S.BG.rgb(0, 100, 255)`
    -   `S.BG.hex("#0064FF")`  or  `S.BG.hex("06F")`
*   256-color palette (foreground / background):
    -   `S.color256(210)`
    -   `S.BG.color256(69)`
*   Hyperlinks (OSC 8):
    -   `S.link("https://example.com")("click here")`
    -   `(S.link("…") | S.BR.BLUE)("click here")`
*   Specific resets (only needed in advanced use; auto-reset usually covers it):
    -   `S.RESET_BOLD`, `S.RESET_DIM`, `S.RESET_ITALIC`, `S.RESET_UNDERLINE`,
        `S.RESET_BLINK`, `S.RESET_INVERSE`, `S.RESET_HIDDEN`, `S.RESET_STRIKE`,
        `S.RESET_FG`, `S.RESET_BG`
*   Total reset (resets every previously applied styles):
    -   `S.RESET`


### Terminal Control – the `Term` class

`Term` exposes commonly used non-styling ANSI sequences for cursor- and screen-control.<br>
These are plain strings (or string-returning helpers),
so they can be passed directly into a `S(…)` call or written to `sys.stdout`:

*   `CLEAR_LINE`                         – Erase the entire current line.
*   `CLEAR_LINE_TO_END`                  – Erase from the cursor to the end of the line.
*   `CLEAR_LINE_TO_START`                – Erase from the line start to the cursor.
*   `CLEAR_SCREEN`                       – Erase the whole screen.
*   `CLEAR_SCREEN_TO_END`                – Erase from the cursor to the end of the screen.
*   `CLEAR_SCREEN_TO_START`              – Erase from the screen start to the cursor.
*   `CLEAR_SCROLLBACK`                   – Erase the scrollback buffer.
*   `CUR_HIDE` / `CUR_SHOW`              – Hide/show the cursor.
*   `CUR_HOME`                           – Move cursor to home position (0, 0).
*   `CUR_SAVE` / `CUR_RESTORE`           – Save/restore cursor position (ANSI.SYS).
*   `CUR_SAVE_DEC` / `CUR_RESTORE_DEC`   – Save/restore cursor position (DEC ESC 7/8).
*   `ALT_SCREEN`                         – Enter the alternate screen buffer.
*   `MAIN_SCREEN`                        – Leave the alternate screen buffer.
*   `BELL`                               – Terminal bell signal (`\\x07`).
*   `up(n)`                              – Move the cursor up by `n` rows.
*   `down(n)`                            – Move the cursor down by `n` rows.
*   `right(n)`                           – Move the cursor right by `n` columns.
*   `left(n)`                            – Move the cursor left by `n` columns.
*   `row(row)`                           – Move the cursor to an absolute row position (1-based, VPA).
*   `col(col)`                           – Move the cursor to an absolute column position (1-based, CHA).
*   `move(row, col)`                     – Move the cursor to an absolute `(row, col)` position.
*   `scroll_up(n)`                       – Scroll page up by `n` lines.
*   `scroll_down(n)`                     – Scroll page down by `n` lines.
*   `title(text)`                        – Set the terminal window / tab title (OSC 2).
*   `cursor_shape(shape)`                – Change cursor shape (DECSCUSR 1-6).
*   `clipboard_copy(text)`               – Copy text to system clipboard via OSC 52.
*   `cwd(path)`                          – Notify terminal of current working directory via OSC 7.
"""

from __future__ import annotations

from . import color as _color_module
from .base.types import Hexa, Hsla, Rgba

import base64 as _base64
import ctypes as _ctypes
import math as _math
import os as _os
import sys as _sys
import textwrap as _textwrap
from contextlib import suppress as _suppress
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, Final, Literal, Self, TextIO, cast, overload
import regex as _rx

if TYPE_CHECKING:
    from .color import _ColorBase, hexa, rgba

    import sys
    from collections.abc import Iterable, Iterator, Sequence

    if sys.version_info >= (3, 13):
        from typing import TypeIs
    else:
        from typing_extensions import TypeIs

_terminal_configured: bool = False
"""Whether the terminal was already configured to be able to interpret and render ANSI styling."""

_ANSI_SEQ_RX: Final[_rx.Pattern[str]] = _rx.compile(r"\x1b(?:\].*?(?:\x1b\\|\x07)|\[[0-?]*[ -/]*[@-~]|[@-Z\\-_c]|[0-9=><])")
"""Compiled regex pattern matching any ANSI escape sequence (CSI, OSC, or single-character)."""

_CHAR_OR_ANSI_RX: Final[_rx.Pattern[str]] = _rx.compile(
    r"(\x1b(?:\].*?(?:\x1b\\|\x07)|\[[0-?]*[ -/]*[@-~]|[@-Z\\-_c]|[0-9=><])|.)"
)
"""Compiled regex pattern matching either a single ANSI escape sequence or an arbitrary character."""

_WORD_OR_ANSI_RX: Final[_rx.Pattern[str]] = _rx.compile(
    r"(\x1b(?:\].*?(?:\x1b\\|\x07)|\[[0-?]*[ -/]*[@-~]|[@-Z\\-_c]|[0-9=><])|\s+|\S+)"
)
"""Compiled regex pattern matching an ANSI escape sequence, whitespace run, or non-whitespace word."""

# fmt:off
_RESET_MAP: Final[dict[int, int]] = {
    # Text styles:
    1: 22, 2: 22, 3: 23, 4: 24, 5: 25, 7: 27, 8: 28, 9: 29, 21: 24,
    # FG colors:
    30: 39, 31: 39, 32: 39, 33: 39, 34: 39, 35: 39, 36: 39, 37: 39,
    # BG colors:
    40: 49, 41: 49, 42: 49, 43: 49, 44: 49, 45: 49, 46: 49, 47: 49,
    # Bright FG colors:
    90: 39, 91: 39, 92: 39, 93: 39, 94: 39, 95: 39, 96: 39, 97: 39,
    # Bright BG colors:
    100: 49, 101: 49, 102: 49, 103: 49, 104: 49, 105: 49, 106: 49, 107: 49,
}
"""Mapping from ANSI style integer to its matching reset integer.\n
Codes that fully reset everything (`0`) or have no useful specific reset are intentionally omitted."""
# fmt:on

_STANDARD_SEQS: Final[dict[int, tuple[tuple[str, ...], tuple[str, ...]]],] = {
    cid: ((f"\x1b[{cid}m",), (f"\x1b[{reset}m",)) for cid, reset in _RESET_MAP.items()
}
"""Pre-computed `(opens, closes)` tuple pairs for every standard single-code SGR style.\n
Used as a fast path in `_build_open_close` to avoid per-call list and string allocations."""

_CUBE_STEPS: Final[tuple[int, ...]] = (0, 95, 135, 175, 215, 255)
"""RGB channel steps for the 6×6×6 color cube in 256-color palettes."""  # ruff:ignore[ambiguous-unicode-character-string]

_CURSOR_SHAPES: Final[dict[str, int]] = {
    "blinking_bar": 5,
    "blinking_block": 1,
    "blinking_underline": 3,
    "steady_bar": 6,
    "steady_block": 2,
    "steady_underline": 4,
}
"""Mapping from cursor shape description names to their corresponding DECSCUSR numeric codes."""

_ANSI16_TO_RGB: Final[dict[int, tuple[int, int, int]]] = {
    30: (0, 0, 0),
    31: (205, 49, 49),
    32: (13, 188, 121),
    33: (229, 229, 16),
    34: (36, 114, 200),
    35: (188, 63, 188),
    36: (17, 168, 205),
    37: (229, 229, 229),
    90: (102, 102, 102),
    91: (241, 76, 76),
    92: (35, 209, 139),
    93: (245, 245, 67),
    94: (59, 142, 234),
    95: (214, 112, 214),
    96: (41, 184, 219),
    97: (255, 255, 255),
}
"""RGB color coordinates corresponding to the standard 16 ANSI colors."""


# ***************************************************** INTERNAL HELPERS ******************************************************


def _ansi256_to_rgb(code: int, /) -> tuple[int, int, int]:
    """Internal function to convert an ANSI 256-color palette index in range `[16, 255]` to an `(R, G, B)` tuple."""

    if code < 232:
        offset = code - 16
        return (_CUBE_STEPS[offset // 36], _CUBE_STEPS[(offset // 6) % 6], _CUBE_STEPS[offset % 6])

    gray = 8 + (code - 232) * 10
    return (gray, gray, gray)


def _rgb_to_ansi256(red: int, green: int, blue: int, /) -> int:
    """Internal function to map an RGB color to the closest ANSI 256-color palette index."""

    if red == green == blue:
        if red < 4:
            return 16
        elif red > 243:
            return 231
        return 232 + int((red - 8) / 10 + 0.5)

    def _closest_cube_index(val: int, /) -> int:
        """Helper function to find the closest index in the 6×6×6 color cube."""

        if val < 48:
            return 0
        elif val < 115:
            return 1
        elif val < 155:
            return 2
        elif val < 195:
            return 3
        elif val < 235:
            return 4
        return 5

    return 16 + 36 * _closest_cube_index(red) + 6 * _closest_cube_index(green) + _closest_cube_index(blue)


def _build_open_close(group: _StyleGroup, /) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Internal function to build the opening and closing ANSI sequences for a `_StyleGroup`.\n
    ----------------------------------------------------------------------------------------------------
    Returns a `(opens, closes)` pair of tuples. Multiple opens / closes are emitted
    only when both an OSC 8 hyperlink and SGR codes are present (OSC wraps SGR)."""

    return _BuildOpenClose(group).build()


def _config_terminal() -> None:
    """Internal function to configure the terminal to be able to interpret and render ANSI styling.\n
    This function only does something the first time it is called. Subsequent calls are no-ops."""

    global _terminal_configured
    if _terminal_configured:
        return

    _sys.stdout.flush()

    if _os.name == "nt":
        with _suppress(Exception):
            kernel32 = _ctypes.windll.kernel32  # type: ignore[attr-defined]
            handle = kernel32.GetStdHandle(-11)  # pyright:ignore[reportUnknownMemberType,reportUnknownVariableType]
            mode = _ctypes.c_ulong()
            kernel32.GetConsoleMode(handle, _ctypes.byref(mode))  # pyright:ignore[reportUnknownMemberType]
            kernel32.SetConsoleMode(handle, mode.value | 0x0004)  # pyright:ignore[reportUnknownMemberType]

    _terminal_configured = True


class _BuildOpenClose:
    """Internal, callable helper class to build the opening and closing ANSI sequences for a `_StyleGroup`."""

    __slots__: tuple[str, ...] = ("group", "link_url", "sgr_close", "sgr_open")

    def __init__(self, group: _StyleGroup, /) -> None:
        self.group: _StyleGroup = group
        self.sgr_open: list[str] = []
        self.sgr_close: list[str] = []
        self.link_url: str | None = None

    def build(self) -> tuple[tuple[str, ...], tuple[str, ...]]:
        """Build the opening and closing ANSI sequences for the given `_StyleGroup`.\n
        ----------------------------------------------------------------------------------------------------
        Returns a `(opens, closes)` pair of tuples. Multiple opens / closes are emitted
        only when both an OSC 8 hyperlink and SGR codes are present (OSC wraps SGR)."""

        if (
            len(codes := self.group._codes) == 1
            and type(codes[0]) is _Style
            and (cached := _STANDARD_SEQS.get(int(codes[0]))) is not None
        ):
            return cached

        for code in self.group:
            self._process_code(code)

        return self._build_result()

    def _process_code(self, code: BaseStyle, /) -> None:
        """Internal helper to process a single style code and append its opening and closing sequences."""

        if isinstance(code, _Link):
            self.link_url = code._url

        elif isinstance(code, _ColorStyle):
            if code._bg:
                self.sgr_open.append(f"48;2;{code._red};{code._green};{code._blue}")
                self.sgr_close.append("49")
            else:
                self.sgr_open.append(f"38;2;{code._red};{code._green};{code._blue}")
                self.sgr_close.append("39")

        elif isinstance(code, _Color256Style):
            if code._bg:
                self.sgr_open.append(f"48;5;{code._code}")
                self.sgr_close.append("49")
            else:
                self.sgr_open.append(f"38;5;{code._code}")
                self.sgr_close.append("39")

        elif isinstance(code, _GradientStyle):
            pass

        else:
            self.sgr_open.append(str(cid := int(code)))
            if (reset := _RESET_MAP.get(cid)) is not None:
                self.sgr_close.append(str(reset))

    def _build_result(self) -> tuple[tuple[str, ...], tuple[str, ...]]:
        """Internal helper to build the final `(opens, closes)` result tuples."""

        seen: set[str] = set()
        dedup_close: list[str] = []

        for close_code in self.sgr_close:
            if close_code not in seen:
                seen.add(close_code)
                dedup_close.append(close_code)

        opens: list[str] = []
        closes: list[str] = []

        if self.link_url is not None:
            opens.append(f"\x1b]8;;{self.link_url}\x1b\\")
        if self.sgr_open:
            opens.append(f"\x1b[{';'.join(self.sgr_open)}m")
        if dedup_close:
            closes.append(f"\x1b[{';'.join(dedup_close)}m")
        if self.link_url is not None:
            closes.append("\x1b]8;;\x1b\\")

        return tuple(opens), tuple(closes)


def _render_styled(
    opens: tuple[str, ...],
    closes: tuple[str, ...],
    segments: tuple[Renderable, ...],
    /,
    *,
    reset_codes: tuple[int, ...] = (),
) -> S:
    """Internal helper to construct an `S` object wrapped in opening and closing ANSI sequences."""

    ansi_parts: list[str] = list(opens)
    for segment in segments:
        _render_segment(segment, ansi_parts)
    for close in closes:
        ansi_parts.append(close)

    return S("".join(ansi_parts), _reset_codes=reset_codes)


def _render_segment(segment: object, ansi_parts: list[str], /) -> None:
    """Internal helper to recursively render a segment into `ansi_parts`."""

    if isinstance(segment, str):
        ansi_parts.append(segment)
        return

    elif isinstance(segment, _SBase):
        ansi_parts.append(segment.ansi)
        return

    elif isinstance(segment, tuple):
        for tuple_part in cast("tuple[object, ...]", segment):
            _render_segment(tuple_part, ansi_parts)
        return

    else:
        # Fallback; coerce unknown objects to str:
        ansi_parts.append(str(segment))


def _style_reset_codes(style: BaseStyle, /) -> tuple[int, ...]:
    """Internal helper to determine the SGR reset codes associated with a style."""

    if isinstance(style, _Style):
        if (reset := _RESET_MAP.get(style._value)) is not None:
            return (reset,)
        return ()

    elif isinstance(style, (_ColorStyle, _Color256Style)):
        return (49 if style._bg else 39,)

    return ()


def _segment_has_reset_code(segment: object, target_code: int, /) -> bool:
    """Internal helper to check if a segment or nested tuple has a matching reset code."""

    if isinstance(segment, S):
        return target_code in segment._reset_codes

    elif isinstance(segment, tuple):
        for item in cast("tuple[object, ...]", segment):
            if _segment_has_reset_code(item, target_code):
                return True

    return False


def _segment_ends_with_reset_code(segment: object, target_code: int, /) -> bool:
    """Internal helper to check if a segment or nested tuple ends with a matching reset code."""

    if isinstance(segment, S):
        return target_code in segment._reset_codes

    elif isinstance(segment, tuple) and segment:
        return _segment_ends_with_reset_code(cast("tuple[object, ...]", segment)[-1], target_code)

    return False


def _collect_outer_resets(outer_styles: tuple[BaseStyle, ...], /) -> tuple[tuple[int, BaseStyle], ...]:
    """Collects unique outer reset codes paired with their effective style in reverse order."""

    outer_resets: list[tuple[int, BaseStyle]] = []
    seen_resets: set[int] = set()

    for style in reversed(outer_styles):
        for reset_code in _style_reset_codes(style):
            if reset_code not in seen_resets:
                seen_resets.add(reset_code)
                outer_resets.append((reset_code, style))

    outer_resets.reverse()
    return tuple(outer_resets)


def _has_matching_reset(segments: tuple[Renderable, ...], outer_resets: tuple[tuple[int, BaseStyle], ...], /) -> bool:
    """Returns True if any segment matches any outer reset code."""

    for reset_code, _style in outer_resets:
        for segment in segments:
            if _segment_has_reset_code(segment, reset_code):
                return True

    return False


def _resolve_styles_to_restore(segment: object, outer_resets: tuple[tuple[int, BaseStyle], ...], /) -> AnyStyle | None:
    """Resolves the style or composite style group to restore behind a segment."""

    styles_to_restore: list[BaseStyle] = []

    for reset_code, restore_style in outer_resets:
        if _segment_ends_with_reset_code(segment, reset_code):
            styles_to_restore.append(restore_style)

    if not styles_to_restore:
        return None
    elif len(styles_to_restore) == 1:
        return styles_to_restore[0]

    return _StyleGroup(*styles_to_restore)


def _restore_reset_styles(outer_styles: tuple[BaseStyle, ...], segments: tuple[Renderable, ...], /) -> tuple[Renderable, ...]:
    """Internal helper to restore active outer styles behind nested auto-resetting segments."""

    if not (outer_resets := _collect_outer_resets(outer_styles)):
        return segments

    if not _has_matching_reset(segments, outer_resets):
        return segments

    result: list[Renderable] = []
    segment_count = len(segments)

    for i, segment in enumerate(segments):
        if isinstance(segment, tuple):
            result.append(_restore_reset_styles(outer_styles, cast("tuple[Renderable, ...]", segment)))
        else:
            result.append(segment)

        if i < segment_count - 1 and (restore_style := _resolve_styles_to_restore(segment, outer_resets)) is not None:
            result.append(restore_style)

    return tuple(result)


# ******************************************************** BASE CLASS *********************************************************


class _SBase:
    """Common base class for styled text (`S`)
    and bare ANSI style builders (`_Style`, `_ColorStyle`, `_Link`, `_StyleGroup`).\n
    ----------------------------------------------------------------------------------------------------
    Provides all string inspection properties, mathematical operators, and text formatting methods."""

    __slots__: tuple[str, ...] = ("ansi",)
    ansi: str

    def __call__(self, *text: Renderable) -> S:
        """Dummy method required to prevent a MyPyC C-struct memory layout bug.\n
        ----------------------------------------------------------------------------------------------------
        If subclasses define `__call__` but the native base class does not,
        MyPyC injects a `vectorcallfunc` pointer into the subclass struct.<br>
        This breaks the memory offset for inherited fields (like `ansi`),
        causing a segmentation fault when accessed."""

        raise NotImplementedError

    # ************************* PROPERTIES **************************

    @property
    def raw(self) -> str:
        """The rendered output with every ANSI escape sequence stripped (the "plain" text)."""

        return _ANSI_SEQ_RX.sub("", self.ansi)

    @property
    def code_positions(self) -> tuple[tuple[int, str], ...]:
        """A tuple of `(position, sequence)` pairs giving the
        start offset of every ANSI escape sequence inside `ansi`."""

        return tuple([(match.start(), match.group()) for match in _ANSI_SEQ_RX.finditer(self.ansi)])

    @property
    def raw_code_positions(self) -> tuple[tuple[int, str], ...]:
        """A tuple of `(position, sequence)` pairs giving the start offset of every ANSI escape
        sequence relative to the plain `raw` text (i.e., as if all escape sequences were removed).\n
        ----------------------------------------------------------------------------------------------------
        This is the counterpart to `code_positions`,
        which reports offsets inside the rendered `ansi` string.<br>
        It is useful for re-inserting the styling after processing the plain text
        (e.g., wrapping or splitting it), since the positions stay valid against `raw`."""

        result: list[tuple[int, str]] = []
        consumed = 0

        for match in _ANSI_SEQ_RX.finditer(self.ansi):
            result.append((match.start() - consumed, match.group()))
            consumed += len(match.group())

        return tuple(result)

    # ************************** OPERATORS **************************

    def __or__(self, other: AnyStyle) -> _StyleGroup:
        """Combines this style with another code or group via `|`."""

        self_codes = self._codes if isinstance(self, _StyleGroup) else (cast("BaseStyle", self),)
        other_codes = other._codes if isinstance(other, _StyleGroup) else (other,)
        return _StyleGroup(*self_codes, *other_codes)

    def __ror__(self, other: BaseStyle) -> _StyleGroup:
        """Combines this style with another code or group via `|`."""

        self_codes = self._codes if isinstance(self, _StyleGroup) else (cast("BaseStyle", self),)
        return _StyleGroup(other, *self_codes)

    def __add__(self, other: Renderable, /) -> S:
        """Concatenate an `_SBase` object with another renderable object."""

        return S(self, other)

    def __radd__(self, other: Renderable, /) -> S:
        """Concatenate another renderable object with an `_SBase` object from the left."""

        return S(other, self)

    def __iadd__(self, other: Renderable, /) -> S:
        """Append another renderable object in place (`+=`)."""

        self.ansi = S(self, other).ansi
        return cast("S", self)

    def __mul__(self, n: int, /) -> S:
        """Repeat this `_SBase` object `n` times."""

        return S(*([self] * max(0, n)), _reset_codes=(self._reset_codes if isinstance(self, S) else ()))

    def __rmul__(self, n: int, /) -> S:
        """Repeat this `_SBase` object `n` times from the left."""

        return self * n

    def __len__(self) -> int:
        """Return the visible length (character count of plain `raw` text)."""

        return len(self.raw)

    def __getitem__(self, key: slice, /) -> S:
        """Slice the styled text by character positions in the plain unstyled (`raw`) text.<br>
        ANSI escape codes are preserved and redistributed over the sliced segment."""

        raw_text = self.raw
        start, stop, step = key.indices(len(raw_text))

        if step != 1:
            raise ValueError("Styled text slicing only supports a step of 1.")

        return self._slice(start, stop, raw_text, self.raw_code_positions)

    def _slice(self, start: int, stop: int, raw_text: str, raw_code_positions: tuple[tuple[int, str], ...]) -> S:
        """Internal fast-path for slicing with precomputed `raw_text` and `raw_code_positions`."""

        if start >= stop:
            return S("")

        prefix_codes: list[str] = []
        middle_codes: list[tuple[int, str]] = []
        suffix_codes: list[str] = []

        for pos, seq in raw_code_positions:
            if pos <= start:
                prefix_codes.append(seq)
            elif start < pos < stop:
                middle_codes.append((pos - start, seq))
            else:
                suffix_codes.append(seq)

        sliced_raw = raw_text[start:stop]
        result_parts: list[str] = list(prefix_codes)
        last_index = 0

        for pos, seq in middle_codes:
            result_parts.append(sliced_raw[last_index:pos])
            result_parts.append(seq)
            last_index = pos

        result_parts.append(sliced_raw[last_index:])
        result_parts.extend(suffix_codes)

        return S("".join(result_parts), _reset_codes=(self._reset_codes if isinstance(self, S) else ()))

    def __contains__(self, item: object, /) -> bool:
        """Check if a substring or plain string is contained in the rendered output or plain text."""

        if isinstance(item, str):
            return item in self.ansi or item in self.raw

        return False

    def __eq__(self, other: object) -> bool:
        """Returns `True` if `other` is an `_SBase` instance or string with identical ANSI text."""

        if isinstance(other, _SBase):
            return self.ansi == other.ansi
        elif isinstance(other, str):
            return self.ansi == other

        return False

    def __bool__(self) -> bool:
        """Return `True` if the unstyled plain text is non-empty."""

        return bool(self.raw)

    def __str__(self) -> str:
        """Return the fully rendered ANSI string."""

        return self.ansi

    def __repr__(self) -> str:
        """Return the debug string representation of the `_SBase` object."""

        return f"S({self.ansi!r})"

    # *************************** METHODS ***************************

    def join(self, iterable: Iterable[Renderable], /) -> S:
        """Join a sequence of segments using the current object as the separator.\n
        ----------------------------------------------------------------------------------------------------
        *   `iterable` – The segments to join, e.g., a list of strings or `S` objects.\n
        ----------------------------------------------------------------------------------------------------
        #### Example Usage

        ```python
        S(", ").join(["Apple", S.BOLD("Banana"), "Cherry"]).print()
        ```

        <!-- DOCS: <TerminalOutput>
        Apple, <span class="b">Banana</span>, Cherry
        </TerminalOutput> -->"""

        return S(*iterable, sep=self.ansi)

    def ljust(self, width: int, fill_char: Renderable = " ", /) -> S:
        """Return the object left justified in a string of length `width` (visible chars).\n
        ----------------------------------------------------------------------------------------------------
        *   `width` – The total visible width of the resulting string.
        *   `fill_char` – The character to use for padding (default is a space).\n
        ----------------------------------------------------------------------------------------------------
        #### Example Usage

        ```python
        S.RED("Text").ljust(10, ".").print()
        ```

        <!-- DOCS: <TerminalOutput>
        <span class="red">Text</span>......
        </TerminalOutput> -->"""

        if (raw_len := len(self.raw)) >= width:
            return cast("S", self) if type(self) is S else S(self)

        return self + fill_char * (width - raw_len)

    def rjust(self, width: int, fill_char: Renderable = " ", /) -> S:
        """Return the object right justified in a string of length `width` (visible chars).\n
        ----------------------------------------------------------------------------------------------------
        *   `width` – The total visible width of the resulting string.
        *   `fill_char` – The character to use for padding (default is a space).\n
        ----------------------------------------------------------------------------------------------------
        #### Example Usage

        ```python
        S.GREEN("Text").rjust(10, ".").print()
        ```

        <!-- DOCS: <TerminalOutput>
        ......<span class="green">Text</span>
        </TerminalOutput> -->"""

        if (raw_len := len(self.raw)) >= width:
            return cast("S", self) if type(self) is S else S(self)

        return fill_char * (width - raw_len) + self

    def center(self, width: int, fill_char: Renderable = " ", /) -> S:
        """Return the object centered in a string of length `width` (visible chars).\n
        ----------------------------------------------------------------------------------------------------
        *   `width` – The total visible width of the resulting string.
        *   `fill_char` – The character to use for padding (default is a space).\n
        ----------------------------------------------------------------------------------------------------
        #### Example Usage

        ```python
        S.BOLD("Text").center(10, "-").print()
        ```

        <!-- DOCS: <TerminalOutput>
        ---<span class="b">Text</span>---
        </TerminalOutput> -->"""

        if (raw_len := len(self.raw)) >= width:
            return cast("S", self) if type(self) is S else S(self)

        total_pad = width - raw_len
        left_pad = total_pad // 2
        right_pad = total_pad - left_pad

        return fill_char * left_pad + self + fill_char * right_pad

    def wrap(self, width: int, /) -> list[S]:
        """Wrap the object to fit within a given line width (in visible characters),
        preserving ANSI styling across all wrapped lines.\n
        ----------------------------------------------------------------------------------------------------
        *   `width` – The maximum visible width of each line."""

        if not (raw_text := self.raw) or width <= 0:
            return [cast("S", self) if type(self) is S else S(self)]

        raw_code_positions = self.raw_code_positions
        result: list[S] = []
        current_offset = 0

        for paragraph in raw_text.split("\n"):
            if not paragraph:
                result.append(S(""))
                current_offset += 1
                continue

            for line_idx, line in enumerate(
                _textwrap.wrap(paragraph, width=width, replace_whitespace=False, drop_whitespace=False)
            ):
                line_len = len(line)
                lead_strip = (line_len - len(line.lstrip(" \t"))) if line_idx > 0 else 0
                trail_strip = line_len - len(line.rstrip(" \t"))

                slice_start = current_offset + lead_strip
                slice_stop = current_offset + line_len - trail_strip

                if slice_start < slice_stop:
                    result.append(self._slice(slice_start, slice_stop, raw_text, raw_code_positions))
                else:
                    result.append(S(""))

                current_offset += line_len

            current_offset += 1

        return result

    def print(self, /, *, end: str = "\n", flush: bool = True, file: TextIO | None = None) -> None:
        """Write the rendered ANSI string straight to `sys.stdout`
        (configuring the terminal for ANSI on first use) or to a custom file-like object.\n
        ----------------------------------------------------------------------------------------------------
        *   `end` – The string to append at the end of the output (default `"\\n"`).
        *   `flush` – Whether to flush the output stream after writing (default `True`).
        *   `file` – The file-like object to write to (default `sys.stdout`).\n
        ----------------------------------------------------------------------------------------------------
        #### Example Usage

        ```python
        S.GREEN("Operation successful!").print()
        ```

        <!-- DOCS: <TerminalOutput>
        <span class="green">Operation successful!</span>
        </TerminalOutput> -->"""

        if file is None:
            _config_terminal()
            out = _sys.stdout
        else:
            out = file

        out.write(self.ansi + end)

        if flush:
            out.flush()

    def input(self, /, *, reset_ansi: bool = False) -> str:
        """Use the rendered ANSI string as an input prompt and return the user's input.\n
        ----------------------------------------------------------------------------------------------------
        *   `reset_ansi` – If true, all ANSI styling will be reset after
            the user confirmed the input and the program continues to run.\n
        ----------------------------------------------------------------------------------------------------
        #### Example Usage

        ```python
        S.BOLD("Enter value: ").input()
        ```

        <!-- DOCS: <TerminalOutput>
        <span class="b">Enter value: </span>
        </TerminalOutput> -->"""

        _config_terminal()
        user_input = input(self.ansi)

        if reset_ansi:
            _sys.stdout.write("\x1b[0m")

        return user_input


# ***************************************************** STYLE SUBCLASSES ******************************************************


class _Style(_SBase):
    """A single ANSI style integer.\n
    ----------------------------------------------------------------------------------------------------
    Supports two operators:
    *   `|`  combines two or more codes into a `_StyleGroup` → `S.BOLD | S.RED`
    *   `()` applies the code to text, auto-resetting after → `S.BOLD("hello")`"""

    __slots__: tuple[str, ...] = ("_oc", "_value")
    _oc: tuple[tuple[str, ...], tuple[str, ...]]

    def __init__(self, value: int, /) -> None:
        self._value: int = value
        self.ansi = f"\x1b[{value}m"

    def __int__(self) -> int:
        return self._value

    def __str__(self) -> str:
        return str(self._value)

    def __repr__(self) -> str:
        return f"_Style({self._value})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, int):
            return self._value == other
        elif isinstance(other, _Style):
            return self._value == other._value
        elif isinstance(other, (_SBase, str)):
            return super().__eq__(other)

        return NotImplemented

    def __hash__(self) -> int:
        return hash(self._value)

    def __call__(self, *text: Renderable) -> S:
        """Applies this style code to the given text, auto-resetting after."""

        try:
            oc = self._oc
        except AttributeError:
            cached = _STANDARD_SEQS.get(int(self))
            oc = _build_open_close(_StyleGroup(self)) if cached is None else cached
            self._oc = oc

        return _render_styled(
            oc[0],
            oc[1],
            _restore_reset_styles((self,), text),
            reset_codes=_style_reset_codes(self),
        )

    def as_fg(self) -> _Style:
        """Convert to the corresponding foreground style."""

        return self

    def as_bg(self) -> _Style:
        """Convert to the corresponding background style."""

        return self


class _ColorStyle(_SBase):
    """A 24-bit true-color style – foreground or background.\n
    ----------------------------------------------------------------------------------------------------
    >>> S.rgb(112, 118, 255)("text")             # Custom FG color
    >>> S.BG.rgb(112, 118, 255)("text")          # Custom BG color
    >>> S.hex("#7075FF")("text")                 # Hex FG color
    >>> (S.BOLD | S.rgb(112, 118, 255))("text")  # Combined with style"""

    __slots__: tuple[str, ...] = ("_bg", "_blue", "_close_seq", "_green", "_open_seq", "_red")

    def __init__(self, red: int, green: int, blue: int, /, *, bg: bool = False) -> None:
        self._red: int = red
        self._green: int = green
        self._blue: int = blue
        self._bg: bool = bg

        if bg:
            self._open_seq: str = f"\x1b[48;2;{red};{green};{blue}m"
            self._close_seq: str = "\x1b[49m"
        else:
            self._open_seq = f"\x1b[38;2;{red};{green};{blue}m"
            self._close_seq = "\x1b[39m"

        self.ansi = self._open_seq

    @classmethod
    def from_hex(cls: type[Self], color: str | int | hexa, /, *, bg: bool | None = None) -> Self:
        """Create a color style from a HEX string, HEX integer, or `hexa` object."""

        if isinstance(color, int):
            if not (0x000000 <= color <= 0xFFFFFF):
                raise ValueError(f"Expected 24-bit HEX integer in range [0x000000, 0xFFFFFF] inclusive, got 0x{color:X}")

            red, green, blue = (color >> 16) & 0xFF, (color >> 8) & 0xFF, color & 0xFF
            return cls(red, green, blue, bg=bg) if bg is not None else cls(red, green, blue)

        if (hex_str := str(color).strip().lstrip("#")).lower().startswith("0x"):
            hex_str = hex_str[2:]
        if len(hex_str) == 3:
            hex_str = hex_str[0] * 2 + hex_str[1] * 2 + hex_str[2] * 2

        if bg is None:
            return cls(int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16))

        return cls(int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16), bg=bg)

    def __call__(self, *text: Renderable) -> S:
        """Applies this color style to the given text, auto-resetting after."""

        return _render_styled(
            (self._open_seq,),
            (self._close_seq,),
            _restore_reset_styles((self,), text),
            reset_codes=(49 if self._bg else 39,),
        )

    def __repr__(self) -> str:
        """Returns a string representation of this color style, indicating
        whether it's foreground or background and its RGB values."""

        return f"_ColorStyle({'bg' if self._bg else 'fg'} {self._red},{self._green},{self._blue})"

    def __eq__(self, other: object) -> bool:
        """Returns `True` if `other` is a `_ColorStyle` with identical RGB values and background flag."""

        if isinstance(other, _ColorStyle):
            return (
                self._red == other._red and self._green == other._green and self._blue == other._blue and self._bg == other._bg
            )
        elif isinstance(other, (_SBase, str)):
            return super().__eq__(other)

        return False

    def __hash__(self) -> int:
        return hash((self._red, self._green, self._blue, self._bg))

    def as_fg(self) -> _FgColorStyle:
        """Convert to the corresponding foreground color style."""

        return _FgColorStyle(self._red, self._green, self._blue)

    def as_bg(self) -> _BgColorStyle:
        """Convert to the corresponding background color style."""

        return _BgColorStyle(self._red, self._green, self._blue)

    def as_text_fg(self) -> _FgColorStyle:
        """Returns black or white foreground color for optimal contrast on this color."""

        luminance = 0.2126 * self._red + 0.7152 * self._green + 0.0722 * self._blue
        return _FgColorStyle(255, 255, 255) if luminance < 128 else _FgColorStyle(0, 0, 0)

    def as_text_bg(self) -> _BgColorStyle:
        """Returns black or white background color for optimal contrast behind this color."""

        luminance = 0.2126 * self._red + 0.7152 * self._green + 0.0722 * self._blue
        return _BgColorStyle(255, 255, 255) if luminance < 128 else _BgColorStyle(0, 0, 0)


class _FgColorStyle(_ColorStyle):
    """A 24-bit true-color foreground style."""

    __slots__: tuple[str, ...] = ()

    def as_fg(self) -> _FgColorStyle:
        """Convert to the corresponding foreground color style."""

        return self

    def as_bg(self) -> _BgColorStyle:
        """Convert to the corresponding background color style."""

        return _BgColorStyle(self._red, self._green, self._blue)

    def with_text_bg(self) -> _StyleGroup:
        """Returns a style group combining this foreground color with an optimal high-contrast text background."""

        return self | self.as_text_bg()


class _BgColorStyle(_ColorStyle):
    """A 24-bit true-color background style."""

    __slots__: tuple[str, ...] = ()

    def __init__(self, red: int, green: int, blue: int, /, *, bg: bool = True) -> None:
        super().__init__(red, green, blue, bg=bg)

    def as_fg(self) -> _FgColorStyle:
        """Convert to the corresponding foreground color style."""

        return _FgColorStyle(self._red, self._green, self._blue)

    def as_bg(self) -> _BgColorStyle:
        """Convert to the corresponding background color style."""

        return self

    def with_text_fg(self) -> _StyleGroup:
        """Returns a style group combining this background color with an optimal high-contrast text foreground."""

        return self | self.as_text_fg()


class _FgStyle(_Style):
    """A single ANSI foreground color code."""

    __slots__: tuple[str, ...] = ()

    def as_fg(self) -> _FgStyle:
        """Convert to the corresponding foreground color style."""

        return self

    def as_bg(self) -> _BgStyle:
        """Convert to the corresponding background color style."""

        return _BgStyle(self._value + 10)

    def as_text_fg(self) -> _FgColorStyle:
        """Returns black or white foreground color for optimal contrast on this foreground."""

        return _FgColorStyle(255, 255, 255) if self._value in {30, 90} else _FgColorStyle(0, 0, 0)

    def as_text_bg(self) -> _BgColorStyle:
        """Returns black or white background color for optimal contrast behind this foreground."""

        return _BgColorStyle(255, 255, 255) if self._value in {30, 90} else _BgColorStyle(0, 0, 0)

    def with_text_bg(self) -> _StyleGroup:
        """Returns a style group combining this foreground color with an optimal high-contrast text background."""

        return self | self.as_text_bg()


class _BgStyle(_Style):
    """A single ANSI background color code."""

    __slots__: tuple[str, ...] = ()

    def as_fg(self) -> _FgStyle:
        """Convert to the corresponding foreground color style."""

        return _FgStyle(self._value - 10)

    def as_bg(self) -> _BgStyle:
        """Convert to the corresponding background color style."""

        return self

    def as_text_fg(self) -> _FgColorStyle:
        """Returns black or white foreground color for optimal contrast on this background."""

        return _FgColorStyle(255, 255, 255) if self._value in {40, 100} else _FgColorStyle(0, 0, 0)

    def as_text_bg(self) -> _BgColorStyle:
        """Returns black or white background color for optimal contrast behind this background."""

        return _BgColorStyle(255, 255, 255) if self._value in {40, 100} else _BgColorStyle(0, 0, 0)

    def with_text_fg(self) -> _StyleGroup:
        """Returns a style group combining this background color with an optimal high-contrast text foreground."""

        return self | self.as_text_fg()


class _Color256Style(_SBase):
    """An 8-bit / 256-color palette style – foreground or background.\n
    ----------------------------------------------------------------------------------------------------
    *   `code` – The 256-color palette index in range [0, 255] inclusive.
    *   `bg` – Whether this style applies to the background instead of the foreground.\n
    ----------------------------------------------------------------------------------------------------
    >>> S.color256(196)("text")     # Red FG from 256-color palette
    >>> S.BG.color256(21)("text")   # Blue BG from 256-color palette"""

    __slots__: tuple[str, ...] = ("_bg", "_close_seq", "_code", "_open_seq")

    def __init__(self, code: int, /, *, bg: bool = False) -> None:
        if not (0 <= code <= 255):
            raise ValueError(f"Expected 256-color index in range [0, 255] inclusive, got {code!r}")

        self._code: int = code
        self._bg: bool = bg

        if bg:
            self._open_seq: str = f"\x1b[48;5;{code}m"
            self._close_seq: str = "\x1b[49m"
        else:
            self._open_seq = f"\x1b[38;5;{code}m"
            self._close_seq = "\x1b[39m"

        self.ansi = self._open_seq

    def __call__(self, *text: Renderable) -> S:
        """Applies this 256-color style to the given text, auto-resetting after."""

        return _render_styled(
            (self._open_seq,),
            (self._close_seq,),
            _restore_reset_styles((self,), text),
            reset_codes=(49 if self._bg else 39,),
        )

    def __repr__(self) -> str:
        """Returns a string representation of this 256-color style."""

        return f"_Color256Style({'bg' if self._bg else 'fg'} {self._code})"

    def __eq__(self, other: object) -> bool:
        """Returns `True` if `other` is a `_Color256Style` with identical color code and background flag."""

        if isinstance(other, _Color256Style):
            return self._code == other._code and self._bg == other._bg
        elif isinstance(other, (_SBase, str)):
            return super().__eq__(other)

        return False

    def __hash__(self) -> int:
        return hash((self._code, self._bg))

    def as_fg(self) -> _FgColor256Style:
        """Convert to the corresponding foreground color style."""

        return _FgColor256Style(self._code)

    def as_bg(self) -> _BgColor256Style:
        """Convert to the corresponding background color style."""

        return _BgColor256Style(self._code)

    def as_text_fg(self) -> _FgColorStyle:
        """Returns black or white foreground color for optimal contrast on this color."""

        if self._code < 16:
            return _FgColorStyle(255, 255, 255) if self._code in {0, 8} else _FgColorStyle(0, 0, 0)

        red, green, blue = _ansi256_to_rgb(self._code)
        luminance = 0.2126 * red + 0.7152 * green + 0.0722 * blue
        return _FgColorStyle(255, 255, 255) if luminance < 128 else _FgColorStyle(0, 0, 0)

    def as_text_bg(self) -> _BgColorStyle:
        """Returns black or white background color for optimal contrast behind this color."""

        if self._code < 16:
            return _BgColorStyle(255, 255, 255) if self._code in {0, 8} else _BgColorStyle(0, 0, 0)

        red, green, blue = _ansi256_to_rgb(self._code)
        luminance = 0.2126 * red + 0.7152 * green + 0.0722 * blue
        return _BgColorStyle(255, 255, 255) if luminance < 128 else _BgColorStyle(0, 0, 0)


class _FgColor256Style(_Color256Style):
    """A 256-color palette foreground style."""

    __slots__: tuple[str, ...] = ()

    def as_fg(self) -> _FgColor256Style:
        """Convert to the corresponding foreground color style."""

        return self

    def as_bg(self) -> _BgColor256Style:
        """Convert to the corresponding background color style."""

        return _BgColor256Style(self._code)

    def with_text_bg(self) -> _StyleGroup:
        """Returns a style group combining this foreground color with an optimal high-contrast text background."""

        return self | self.as_text_bg()


class _BgColor256Style(_Color256Style):
    """A 256-color palette background style."""

    __slots__: tuple[str, ...] = ()

    def __init__(self, code: int, /, *, bg: bool = True) -> None:
        super().__init__(code, bg=bg)

    def as_fg(self) -> _FgColor256Style:
        """Convert to the corresponding foreground color style."""

        return _FgColor256Style(self._code)

    def as_bg(self) -> _BgColor256Style:
        """Convert to the corresponding background color style."""

        return self

    def with_text_fg(self) -> _StyleGroup:
        """Returns a style group combining this background color with an optimal high-contrast text foreground."""

        return self | self.as_text_fg()


class _Link(_SBase):
    """An OSC 8 hyperlink. Combine with other styles via `|` to add text styling.\n
    ----------------------------------------------------------------------------------------------------
    >>> S.link("https://example.com")("click here")
    >>> (S.link("https://example.com") | S.BR.BLUE)("click here")"""

    __slots__: tuple[str, ...] = ("_close_seq", "_open_seq", "_url")

    def __init__(self, url: str | Path, /) -> None:
        self._url: str = url.resolve().as_uri() if isinstance(url, Path) else url
        self._open_seq: str = f"\x1b]8;;{self._url}\x1b\\"
        self._close_seq: str = "\x1b]8;;\x1b\\"
        self.ansi = self._open_seq

    def __call__(self, *text: Renderable) -> S:
        """Applies this link style to the given text, auto-resetting after."""

        return _render_styled((self._open_seq,), (self._close_seq,), text)

    def __repr__(self) -> str:
        """Returns a string representation of this link style, showing the URL it points to."""

        return f"_Link({self._url!r})"

    def __eq__(self, other: object) -> bool:
        """Returns `True` if `other` is a `_Link` pointing to the same URL."""

        if isinstance(other, _Link):
            return self._url == other._url
        elif isinstance(other, (_SBase, str)):
            return super().__eq__(other)

        return False

    def __hash__(self) -> int:
        return hash(self._url)

    def as_fg(self) -> _Link:
        """Convert to the corresponding foreground style."""

        return self

    def as_bg(self) -> _Link:
        """Convert to the corresponding background style."""

        return self


type ColorInput = _ColorStyle | _Color256Style | _Style | _ColorBase | Rgba | Hsla | Hexa
"""Supported color representations for ANSI gradient styles."""

type GradientStop = ColorInput | tuple[ColorInput, float | int]
"""A color stop for ANSI gradients: a color or a `(color, position)` tuple."""


def _color_obj_to_rgb(
    color: _Style | _ColorStyle | _Color256Style | _ColorBase | Rgba | Hsla | Hexa,
    /,
) -> tuple[int, int, int]:
    """Internal helper to convert style objects to an `(R, G, B)` tuple."""

    if isinstance(color, _ColorStyle):
        return (color._red, color._green, color._blue)

    elif isinstance(color, _Color256Style):
        return _ansi256_to_rgb(color._code)

    elif isinstance(color, _Style):
        if (30 <= (code_val := color._value) <= 37) or (90 <= code_val <= 97):
            return _ANSI16_TO_RGB.get(code_val, (255, 255, 255))
        elif (40 <= code_val <= 47) or (100 <= code_val <= 107):
            normalized_code = (code_val - 40 + 30) if (40 <= code_val <= 47) else (code_val - 100 + 90)
            return _ANSI16_TO_RGB.get(normalized_code, (255, 255, 255))
        return (255, 255, 255)

    return _color_module._extract_rgb_fast(color)


def _unwrap_gradient_colors(
    raw_colors: tuple[GradientStop | Sequence[GradientStop], ...],
    /,
) -> tuple[GradientStop, ...]:
    """Internal helper to unwrap nested collections of gradient stops."""

    unwrapped: tuple[GradientStop, ...] = cast("tuple[GradientStop, ...]", raw_colors)

    if len(raw_colors) == 1 and isinstance(raw_colors[0], (list, tuple)):
        is_rgb_tuple = False

        if len(first_item := raw_colors[0]) in {3, 4}:
            is_rgb_tuple = True
            for ch in first_item:
                if not isinstance(ch, int):
                    is_rgb_tuple = False
                    break

        if not is_rgb_tuple:
            unwrapped = tuple(cast("Sequence[GradientStop]", first_item))

    if not unwrapped:
        raise ValueError("At least one color must be provided for a gradient")

    return unwrapped


def _parse_gradient_stops(
    raw_colors: tuple[GradientStop | Sequence[GradientStop], ...],
    /,
) -> tuple[tuple[tuple[int, int, int], float], ...]:
    """Internal helper to parse raw color arguments into sorted `((red, green, blue), position)` stops."""

    raw_items: list[tuple[tuple[int, int, int], float | None]] = []

    for item in _unwrap_gradient_colors(raw_colors):
        if isinstance(item, tuple) and len(item) == 2:
            raw_items.append((_color_obj_to_rgb(item[0]), float(item[1])))
        else:
            raw_items.append((_color_obj_to_rgb(item), None))

    return _color_module._distribute_color_stops(raw_items)


class _GradientStyle(_SBase):
    """An ANSI gradient style that smoothly transitions colors across text or terminal blocks.\n
    ----------------------------------------------------------------------------------------------------
    *   `stops` – Parsed color stops `tuple[tuple[tuple[int, int, int], float], ...]`.
    *   `angle` – Direction angle in degrees (`0.0` = left-to-right, `90.0` = top-to-bottom).
    *   `space` – Color interpolation space
        (`"rgb"`, `"hsl"`, `"hsl_long"`, `"linear_rgb"`, `"oklab"`).
    *   `granularity` – Coloring granularity (`"char"`, `"word"`, or `"line"`).
    *   `skip_whitespace` – Whether to skip emitting color escape sequences over whitespace.
    *   `cell_aspect_ratio` – Font cell aspect ratio for 2D geometry correction (default `2.0`).
    *   `color_depth` – Color mode (`"truecolor"`, `"256"`, or `"auto"`).
    *   `bg` – Whether this gradient applies to the background instead of foreground."""

    __slots__: tuple[str, ...] = (
        "_angle",
        "_bg",
        "_cell_aspect_ratio",
        "_color_depth",
        "_granularity",
        "_skip_whitespace",
        "_space",
        "_stops",
    )

    def __init__(
        self,
        stops: tuple[tuple[tuple[int, int, int], float], ...],
        /,
        *,
        angle: float = 0.0,
        space: Literal["rgb", "hsl", "hsl_long", "linear_rgb", "oklab"] = "hsl",
        granularity: Literal["char", "word", "line"] = "char",
        skip_whitespace: bool = True,
        cell_aspect_ratio: float = 2.0,
        color_depth: Literal["truecolor", "256", "auto"] = "auto",
        bg: bool = False,
    ) -> None:
        self._stops: tuple[tuple[tuple[int, int, int], float], ...] = stops
        self._angle: float = float(angle) % 360.0
        self._space: Literal["rgb", "hsl", "hsl_long", "linear_rgb", "oklab"] = space
        self._granularity: Literal["char", "word", "line"] = granularity
        self._skip_whitespace: bool = skip_whitespace
        self._cell_aspect_ratio: float = cell_aspect_ratio
        self._color_depth: Literal["truecolor", "256", "auto"] = color_depth
        self._bg: bool = bg
        self.ansi = ""

    def __call__(self, *text: Renderable) -> S:
        """Applies this gradient style to the given text, auto-resetting after."""

        return self._render_gradient(text)

    def __repr__(self) -> str:
        """Returns a string representation of this gradient style."""

        return f"_GradientStyle({'bg' if self._bg else 'fg'} stops={len(self._stops)} angle={self._angle}°)"

    def __eq__(self, other: object) -> bool:
        """Returns `True` if `other` is a `_GradientStyle` with identical attributes."""

        if isinstance(other, _GradientStyle):
            return (
                self._stops == other._stops
                and self._angle == other._angle
                and self._space == other._space
                and self._granularity == other._granularity
                and self._skip_whitespace == other._skip_whitespace
                and self._cell_aspect_ratio == other._cell_aspect_ratio
                and self._color_depth == other._color_depth
                and self._bg == other._bg
            )
        elif isinstance(other, (_SBase, str)):
            return super().__eq__(other)

        return False

    def __hash__(self) -> int:
        return hash((
            self._stops,
            self._angle,
            self._space,
            self._granularity,
            self._skip_whitespace,
            self._cell_aspect_ratio,
            self._color_depth,
            self._bg,
        ))

    def as_fg(self) -> _GradientStyle:
        """Convert to the corresponding foreground gradient style."""

        if not self._bg:
            return self

        return _GradientStyle(
            self._stops,
            angle=self._angle,
            space=self._space,
            granularity=self._granularity,
            skip_whitespace=self._skip_whitespace,
            cell_aspect_ratio=self._cell_aspect_ratio,
            color_depth=self._color_depth,
            bg=False,
        )

    def as_bg(self) -> _GradientStyle:
        """Convert to the corresponding background gradient style."""

        if self._bg:
            return self

        return _GradientStyle(
            self._stops,
            angle=self._angle,
            space=self._space,
            granularity=self._granularity,
            skip_whitespace=self._skip_whitespace,
            cell_aspect_ratio=self._cell_aspect_ratio,
            color_depth=self._color_depth,
            bg=True,
        )

    def _color_seq_for_proj(
        self,
        proj_val: float,
        min_proj: float,
        proj_span: float,
        /,
        *,
        is_256: bool,
    ) -> str:
        """Internal helper to calculate the ANSI color escape sequence for a projected coordinate."""

        ratio_val = max(0.0, min(1.0, (proj_val - min_proj) / proj_span if proj_span > 1e-9 else 0.0))
        rgb_tuple = _color_module._resolve_color_stop(self._stops, ratio_val, space=self._space)

        if is_256:
            code_val = _rgb_to_ansi256(rgb_tuple[0], rgb_tuple[1], rgb_tuple[2])
            return f"\x1b[48;5;{code_val}m" if self._bg else f"\x1b[38;5;{code_val}m"

        return (
            f"\x1b[48;2;{rgb_tuple[0]};{rgb_tuple[1]};{rgb_tuple[2]}m"
            if self._bg
            else f"\x1b[38;2;{rgb_tuple[0]};{rgb_tuple[1]};{rgb_tuple[2]}m"
        )

    def _render_line_gradient(
        self,
        lines: list[str],
        /,
        *,
        max_width: int,
        cos_val: float,
        sin_val: float,
        min_proj: float,
        proj_span: float,
        is_256: bool,
        color_reset: str,
    ) -> list[str]:
        """Internal helper to render lines with line-level gradient granularity."""

        rendered_lines: list[str] = []

        for row_idx, line in enumerate(lines):
            if not line:
                rendered_lines.append("")
                continue

            proj_line = ((float(max_width - 1)) / 2.0) * cos_val + (float(row_idx) * self._cell_aspect_ratio) * sin_val
            color_seq = self._color_seq_for_proj(proj_line, min_proj, proj_span, is_256=is_256)
            rendered_lines.append(f"{color_seq}{line}{color_reset}")

        return rendered_lines

    def _render_word_gradient(
        self,
        lines: list[str],
        /,
        *,
        cos_val: float,
        sin_val: float,
        min_proj: float,
        proj_span: float,
        is_256: bool,
        color_reset: str,
    ) -> list[str]:
        """Internal helper to render lines with word-level gradient granularity."""

        rendered_lines: list[str] = []

        for row_idx, line in enumerate(lines):
            line_parts: list[str] = []
            col_x = 0
            current_color: str | None = None

            for match in _WORD_OR_ANSI_RX.finditer(line):
                if (token := match.group(1)).startswith("\x1b"):
                    line_parts.append(token)

                elif token.isspace():
                    if not self._bg and self._skip_whitespace:
                        if current_color is not None:
                            line_parts.append(color_reset)
                            current_color = None
                        line_parts.append(token)

                    else:
                        proj_word = float(col_x) * cos_val + (float(row_idx) * self._cell_aspect_ratio) * sin_val
                        color_seq = self._color_seq_for_proj(proj_word, min_proj, proj_span, is_256=is_256)
                        if color_seq != current_color:
                            line_parts.append(color_seq)
                            current_color = color_seq
                        line_parts.append(token)

                    col_x += len(token)

                else:
                    proj_word = float(col_x) * cos_val + (float(row_idx) * self._cell_aspect_ratio) * sin_val
                    color_seq = self._color_seq_for_proj(proj_word, min_proj, proj_span, is_256=is_256)
                    if color_seq != current_color:
                        line_parts.append(color_seq)
                        current_color = color_seq
                    line_parts.append(token)
                    col_x += len(token)

            if current_color is not None:
                line_parts.append(color_reset)

            rendered_lines.append("".join(line_parts))

        return rendered_lines

    def _render_char_gradient(
        self,
        lines: list[str],
        /,
        *,
        cos_val: float,
        sin_val: float,
        min_proj: float,
        proj_span: float,
        is_256: bool,
        color_reset: str,
    ) -> list[str]:
        """Internal helper to render lines with character-level gradient granularity."""

        rendered_lines: list[str] = []

        for row_idx, line in enumerate(lines):
            line_parts: list[str] = []
            col_x = 0
            current_color: str | None = None

            for match in _CHAR_OR_ANSI_RX.finditer(line):
                if (token := match.group(1)).startswith("\x1b"):
                    line_parts.append(token)

                elif token in {" ", "\t"} and not self._bg and self._skip_whitespace:
                    if current_color is not None:
                        line_parts.append(color_reset)
                        current_color = None
                    line_parts.append(token)
                    col_x += 1

                else:
                    proj_char = float(col_x) * cos_val + (float(row_idx) * self._cell_aspect_ratio) * sin_val
                    color_seq = self._color_seq_for_proj(proj_char, min_proj, proj_span, is_256=is_256)
                    if color_seq != current_color:
                        line_parts.append(color_seq)
                        current_color = color_seq
                    line_parts.append(token)
                    col_x += 1

            if current_color is not None:
                line_parts.append(color_reset)

            rendered_lines.append("".join(line_parts))

        return rendered_lines

    def _render_gradient(self, segments: tuple[Renderable, ...], extra_styles: tuple[BaseStyle, ...] = ()) -> S:
        """Internal worker method to render text segments with this gradient applied."""

        raw_parts: list[str] = []
        for segment in segments:
            _render_segment(segment, raw_parts)
        full_text = "".join(raw_parts)

        if not full_text:
            return S("")

        is_256 = self._color_depth == "256" or (
            self._color_depth == "auto"
            and not (_os.name == "nt" or _os.getenv("COLORTERM", "").lower() in {"truecolor", "24bit"})
        )

        color_reset = "\x1b[49m" if self._bg else "\x1b[39m"

        extra_open = ""
        extra_close = ""
        if extra_styles:
            extra_oc = _BuildOpenClose(_StyleGroup(*extra_styles)).build()
            extra_open = "".join(extra_oc[0])
            extra_close = "".join(extra_oc[1])

        lines = full_text.split("\n")
        num_rows = len(lines)
        visible_widths = [len(_ANSI_SEQ_RX.sub("", line)) for line in lines]
        max_width = max(visible_widths) if visible_widths else 0
        if max_width < 1:
            max_width = 1

        rad = _math.radians(self._angle)
        cos_val = _math.cos(rad)
        sin_val = _math.sin(rad)

        proj_00 = 0.0
        proj_w0 = float(max_width - 1) * cos_val
        proj_0h = float(num_rows - 1) * self._cell_aspect_ratio * sin_val
        proj_wh = proj_w0 + proj_0h

        min_proj = min([proj_00, proj_w0, proj_0h, proj_wh])
        max_proj = max([proj_00, proj_w0, proj_0h, proj_wh])
        proj_span = max_proj - min_proj

        if self._granularity == "line":
            rendered_lines = self._render_line_gradient(
                lines,
                max_width=max_width,
                cos_val=cos_val,
                sin_val=sin_val,
                min_proj=min_proj,
                proj_span=proj_span,
                is_256=is_256,
                color_reset=color_reset,
            )
        elif self._granularity == "word":
            rendered_lines = self._render_word_gradient(
                lines,
                cos_val=cos_val,
                sin_val=sin_val,
                min_proj=min_proj,
                proj_span=proj_span,
                is_256=is_256,
                color_reset=color_reset,
            )
        else:
            rendered_lines = self._render_char_gradient(
                lines,
                cos_val=cos_val,
                sin_val=sin_val,
                min_proj=min_proj,
                proj_span=proj_span,
                is_256=is_256,
                color_reset=color_reset,
            )

        output_content = "\n".join(rendered_lines)
        gradient_resets: tuple[int, ...] = (49 if self._bg else 39,)

        if extra_styles:
            extra_resets: list[int] = []

            for extra_style in extra_styles:
                for reset_code in _style_reset_codes(extra_style):
                    if reset_code not in extra_resets:
                        extra_resets.append(reset_code)

            gradient_resets = gradient_resets + tuple(extra_resets)

        return (
            S(f"{extra_open}{output_content}{extra_close}", _reset_codes=gradient_resets)
            if extra_open or extra_close
            else S(output_content, _reset_codes=gradient_resets)
        )


class _StyleGroup(_SBase):
    """An immutable, ordered group of styles produced by `|`.\n
    ----------------------------------------------------------------------------------------------------
    Supports further `|` chaining and `()` application."""

    __slots__: tuple[str, ...] = ("_codes", "_oc")

    def __init__(self, *codes: BaseStyle) -> None:
        self._codes: tuple[BaseStyle, ...] = codes
        self._oc = _build_open_close(self)
        self.ansi = "".join(self._oc[0])

    def __iter__(self) -> Iterator[BaseStyle]:
        """Iterating a `_StyleGroup` yields its individual styles in order."""

        return iter(self._codes)

    def __call__(self, *text: Renderable) -> S:
        """Applies this style group to the given text, auto-resetting after."""

        for code in self._codes:
            if isinstance(code, _GradientStyle):
                other_codes = tuple([item for item in self._codes if not isinstance(item, _GradientStyle)])
                return code._render_gradient(text, extra_styles=other_codes)

        group_resets: list[int] = []

        for code in self._codes:
            for reset_code in _style_reset_codes(code):
                if reset_code not in group_resets:
                    group_resets.append(reset_code)

        return _render_styled(
            self._oc[0],
            self._oc[1],
            _restore_reset_styles(self._codes, text),
            reset_codes=tuple(group_resets),
        )

    def __repr__(self) -> str:
        """Returns a string representation of this style group, showing its individual codes."""

        return f"_StyleGroup{self._codes!r}"

    def __eq__(self, other: object) -> bool:
        """Returns `True` if `other` is a `_StyleGroup` with identical style codes in identical order."""

        if isinstance(other, _StyleGroup):
            return self._codes == other._codes
        elif isinstance(other, (_SBase, str)):
            return super().__eq__(other)

        return False

    def __hash__(self) -> int:
        return hash(self._codes)

    def as_fg(self) -> _StyleGroup:
        """Convert all background color styles in this group to foreground color styles."""

        return _StyleGroup(*[code.as_fg() for code in self._codes])

    def as_bg(self) -> _StyleGroup:
        """Convert all foreground color styles in this group to background color styles."""

        return _StyleGroup(*[code.as_bg() for code in self._codes])

    def as_text_fg(self) -> _FgColorStyle:
        """Returns black or white foreground color for optimal contrast on the background in this group."""

        for code in reversed(self._codes):
            if isinstance(code, (_BgStyle, _BgColorStyle, _BgColor256Style)):
                return code.as_text_fg()

        return _FgColorStyle(255, 255, 255)

    def as_text_bg(self) -> _BgColorStyle:
        """Returns black or white background color for optimal contrast behind the foreground in this group."""

        for code in reversed(self._codes):
            if isinstance(code, (_FgStyle, _FgColorStyle, _FgColor256Style)):
                return code.as_text_bg()

        return _BgColorStyle(0, 0, 0)

    def with_text_fg(self) -> _StyleGroup:
        """Returns a new style group combining this group with an optimal high-contrast text foreground."""

        return self | self.as_text_fg()

    def with_text_bg(self) -> _StyleGroup:
        """Returns a new style group combining this group with an optimal high-contrast text background."""

        return self | self.as_text_bg()


# ***************************************************** NAMESPACE HELPERS *****************************************************


class _BgBrNS:
    """Namespace for bright background colors, reachable as `S.BG.BR.*`."""

    BLACK: ClassVar[_BgStyle] = _BgStyle(100)
    """Bright black (gray) background."""
    RED: ClassVar[_BgStyle] = _BgStyle(101)
    """Bright red background."""
    GREEN: ClassVar[_BgStyle] = _BgStyle(102)
    """Bright green background."""
    YELLOW: ClassVar[_BgStyle] = _BgStyle(103)
    """Bright yellow background."""
    BLUE: ClassVar[_BgStyle] = _BgStyle(104)
    """Bright blue background."""
    MAGENTA: ClassVar[_BgStyle] = _BgStyle(105)
    """Bright magenta background."""
    CYAN: ClassVar[_BgStyle] = _BgStyle(106)
    """Bright cyan background."""
    WHITE: ClassVar[_BgStyle] = _BgStyle(107)
    """Bright white background."""


class _BgNS:
    """Namespace for background styles and colors, reachable as `S.BG.*`."""

    # ********************* STANDARD BG COLORS **********************

    BLACK: ClassVar[_BgStyle] = _BgStyle(40)
    """Black background."""
    RED: ClassVar[_BgStyle] = _BgStyle(41)
    """Red background."""
    GREEN: ClassVar[_BgStyle] = _BgStyle(42)
    """Green background."""
    YELLOW: ClassVar[_BgStyle] = _BgStyle(43)
    """Yellow background."""
    BLUE: ClassVar[_BgStyle] = _BgStyle(44)
    """Blue background."""
    MAGENTA: ClassVar[_BgStyle] = _BgStyle(45)
    """Magenta background."""
    CYAN: ClassVar[_BgStyle] = _BgStyle(46)
    """Cyan background."""
    WHITE: ClassVar[_BgStyle] = _BgStyle(47)
    """White background."""

    # ***************** BRIGHT BG COLORS NAMESPACE ******************

    BR: ClassVar[type[_BgBrNS]] = _BgBrNS
    """Access bright background colors (e.g., `S.BG.BR.RED`)."""

    # ********************** CUSTOM BG COLORS ***********************

    @overload
    @staticmethod
    def rgb(red: int, green: int, blue: int, /) -> _BgColorStyle: ...
    @overload
    @staticmethod
    def rgb(color: rgba, /) -> _BgColorStyle: ...

    @staticmethod
    def rgb(*args: Any) -> _BgColorStyle:
        """24-bit background color from RGB components or an `rgba` object.\n
        `S.BG.rgb(112, 118, 255)("text")` or `S.BG.rgb(my_rgba)("text")`"""

        if len(args) == 3:
            return _BgColorStyle(args[0], args[1], args[2])

        return _BgColorStyle(args[0][0], args[0][1], args[0][2])

    @staticmethod
    def hex(color: str | int | hexa, /) -> _BgColorStyle:
        """24-bit background color from HEX string, HEX integer, or `hexa` object.\n
        `S.BG.hex("#67F")("text")`, `S.BG.hex(0x7075FF)`, or `S.BG.hex(my_hexa)("text")`"""

        return _BgColorStyle.from_hex(color, bg=True)

    @staticmethod
    def color256(code: int, /) -> _BgColor256Style:
        """256-color palette background color (code in range [0, 255] inclusive).\n
        `S.BG.color256(196)("text")`"""

        return _BgColor256Style(code)

    @staticmethod
    def gradient(
        *colors: GradientStop | Sequence[GradientStop],
        angle: float | int = 0.0,
        space: Literal["rgb", "hsl", "hsl_long", "linear_rgb", "oklab"] = "hsl",
        granularity: Literal["char", "word", "line"] = "char",
        skip_whitespace: bool = False,
        cell_aspect_ratio: float = 2.0,
        color_depth: Literal["truecolor", "256", "auto"] = "auto",
    ) -> _GradientStyle:
        """Create a background gradient style transitioning colors across text or terminal blocks.\n
        ----------------------------------------------------------------------------------------------------
        *   `colors` – Sequence of colors or `(color, position)` tuples defining the gradient stops.
        *   `angle` – Direction angle in degrees (`0.0` = left-to-right, `90.0` = top-to-bottom,
            `180.0` = right-to-left, `270.0` = bottom-to-top, `45.0` = top-left to bottom-right).
        *   `space` – Color space to interpolate in
            (`"rgb"`, `"hsl"`, `"hsl_long"`, `"linear_rgb"`, or `"oklab"`). Default is `"hsl"`.
        *   `granularity` – Coloring granularity (`"char"`, `"word"`, or `"line"`).
        *   `skip_whitespace` – Whether to skip emitting color escape sequences over whitespace.
        *   `cell_aspect_ratio` – Font cell aspect ratio for 2D geometry correction (default `2.0`).
        *   `color_depth` – Color mode (`"truecolor"`, `"256"`, or `"auto"`).\n
        ----------------------------------------------------------------------------------------------------
        Raises `ValueError` if `colors` is empty or any option is invalid."""

        if space not in {"rgb", "hsl", "hsl_long", "linear_rgb", "oklab"}:
            raise ValueError(f"Invalid gradient space {space!r}. Expected 'rgb', 'hsl', 'hsl_long', 'linear_rgb', or 'oklab'")
        if granularity not in {"char", "word", "line"}:
            raise ValueError(f"Invalid granularity {granularity!r}. Expected 'char', 'word', or 'line'")
        if color_depth not in {"truecolor", "256", "auto"}:
            raise ValueError(f"Invalid color_depth {color_depth!r}. Expected 'truecolor', '256', or 'auto'")
        if cell_aspect_ratio <= 0.0:
            raise ValueError(f"The 'cell_aspect_ratio' parameter must be positive, got {cell_aspect_ratio!r}")

        return _GradientStyle(
            _parse_gradient_stops(colors),
            angle=float(angle),
            space=space,
            granularity=granularity,
            skip_whitespace=skip_whitespace,
            cell_aspect_ratio=cell_aspect_ratio,
            color_depth=color_depth,
            bg=True,
        )


class _BrNS:
    """Namespace for bright foreground colors, reachable as `S.BR.*`."""

    BLACK: ClassVar[_FgStyle] = _FgStyle(90)
    """Bright black (gray) foreground."""
    RED: ClassVar[_FgStyle] = _FgStyle(91)
    """Bright red foreground."""
    GREEN: ClassVar[_FgStyle] = _FgStyle(92)
    """Bright green foreground."""
    YELLOW: ClassVar[_FgStyle] = _FgStyle(93)
    """Bright yellow foreground."""
    BLUE: ClassVar[_FgStyle] = _FgStyle(94)
    """Bright blue foreground."""
    MAGENTA: ClassVar[_FgStyle] = _FgStyle(95)
    """Bright magenta foreground."""
    CYAN: ClassVar[_FgStyle] = _FgStyle(96)
    """Bright cyan foreground."""
    WHITE: ClassVar[_FgStyle] = _FgStyle(97)
    """Bright white foreground."""


# ******************************************************* STYLE & TEXT ********************************************************


class S(_SBase):
    """Build a styled string from a sequence of segments
    (strings, `S` objects, bare styles, or raw tuples), joined by `sep`,
    or use class-level style attributes and methods to apply ANSI styling.\n
    ----------------------------------------------------------------------------------------------------
    *   `segments` – Any number of segments to render.
        Each positional argument represents one logical line.
    *   `sep` – The separator inserted between two adjacent positional arguments (default `""`).\n
    ----------------------------------------------------------------------------------------------------
    After construction the instance exposes:
    *   `ansi` – The fully rendered ANSI escape string, ready to be written to a terminal.
    *   `raw` – `ansi` with every ANSI escape sequence stripped (computed on demand).
    *   `code_positions` – A tuple of `(position, sequence)` pairs giving
        the start offset of every ANSI escape sequence inside `ansi` (computed on demand).\n
    ----------------------------------------------------------------------------------------------------
    Every style attribute supports `|` for combining and `()` for applying to text.\n
    ----------------------------------------------------------------------------------------------------
    #### Example Usage

    ```python
    from xulbux import S

    # Combine styles using operator `|`:
    status = (S.BOLD | S.BR.GREEN)("SUCCESS")

    # Nesting and joining styled items:
    header = S(S.BOLD("Options: "), S(", ").join([S.CYAN("fast"), S.CYAN("safe")]))

    # Direct terminal printing:
    status.print()
    ```"""

    __slots__: tuple[str, ...] = ("_reset_codes",)

    _reset_codes: tuple[int, ...]
    """Tuple of ANSI SGR reset codes associated with the style of this instance."""

    # ************************* TOTAL RESET *************************

    RESET: ClassVar[_Style] = _Style(0)
    """Reset all styling to default."""

    # *********************** SPECIFIC RESETS ***********************

    RESET_BOLD: ClassVar[_Style] = _Style(22)
    """Reset bold (also resets dim, as they share the same code)."""
    RESET_DIM: ClassVar[_Style] = _Style(22)
    """Reset dim (also resets bold, as they share the same code)."""
    RESET_ITALIC: ClassVar[_Style] = _Style(23)
    """Reset italic."""
    RESET_UNDERLINE: ClassVar[_Style] = _Style(24)
    """Reset underline and double underline."""
    RESET_INVERSE: ClassVar[_Style] = _Style(27)
    """Reset inverse."""
    RESET_HIDDEN: ClassVar[_Style] = _Style(28)
    """Reset hidden."""
    RESET_STRIKETHROUGH: ClassVar[_Style] = _Style(29)
    """Reset strikethrough."""
    RESET_BLINK: ClassVar[_Style] = _Style(25)
    """Reset blink."""
    RESET_FG: ClassVar[_Style] = _Style(39)
    """Reset foreground color."""
    RESET_BG: ClassVar[_Style] = _Style(49)
    """Reset background color."""

    # ************************* TEXT STYLES *************************

    BOLD: ClassVar[_Style] = _Style(1)
    """Bold text.\n
    Note that this is also reset by `RESET_DIM`."""
    DIM: ClassVar[_Style] = _Style(2)
    """Dim text.\n
    Note that this is also reset by `RESET_BOLD`."""
    ITALIC: ClassVar[_Style] = _Style(3)
    """Italic text."""
    UNDERLINE: ClassVar[_Style] = _Style(4)
    """Underline text."""
    BLINK: ClassVar[_Style] = _Style(5)
    """Blinking text."""
    INVERSE: ClassVar[_Style] = _Style(7)
    """Inverse colors (swap foreground and background colors)."""
    HIDDEN: ClassVar[_Style] = _Style(8)
    """Hidden (invisible) text."""
    STRIKETHROUGH: ClassVar[_Style] = _Style(9)
    """Strikethrough text."""
    DOUBLE_UNDERLINE: ClassVar[_Style] = _Style(21)
    """Double underline text."""

    # ********************* STANDARD FG COLORS **********************

    BLACK: ClassVar[_FgStyle] = _FgStyle(30)
    """Black foreground."""
    RED: ClassVar[_FgStyle] = _FgStyle(31)
    """Red foreground."""
    GREEN: ClassVar[_FgStyle] = _FgStyle(32)
    """Green foreground."""
    YELLOW: ClassVar[_FgStyle] = _FgStyle(33)
    """Yellow foreground."""
    BLUE: ClassVar[_FgStyle] = _FgStyle(34)
    """Blue foreground."""
    MAGENTA: ClassVar[_FgStyle] = _FgStyle(35)
    """Magenta foreground."""
    CYAN: ClassVar[_FgStyle] = _FgStyle(36)
    """Cyan foreground."""
    WHITE: ClassVar[_FgStyle] = _FgStyle(37)
    """Bright white foreground."""

    # ************************* NAMESPACES **************************

    BR: ClassVar[type[_BrNS]] = _BrNS
    BG: ClassVar[type[_BgNS]] = _BgNS

    # ******************** CUSTOM COLORS & LINKS ********************

    @overload
    @staticmethod
    def rgb(red: int, green: int, blue: int, /) -> _FgColorStyle: ...
    @overload
    @staticmethod
    def rgb(color: rgba, /) -> _FgColorStyle: ...

    @staticmethod
    def rgb(*args: Any) -> _FgColorStyle:
        """24-bit foreground color from RGB components or an `rgba` object.\n
        `S.rgb(112, 118, 255)("text")` or `S.rgb(my_rgba)("text")`"""

        if len(args) == 3:
            return _FgColorStyle(args[0], args[1], args[2])

        return _FgColorStyle(args[0][0], args[0][1], args[0][2])

    @staticmethod
    def hex(color: str | int | hexa, /) -> _FgColorStyle:
        """24-bit foreground color from HEX string, HEX integer, or `hexa` object.\n
        `S.hex("#67F")("text")`, `S.hex(0x7075FF)`, or `S.hex(my_hexa)("text")`"""

        return _FgColorStyle.from_hex(color)

    @staticmethod
    def color256(code: int, /) -> _FgColor256Style:
        """256-color palette foreground color (code in range [0, 255] inclusive).\n
        `S.color256(196)("text")`"""

        return _FgColor256Style(code)

    @staticmethod
    def link(url: str | Path, /) -> _Link:
        """Clickable hyperlink. Accepts strings or `pathlib.Path` objects.<br>
        If a `pathlib.Path` is passed, it is automatically resolved and converted to a URI.\n
        ----------------------------------------------------------------------------------------------------
        >>> S.link("https://example.com")("click here")
        >>> S.link(Path("docs/readme.md"))("open file")"""

        return _Link(url)

    @staticmethod
    def gradient(
        *colors: GradientStop | Sequence[GradientStop],
        angle: float | int = 0.0,
        space: Literal["rgb", "hsl", "hsl_long", "linear_rgb", "oklab"] = "hsl",
        granularity: Literal["char", "word", "line"] = "char",
        skip_whitespace: bool = True,
        cell_aspect_ratio: float = 2.0,
        color_depth: Literal["truecolor", "256", "auto"] = "auto",
    ) -> _GradientStyle:
        """Create a gradient style that smoothly transitions colors across text or terminal blocks.\n
        ----------------------------------------------------------------------------------------------------
        *   `colors` – Sequence of colors or `(color, position)` tuples defining the gradient stops.
        *   `angle` – Direction angle in degrees (`0.0` = left-to-right, `90.0` = top-to-bottom,
            `180.0` = right-to-left, `270.0` = bottom-to-top, `45.0` = top-left to bottom-right).
        *   `space` – Color space to interpolate in
            (`"rgb"`, `"hsl"`, `"hsl_long"`, `"linear_rgb"`, or `"oklab"`). Default is `"hsl"`.
        *   `granularity` – Coloring granularity (`"char"`, `"word"`, or `"line"`).
        *   `skip_whitespace` – Whether to skip emitting color escape sequences over whitespace.
        *   `cell_aspect_ratio` – Font cell aspect ratio for 2D geometry correction (default `2.0`).
        *   `color_depth` – Color mode (`"truecolor"`, `"256"`, or `"auto"`).\n
        ----------------------------------------------------------------------------------------------------
        Raises `ValueError` if `colors` is empty or any option is invalid."""

        if space not in {"rgb", "hsl", "hsl_long", "linear_rgb", "oklab"}:
            raise ValueError(f"Invalid gradient space {space!r}. Expected 'rgb', 'hsl', 'hsl_long', 'linear_rgb', or 'oklab'")
        if granularity not in {"char", "word", "line"}:
            raise ValueError(f"Invalid granularity {granularity!r}. Expected 'char', 'word', or 'line'")
        if color_depth not in {"truecolor", "256", "auto"}:
            raise ValueError(f"Invalid color_depth {color_depth!r}. Expected 'truecolor', '256', or 'auto'")
        if cell_aspect_ratio <= 0.0:
            raise ValueError(f"The 'cell_aspect_ratio' parameter must be positive, got {cell_aspect_ratio!r}")

        return _GradientStyle(
            _parse_gradient_stops(colors),
            angle=float(angle),
            space=space,
            granularity=granularity,
            skip_whitespace=skip_whitespace,
            cell_aspect_ratio=cell_aspect_ratio,
            color_depth=color_depth,
            bg=False,
        )

    # *********************** INITIALIZATION ************************

    def __init__(self, /, *segments: Renderable, sep: str = "", _reset_codes: tuple[int, ...] = ()) -> None:
        ansi_parts: list[str] = []

        for i, segment in enumerate(segments):
            if i > 0 and sep:
                ansi_parts.append(sep)

            _render_segment(segment, ansi_parts)

        self.ansi = "".join(ansi_parts)
        self._reset_codes = _reset_codes


# **************************************************** PUBLIC TYPE HELPERS ****************************************************


type FgColorStyle = _FgStyle | _FgColorStyle | _FgColor256Style
"""A single foreground color style code (e.g., `S.RED`, `S.BR.BLUE`, `S.hex("#67F")`, `S.color256(196)`).<br>
Excludes background colors and non-color styles like `S.BOLD`."""


def is_fg_color_style(obj: object, /) -> TypeIs[FgColorStyle]:
    """Returns true if `obj` is an instance that matches the `FgColorStyle` type."""

    if isinstance(obj, (_FgColorStyle, _FgColor256Style, _FgStyle)):
        return True
    elif isinstance(obj, _Style):
        return (30 <= (val := obj._value) <= 37) or (90 <= val <= 97)
    elif isinstance(obj, (_ColorStyle, _Color256Style)):
        return not obj._bg

    return False


type BgColorStyle = _BgStyle | _BgColorStyle | _BgColor256Style
"""A single background color style code (e.g., `S.BG.RED`, `S.BG.hex("#67F")`, `S.BG.color256(196)`).<br>
Excludes foreground colors and non-color styles like `S.BOLD`."""


def is_bg_color_style(obj: object, /) -> TypeIs[BgColorStyle]:
    """Returns true if `obj` is an instance that matches the `BgColorStyle` type."""

    if isinstance(obj, (_BgColorStyle, _BgColor256Style, _BgStyle)):
        return True
    elif isinstance(obj, _Style):
        return (40 <= (val := obj._value) <= 47) or (100 <= val <= 107)
    elif isinstance(obj, (_ColorStyle, _Color256Style)):
        return obj._bg

    return False


type ColorStyle = FgColorStyle | BgColorStyle
"""Any single foreground or background color style code (e.g., `S.RED`, `S.BG.BLUE`, `S.hex("#67F")`).<br>
Excludes non-color styles like `S.BOLD`."""


def is_color_style(obj: object, /) -> TypeIs[ColorStyle]:
    """Returns true if `obj` is an instance that matches the `ColorStyle` type."""

    return is_fg_color_style(obj) or is_bg_color_style(obj)


type BaseStyle = _Style | _ColorStyle | _Color256Style | _GradientStyle | _Link
"""Any single style code, color style, link, or gradient style that can be combined via `|` and applied to text."""


def is_base_style(obj: object, /) -> TypeIs[BaseStyle]:
    """Returns true if `obj` is an instance that matches the `BaseStyle` type."""

    return isinstance(obj, (_Style, _ColorStyle, _Color256Style, _GradientStyle, _Link))


type AnyStyle = BaseStyle | _StyleGroup
"""Any single style or group of styles that can be combined via `|` and applied to text."""


def is_any_style(obj: object, /) -> TypeIs[AnyStyle]:
    """Returns true if `obj` is an instance that matches the `AnyStyle` type."""

    return isinstance(obj, (_Style, _ColorStyle, _Color256Style, _Link, _GradientStyle, _StyleGroup))


type TextSegment = str | S
"""A single segment that contains actual text: a plain string or a styled `S` object.<br>
Strictly excludes bare style objects (e.g., `S.RED`, `S.BOLD | S.BLUE`) that do not contain text."""


def is_text_segment(obj: object, /) -> TypeIs[TextSegment]:
    """Returns true if `obj` is an instance that matches the `TextSegment` type (has actual text)."""

    return isinstance(obj, (str, S))


type RenderSegment = str | _SBase
"""A single segment: a plain string, a bare style object (open-only), or a styled `S` object."""


def is_render_segment(obj: object, /) -> TypeIs[RenderSegment]:
    """Returns true if `obj` is an instance that matches the `RenderSegment` type."""

    return isinstance(obj, (str, _SBase))


type TextRenderable = TextSegment | tuple[TextRenderable, ...]
"""Anything that contains actual textual content to be rendered, strictly excluding bare styles.<br>
Can be passed to a `_Style` call, or as a positional argument to `S(…)`. Can be arbitrarily nested in tuples."""


def is_text_renderable(obj: object, /) -> TypeIs[TextRenderable]:
    """Returns true if `obj` is an instance that matches the `TextRenderable` type."""

    if isinstance(obj, (str, S)):
        return True

    elif isinstance(obj, tuple):
        # Don't use `all()` as for-loop is more performant:
        for item in cast("tuple[Any, ...]", obj):  # ruff:ignore[reimplemented-builtin]
            if not is_text_renderable(item):
                return False
        return True

    return False


type Renderable = RenderSegment | tuple[Renderable, ...]
"""Anything that can be styled or rendered.<br>
Can be passed to a `_Style` call, or as a positional argument to `S(…)`. Can be arbitrarily nested in tuples."""


def is_renderable(obj: object, /) -> TypeIs[Renderable]:
    """Returns true if `obj` is an instance that matches the `Renderable` type."""

    if isinstance(obj, (str, _SBase)):
        return True

    elif isinstance(obj, tuple):
        # Don't use `all()` as for-loop is more performant:
        for item in cast("tuple[Any, ...]", obj):  # ruff:ignore[reimplemented-builtin]
            if not is_renderable(item):
                return False
        return True

    return False


# ***************************************************** TERMINAL CONTROL ******************************************************


class Term:
    """Common ANSI terminal control sequences (cursor, screen, title, clipboard, modes)
    as plain strings or string-returning static methods.\n
    ----------------------------------------------------------------------------------------------------
    Values can be passed straight into an `S(…)` call or written to `sys.stdout`.\n
    ----------------------------------------------------------------------------------------------------
    #### Example Usage

    ```python
    import sys
    from xulbux import Term

    # Switch to alternate screen and hide cursor:
    sys.stdout.write(Term.ALT_SCREEN + Term.CUR_HIDE)
    sys.stdout.flush()

    # Move cursor up 2 rows and clear line:
    sys.stdout.write(Term.up(2) + Term.CLEAR_LINE)
    sys.stdout.flush()

    # Restore main screen and cursor:
    sys.stdout.write(Term.CUR_SHOW + Term.MAIN_SCREEN)
    sys.stdout.flush()
    ```"""

    BELL: ClassVar[str] = "\x07"
    """Terminal bell character to trigger an audio or visual alert."""
    CLEAR_LINE: ClassVar[str] = "\x1b[2K"
    """Erase the entire current line."""
    CLEAR_LINE_TO_END: ClassVar[str] = "\x1b[0K"
    """Erase from the cursor to the end of the current line."""
    CLEAR_LINE_TO_START: ClassVar[str] = "\x1b[1K"
    """Erase from the beginning of the line up to the cursor."""
    CLEAR_SCREEN: ClassVar[str] = "\x1b[2J"
    """Erase the whole screen."""
    CLEAR_SCREEN_TO_END: ClassVar[str] = "\x1b[0J"
    """Erase from the cursor to the end of the screen."""
    CLEAR_SCREEN_TO_START: ClassVar[str] = "\x1b[1J"
    """Erase from the beginning of the screen up to the cursor."""
    CLEAR_SCROLLBACK: ClassVar[str] = "\x1b[3J"
    """Erase the terminal scrollback history buffer."""
    CUR_HIDE: ClassVar[str] = "\x1b[?25l"
    """Hide the cursor."""
    CUR_SHOW: ClassVar[str] = "\x1b[?25h"
    """Show the cursor."""
    CUR_HOME: ClassVar[str] = "\x1b[H"
    """Move the cursor to the home position (0,0) (CUP/HVP)."""
    CUR_SAVE: ClassVar[str] = "\x1b[s"
    """Save the current cursor position (ANSI.SYS / SCO)."""
    CUR_RESTORE: ClassVar[str] = "\x1b[u"
    """Restore the previously saved cursor position (ANSI.SYS / SCO)."""
    CUR_SAVE_DEC: ClassVar[str] = "\x1b7"
    """Save cursor position and attributes (DEC private sequence ESC 7)."""
    CUR_RESTORE_DEC: ClassVar[str] = "\x1b8"
    """Restore cursor position and attributes (DEC private sequence ESC 8)."""
    ALT_SCREEN: ClassVar[str] = "\x1b[?1049h"
    """Enter the alternate screen buffer."""
    MAIN_SCREEN: ClassVar[str] = "\x1b[?1049l"
    """Leave the alternate screen buffer."""
    BRACKETED_PASTE_ENABLE: ClassVar[str] = "\x1b[?2004h"
    """Enable bracketed paste mode (wraps pasted text in paste brackets)."""
    BRACKETED_PASTE_DISABLE: ClassVar[str] = "\x1b[?2004l"
    """Disable bracketed paste mode."""
    LINE_WRAP_ENABLE: ClassVar[str] = "\x1b[?7h"
    """Enable line wrapping (DECAWM)."""
    LINE_WRAP_DISABLE: ClassVar[str] = "\x1b[?7l"
    """Disable line wrapping (DECAWM)."""
    RESET: ClassVar[str] = "\x1bc"
    """Hard reset to initial state (RIS)."""
    SOFT_RESET: ClassVar[str] = "\x1b[!p"
    """Soft terminal reset to sensible defaults (DECSTR)."""

    @staticmethod
    def up(n: int = 1, /) -> str:
        """Move the cursor up by `n` rows."""

        return f"\x1b[{n}A"

    @staticmethod
    def down(n: int = 1, /) -> str:
        """Move the cursor down by `n` rows."""

        return f"\x1b[{n}B"

    @staticmethod
    def left(n: int = 1, /) -> str:
        """Move the cursor left by `n` columns."""

        return f"\x1b[{n}D"

    @staticmethod
    def right(n: int = 1, /) -> str:
        """Move the cursor right by `n` columns."""

        return f"\x1b[{n}C"

    @staticmethod
    def prev_line(n: int = 1, /) -> str:
        """Move the cursor to the beginning of the previous line, `n` lines up."""

        return f"\x1b[{n}F"

    @staticmethod
    def next_line(n: int = 1, /) -> str:
        """Move the cursor to the beginning of the next line, `n` lines down."""

        return f"\x1b[{n}E"

    @staticmethod
    def row(row: int = 1, /) -> str:
        """Move the cursor to absolute row `row` in the current column (1-based, VPA)."""

        return f"\x1b[{row}d"

    @staticmethod
    def col(col: int = 1, /) -> str:
        """Move the cursor to absolute column `col` in the current row (1-based, CHA)."""

        return f"\x1b[{col}G"

    @staticmethod
    def move(row: int, col: int, /) -> str:
        """Move the cursor to absolute position `(row, col)` (1-based, CUP)."""

        return f"\x1b[{row};{col}H"

    @staticmethod
    def insert_lines(n: int = 1, /) -> str:
        """Insert `n` blank lines at the current row (IL)."""

        return f"\x1b[{n}L"

    @staticmethod
    def delete_lines(n: int = 1, /) -> str:
        """Delete `n` lines starting from the current row (DL)."""

        return f"\x1b[{n}M"

    @staticmethod
    def insert_chars(n: int = 1, /) -> str:
        """Insert `n` blank characters at the current cursor position (ICH)."""

        return f"\x1b[{n}@"

    @staticmethod
    def delete_chars(n: int = 1, /) -> str:
        """Delete `n` characters at the current cursor position (DCH)."""

        return f"\x1b[{n}P"

    @staticmethod
    def scroll_up(n: int = 1, /) -> str:
        """Scroll page up by `n` lines."""

        return f"\x1b[{n}S"

    @staticmethod
    def scroll_down(n: int = 1, /) -> str:
        """Scroll page down by `n` lines."""

        return f"\x1b[{n}T"

    @staticmethod
    def title(text: str, /) -> str:
        """Set the terminal window / tab title (OSC 2)."""

        return f"\x1b]2;{text}\x07"

    @staticmethod
    def cursor_shape(
        shape: Literal[
            1,
            2,
            3,
            4,
            5,
            6,
            "blinking_block",
            "steady_block",
            "blinking_underline",
            "steady_underline",
            "blinking_bar",
            "steady_bar",
        ],
        /,
    ) -> str:
        """Set the terminal cursor shape (DECSCUSR).\n
        ----------------------------------------------------------------------------------------------------
        *   `shape` – An integer in range [1, 6] inclusive, or a string name of the shape:
            - `1` `"blinking_block"`
            - `2` `"steady_block"`
            - `3` `"blinking_underline"`
            - `4` `"steady_underline"`
            - `5` `"blinking_bar"`
            - `6` `"steady_bar"`"""

        if (shape_num := _CURSOR_SHAPES.get(shape) if isinstance(shape, str) else shape) not in {1, 2, 3, 4, 5, 6}:
            raise ValueError(
                f"Expected cursor shape in [1, 6] inclusive, or one of {list(_CURSOR_SHAPES.keys())!r}, got {shape!r}"
            )

        return f"\x1b[{shape_num} q"

    @staticmethod
    def clipboard_copy(text: str, /) -> str:
        """Copy `text` to the system clipboard (OSC 52)."""

        encoded = _base64.b64encode(text.encode("utf-8")).decode("ascii")
        return f"\x1b]52;c;{encoded}\x1b\\"

    @staticmethod
    def cwd(path: str | Path, /) -> str:
        """Notify the terminal of the current working directory (OSC 7)."""

        uri = path.resolve().as_uri() if isinstance(path, Path) else path
        return f"\x1b]7;{uri}\x1b\\"
