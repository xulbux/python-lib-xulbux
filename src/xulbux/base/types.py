"""
This module contains all custom type definitions used throughout the library.
"""

from typing import TYPE_CHECKING, Annotated, TypeAlias, TypedDict, Optional, Protocol, Literal, Union, Any
from pathlib import Path

# PREVENT CIRCULAR IMPORTS
if TYPE_CHECKING:
    from ..color import rgba, hsla, hexa

#
################################################## Annotated ##################################################

Int_0_100 = Annotated[int, "Integer constrained to the range [0, 100] inclusive."]
"""Integer constrained to the range [0, 100] inclusive."""
Int_0_255 = Annotated[int, "Integer constrained to the range [0, 255] inclusive."]
"""Integer constrained to the range [0, 255] inclusive."""
Int_0_360 = Annotated[int, "Integer constrained to the range [0, 360] inclusive."]
"""Integer constrained to the range [0, 360] inclusive."""
Float_0_1 = Annotated[float, "Float constrained to the range [0.0, 1.0] inclusive."]
"""Float constrained to the range [0.0, 1.0] inclusive."""

FormattableString = Annotated[str, "String made to be formatted with the `.format()` method."]
"""String made to be formatted with the `.format()` method."""

#
################################################## TypeAlias ##################################################

PathsList: TypeAlias = Union[list[Path], list[str], list[Union[Path, str]]]
"""Union of all supported list types for a list of paths."""

DataObj: TypeAlias = Union[list[Any], tuple[Any, ...], set[Any], frozenset[Any], dict[Any, Any]]
"""Union of supported data structures used in the `data` module."""
DataObjTT = (list, tuple, set, frozenset, dict)
"""Tuple of supported data structures used in the `data` module."""

IndexIterable: TypeAlias = Union[list[Any], tuple[Any, ...], set[Any], frozenset[Any]]
"""Union of all iterable types that support indexing operations."""
IndexIterableTT = (list, tuple, set, frozenset)
"""Tuple of all iterable types that support indexing operations."""

Rgba: TypeAlias = Union[
    tuple[Int_0_255, Int_0_255, Int_0_255],
    tuple[Int_0_255, Int_0_255, Int_0_255, Optional[Float_0_1]],
    list[Int_0_255],
    list[Union[Int_0_255, Optional[Float_0_1]]],
    "RgbaDict",
    "rgba",
    str,
]
"""Matches all supported RGBA color value formats."""
Hsla: TypeAlias = Union[
    tuple[Int_0_360, Int_0_100, Int_0_100],
    tuple[Int_0_360, Int_0_100, Int_0_100, Optional[Float_0_1]],
    list[Union[Int_0_360, Int_0_100]],
    list[Union[Int_0_360, Int_0_100, Optional[Float_0_1]]],
    "HslaDict",
    "hsla",
    str,
]
"""Matches all supported HSLA color value formats."""
Hexa: TypeAlias = Union[str, int, "hexa"]
"""Matches all supported HEXA color value formats."""

AnyRgba: TypeAlias = Any
"""Generic type alias for RGBA color values in any format (type checking disabled)."""
AnyHsla: TypeAlias = Any
"""Generic type alias for HSLA color values in any format (type checking disabled)."""
AnyHexa: TypeAlias = Any
"""Generic type alias for HEXA color values in any format (type checking disabled)."""

ArgParseConfig: TypeAlias = Union[set[str], "ArgConfigWithDefault", Literal["before", "after"]]
"""Matches the command-line-parsing configuration of a single argument."""
ArgParseConfigs: TypeAlias = dict[str, ArgParseConfig]
"""Matches the command-line-parsing configurations of multiple arguments, packed in a dictionary."""

#
################################################## Sentinel ##################################################


class AllTextChars:
    """Sentinel class indicating all characters are allowed."""
    ...


################################################## TypedDict ##################################################


class ArgConfigWithDefault(TypedDict):
    """Configuration schema for a flagged command-line argument that has a specified default value."""
    flags: set[str]
    default: str


class ArgData(TypedDict):
    """Schema for the resulting data of parsing a single command-line argument."""
    exists: bool
    is_pos: bool
    values: list[str]
    flag: Optional[str]


class RgbaDict(TypedDict):
    """Dictionary schema for RGBA color components."""
    r: Int_0_255
    g: Int_0_255
    b: Int_0_255
    a: Optional[Float_0_1]


class HslaDict(TypedDict):
    """Dictionary schema for HSLA color components."""
    h: Int_0_360
    s: Int_0_100
    l: Int_0_100
    a: Optional[Float_0_1]


class HexaDict(TypedDict):
    """Dictionary schema for HEXA color components."""
    r: str
    g: str
    b: str
    a: Optional[str]


class MissingLibsMsgs(TypedDict):
    """Configuration schema for custom messages in `System.check_libs()` when checking library dependencies."""
    found_missing: str
    should_install: str


################################################## Protocol ##################################################


class ProgressUpdater(Protocol):
    """Protocol for a progress updater function used in console progress bars."""

    def __call__(self, current: Optional[int] = None, label: Optional[str] = None) -> None:
        """Update the current progress value and/or label."""
        ...
