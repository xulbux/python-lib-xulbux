"""
Provides custom type definitions and TypeVars used throughout the library.
<br>
Includes type aliases for structured color formats, path representations,
and generic nested data structures.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, NotRequired, Protocol, TypedDict, cast, overload

if TYPE_CHECKING:
    import sys
    from collections.abc import Iterable
    from xulbux.ansi import Renderable

    if sys.version_info >= (3, 13):
        from typing import TypeIs
    else:
        from typing_extensions import TypeIs


# ************************************************** COLLECTIONS & ITERABLES **************************************************


type Seq[T] = list[T] | tuple[T, ...]
"""Union of all built-in sequence types (`list`, `tuple`)."""


@overload
def is_seq(obj: object, /) -> TypeIs[Seq[Any]]: ...
@overload
def is_seq[T](obj: object, item_type: type[T] | tuple[type[T], ...], /) -> TypeIs[Seq[T]]: ...
@overload
def is_seq(obj: object, item_type: None, /) -> TypeIs[Seq[Any]]: ...


def is_seq(obj: object, item_type: type[Any] | tuple[type[Any], ...] | None = None, /) -> bool:
    """Returns true if `obj` is an instance that matches the `Seq` type,
    optionally checking if all contained elements are instances of `item_type`.\n
    ----------------------------------------------------------------------------------------------------
    *   `obj` – The object to check.
    *   `item_type` – An optional type or tuple of types to check each contained element against."""

    if not isinstance(obj, (list, tuple)):
        return False
    elif item_type is None:
        return True

    # Don't use `all()` as for-loop is more performant:
    for item in cast("Iterable[Any]", obj):  # ruff:ignore[reimplemented-builtin]
        if not isinstance(item, item_type):
            return False

    return True


type SeqOrSet[T] = list[T] | tuple[T, ...] | set[T] | frozenset[T]
"""Union of all built-in sequence and set types (`list`, `tuple`, `set`, `frozenset`)."""


@overload
def is_seq_or_set(obj: object, /) -> TypeIs[SeqOrSet[Any]]: ...
@overload
def is_seq_or_set[T](obj: object, item_type: type[T] | tuple[type[T], ...], /) -> TypeIs[SeqOrSet[T]]: ...
@overload
def is_seq_or_set(obj: object, item_type: None, /) -> TypeIs[SeqOrSet[Any]]: ...


def is_seq_or_set(obj: object, item_type: type[Any] | tuple[type[Any], ...] | None = None, /) -> bool:
    """Returns true if `obj` is an instance that matches the `SeqOrSet` type,
    optionally checking if all contained elements are instances of `item_type`.\n
    ----------------------------------------------------------------------------------------------------
    *   `obj` – The object to check.
    *   `item_type` – An optional type or tuple of types to check each contained element against."""

    if not isinstance(obj, (list, tuple, set, frozenset)):
        return False
    elif item_type is None:
        return True

    # Don't use `all()` as for-loop is more performant:
    for item in cast("Iterable[Any]", obj):  # ruff:ignore[reimplemented-builtin]
        if not isinstance(item, item_type):
            return False

    return True


type DataObj = list[Any] | tuple[Any, ...] | set[Any] | frozenset[Any] | dict[Any, Any]
"""Union of supported data structures used in the `data` module."""


def is_data_obj(obj: object, /) -> TypeIs[DataObj]:
    """Returns true if `obj` is an instance that matches the `DataObj` type."""

    return isinstance(obj, (list, tuple, set, frozenset, dict))


def is_dict(obj: object, /) -> TypeIs[dict[Any, Any]]:
    """Returns true if `obj` is an instance that matches the `dict` type."""

    return isinstance(obj, dict)


type PathsList = list[Path] | list[str] | list[Path | str] | tuple[Path, ...] | tuple[str, ...] | tuple[Path | str, ...]
"""Union of all supported collection types for paths."""


def is_paths_list(obj: object, /) -> TypeIs[PathsList]:
    """Returns true if `obj` is an instance that matches the `PathsList` type."""

    if isinstance(obj, (list, tuple)):
        # Don't use `all()` as for-loop is more performant:
        for item in cast("list[Any] | tuple[Any, ...]", obj):  # ruff:ignore[reimplemented-builtin]
            if not isinstance(item, (Path, str)):
                return False
        return True

    return False


# ********************************************************** COLORS ***********************************************************


class _RgbaObj(Protocol):
    """Protocol for rgba-like color objects (structurally matches `rgba`)."""

    red: int
    green: int
    blue: int
    alpha: float | None


class _HslaObj(Protocol):
    """Protocol for hsla-like color objects (structurally matches `hsla`)."""

    hue: int
    sat: int
    light: int
    alpha: float | None


class _HexaObj(Protocol):
    """Protocol for hex-like color objects (structurally matches `hexa`)."""

    red: int
    green: int
    blue: int
    alpha: float | None


class RgbaDict(TypedDict):
    """Dictionary schema for RGBA color components."""

    red: int
    """The red channel in range [0, 255] inclusive."""
    green: int
    """The green channel in range [0, 255] inclusive."""
    blue: int
    """The blue channel in range [0, 255] inclusive."""
    alpha: NotRequired[float]
    """The alpha channel in range [0.0, 1.0] inclusive."""


class HslaDict(TypedDict):
    """Dictionary schema for HSLA color components."""

    hue: int
    """The hue channel in range [0, 360] inclusive."""
    sat: int
    """The saturation channel in range [0, 100] inclusive."""
    light: int
    """The lightness channel in range [0, 100] inclusive."""
    alpha: NotRequired[float]
    """The alpha channel in range [0.0, 1.0] inclusive."""


class HexaDict(TypedDict):
    """Dictionary schema for hex color components."""

    red: str
    """The red channel in range [0, 255] inclusive."""
    green: str
    """The green channel in range [0, 255] inclusive."""
    blue: str
    """The blue channel in range [0, 255] inclusive."""
    alpha: NotRequired[str]
    """The alpha channel in range [0.0, 1.0] inclusive."""


type Rgba = tuple[int, int, int] | tuple[int, int, int, float] | list[int] | list[int | float] | RgbaDict | _RgbaObj
"""Structured RGBA color representations:<br>
3- or 4-item `tuple` or `list` (RGB[A]), `RgbaDict`, or an RGBA protocol-compatible object."""

type Hsla = tuple[int, int, int] | tuple[int, int, int, float] | list[int] | list[int | float] | HslaDict | _HslaObj
"""Structured HSLA color representations:<br>
3- or 4-item `tuple` or `list` (HSL[A]), `HslaDict`, or an HSLA protocol-compatible object."""

type Hexa = str | int | _HexaObj
"""Hexadecimal color representations:<br>
Hex `str` (with or without prefix), 24-bit hex `int`, or a hex protocol-compatible object."""


# **************************************************** SYSTEM & UTILITIES *****************************************************


class AllTextChars:
    """Sentinel class indicating all characters are allowed."""

    __slots__: tuple[str, ...] = ()


class MissingLibsMsgs(TypedDict):
    """Configuration schema for custom messages in `system.check_libs()` when checking library dependencies."""

    found_missing: str
    """Message to display when one or more libraries are missing."""
    should_install: str
    """Confirmation message to ask the user if they want to install the missing libraries."""


class ProgressUpdater(Protocol):
    """Protocol for a progress updater function used in terminal progress bars."""

    @overload
    def __call__(self, current: int) -> None:
        """Update the current progress value."""
        ...

    @overload
    def __call__(self, current: int, label: Renderable) -> None:
        """Update the current progress value and label."""
        ...

    @overload
    def __call__(self, *, label: Renderable) -> None:
        """Update the progress label only (keyword-only)."""

    def __call__(self, current: int | None = None, label: Renderable | None = None) -> None:
        """Update the current progress value and/or label."""
        ...  # coverage:ignore[protocol]
