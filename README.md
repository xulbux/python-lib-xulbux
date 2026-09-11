<div align="center">
<br><br>
<h1>
<a href="https://xulbux.github.io/python-lib-xulbux"><img height="64" src="https://github.com/xulbux/python-lib-xulbux/blob/main/assets/icon.svg?raw=true"></a>
<br>
Python library <code>xulbux</code>
<br><br>
<a href="https://pypi.org/project/xulbux"><img src="https://img.shields.io/pypi/v/xulbux?style=flat&labelColor=404560&color=7075FF"/></a> <a href="https://clickpy.clickhouse.com/dashboard/xulbux"><img src="https://img.shields.io/pepy/dt/xulbux?style=flat&labelColor=404560&color=7075FF"/></a> <a href="https://github.com/xulbux/python-lib-xulbux/blob/main/LICENSE"><img src="https://img.shields.io/github/license/xulbux/python-lib-xulbux?style=flat&labelColor=404560&color=A6A8FF"/></a> <a href="https://github.com/xulbux/python-lib-xulbux/commits"><img src="https://img.shields.io/github/last-commit/xulbux/python-lib-xulbux?style=flat&labelColor=55404A&color=FF608A"/></a> <a href="https://github.com/xulbux/python-lib-xulbux/issues"><img src="https://img.shields.io/github/issues/xulbux/python-lib-xulbux?style=flat&labelColor=55404A&color=FF608A"/></a> <a href="https://github.com/xulbux/python-lib-xulbux/stargazers"><img src="https://img.shields.io/github/stars/xulbux/python-lib-xulbux?label=★&style=flat&labelColor=55404A&color=FF8FB4"/></a>
</h1>
<h3>A Python library to simplify common programming tasks.</h3>
<br><br>
</div>

**`xulbux`** is a library that contains many useful classes, types, and functions,
ranging from terminal logging and working with colors to file management and system operations.
The library is designed to simplify common programming tasks and improve code readability through its collection of tools.

For precise information about the library, see the library's [**documentation**](https://xulbux.github.io/python-lib-xulbux/docs).<br>
For the library's latest changes and updates, see the [**change log**](https://github.com/xulbux/python-lib-xulbux/blob/main/CHANGELOG.md).

### The best modules, you have to check out:

<a href="https://xulbux.github.io/python-lib-xulbux/docs/ansi"><img src="https://img.shields.io/badge/ansi-BAA1FF?style=for-the-badge" alt="ansi"></a> <a href="https://xulbux.github.io/python-lib-xulbux/docs/console"><img src="https://img.shields.io/badge/console-BAA1FF?style=for-the-badge" alt="console"></a> <a href="https://xulbux.github.io/python-lib-xulbux/docs/color"><img src="https://img.shields.io/badge/color-BAA1FF?style=for-the-badge" alt="color"></a>

<br>

## Installation

It is recommended to install the library within a [virtual environment](https://docs.python.org/3/tutorial/venv.html) to align with modern Python standards and prevent `externally-managed-environment` errors on newer operating systems.

To install the library, run:

```bash
pip install xulbux
```

To upgrade to the latest available version:

```bash
pip install --upgrade xulbux
```

<br>

## CLI Commands

When the library is installed, the following commands are available in the terminal:

| Command           | Description                                       |
| :---------------- | :------------------------------------------------ |
| `xulbux-lib`      | Show some information about the library.          |
| `xulbux-lib ansi` | Preview all possible ANSI styles in the terminal. |
| `xulbux-lib c256` | Show a map of all 256 colors in the terminal.     |
| `xulbux-lib tc`   | Show a true-color gradient map in the terminal.   |

<br>

## Usage

The library's modules can be accessed by importing the `xulbux` package. It is highly recommended to alias the package (e.g., as `xx`) to prevent naming conflicts with common variable names like `data` or `file`:

```python
import xulbux as xx

xx.console.log("Hello, World!")
xx.data.render({"key": "value"})
```

The library's classes can be imported directly from the `xulbux` package:

```python
from xulbux import ArgumentParser, S
```

Certain things aren't exposed under the `xulbux` package directly.<br>
They can be imported from their respective submodules, for example:

```python
from xulbux.base.consts import CHARS
from xulbux.base.types import PathsList
```

<br>

## Modules

<table>
  <thead>
    <tr>
      <th align="left">Main Module</th>
      <th align="left">Contents</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td align="center"><b><code>base</code></b></td>
      <td>
        <table>
          <thead>
            <tr>
              <th align="left">Sub Module</th>
              <th align="left">Contents</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td align="center"><b><code><a href="https://xulbux.github.io/python-lib-xulbux/docs/api/base.consts">consts</a></code></b></td>
              <td>Character set constants and terminal key sequences used throughout the library.</td>
            </tr>
            <tr>
              <td align="center"><b><code><a href="https://xulbux.github.io/python-lib-xulbux/docs/api/base.decorators">decorators</a></code></b></td>
              <td>Utility decorators used throughout the library.</td>
            </tr>
            <tr>
              <td align="center"><b><code><a href="https://xulbux.github.io/python-lib-xulbux/docs/api/base.exceptions">exceptions</a></code></b></td>
              <td>Custom exception classes used throughout the library.</td>
            </tr>
            <tr>
              <td align="center"><b><code><a href="https://xulbux.github.io/python-lib-xulbux/docs/api/base.types">types</a></code></b></td>
              <td>Custom type definitions used throughout the library.</td>
            </tr>
          </tbody>
        </table>
      </td>
    </tr>
    <tr>
      <td align="center"><b><code><a href="https://xulbux.github.io/python-lib-xulbux/docs/api/ansi">ansi</a></code></b></td>
      <td><code>S</code> and <code>Term</code> classes for building richly formatted terminal output via a typed, operator-based syntax and emitting cursor- and screen-control sequences.</td>
    </tr>
    <tr>
      <td align="center"><b><code><a href="https://xulbux.github.io/python-lib-xulbux/docs/api/color">color</a></code></b></td>
      <td><code>rgba</code>, <code>hsla</code>, and <code>hexa</code> classes for manipulating, converting, blending, and interpolating colors across different color spaces.</td>
    </tr>
    <tr>
      <td align="center"><b><code><a href="https://xulbux.github.io/python-lib-xulbux/docs/api/console">console</a></code></b></td>
      <td><code>ArgumentParser</code>, <code>ProgressBar</code>, and <code>Throbber</code> classes, along with utilities for styled logging, interactive prompts, and terminal control.</td>
    </tr>
    <tr>
      <td align="center"><b><code><a href="https://xulbux.github.io/python-lib-xulbux/docs/api/data">data</a></code></b></td>
      <td>Utilities for processing and managing complex data structures, including deep merging, nested key access, recursive sorting, and syntax-highlighted rendering.</td>
    </tr>
    <tr>
      <td align="center"><b><code><a href="https://xulbux.github.io/python-lib-xulbux/docs/api/fs">fs</a></code></b></td>
      <td>File system utilities including fuzzy path resolution, recursive searching, safe directory creation, and common system path lookups.</td>
    </tr>
    <tr>
      <td align="center"><b><code><a href="https://xulbux.github.io/python-lib-xulbux/docs/api/json">json</a></code></b></td>
      <td>Enhanced JSON file handling and serialization with non-destructive updates, automatic directory creation, and support for comments.</td>
    </tr>
    <tr>
      <td align="center"><b><code><a href="https://xulbux.github.io/python-lib-xulbux/docs/api/regex">regex</a></code></b></td>
      <td><code>LazyRegex</code> pattern container and builders to dynamically generate regular expression patterns for common use cases.</td>
    </tr>
    <tr>
      <td align="center"><b><code><a href="https://xulbux.github.io/python-lib-xulbux/docs/api/string">string</a></code></b></td>
      <td>Utility functions for advanced string manipulation, casing conversion, whitespace stripping, diffing, and safe type casting.</td>
    </tr>
    <tr>
      <td align="center"><b><code><a href="https://xulbux.github.io/python-lib-xulbux/docs/api/system">system</a></code></b></td>
      <td>OS-level automation helpers including clipboard access, file launching, command execution, privilege checks, and dependency installation.</td>
    </tr>
  </tbody>
</table>

<br>

## Example Usage

This is what it could look like using this library for a simple but ultra good-looking color converter:

```python
import xulbux as xx
from xulbux import S, hexa
from xulbux.base.consts import CHARS


def main() -> None:

    # Let the user enter a hexa color in any format:
    input_clr = xx.console.input(
        (S.BOLD("Enter a HEXA color in any format"), " > "),
        start="\n",
        placeholder="#7075FF",
        max_len=7,
        allowed_chars=CHARS.HEX_DIGITS,
    )

    # Announce indexing the input color:
    xx.console.log("INDEX", "Indexing the input HEXA color...", start="\n", title_bg_color=S.BG.BR.BLUE)

    try:
        # Try to initialize the input string as a `hexa()` object:
        hexa_color = hexa(input_clr)

    except ValueError:
        # Announce the invalid input color and exit the program:
        xx.console.fail("The input HEXA color is invalid.", end="\n\n", exit_code=1)

    # Announce starting the conversion:
    xx.console.log("CONVERT", "Converting the HEXA color into different types...", title_bg_color=S.BG.BR.MAGENTA)

    # Convert the hexa color into the two other color styles:
    rgba_color = hexa_color.as_rgba()
    hsla_color = hexa_color.as_hsla()

    # Announce the successful conversion:
    xx.console.done("Successfully converted color into different types.", end="\n\n")

    # Pretty print the color in different formats:
    xx.console.box(
        (S.BOLD("HEXA: "), (S.ITALIC | S.BR.WHITE)(str(hexa_color))),
        (S.BOLD("RGBA: "), (S.ITALIC | S.BR.WHITE)(str(rgba_color))),
        (S.BOLD("HSLA: "), (S.ITALIC | S.BR.WHITE)(str(hsla_color))),
        "{hr}",
        S.BG.hex(hexa_color).with_text_fg()(" ... .... . -. .- -. .. --. .- -. ... "),
        border_style=S.DIM,
        end="\n\n",
    )


if __name__ == "__main__":
    main()
```

<br>
<br>

-----------------------------------------------------------------
[View this library on **PyPI**](https://pypi.org/project/xulbux)
