<span id="top" />

<div align="center">
<br><br>
<h1>
<a href="https://xulbux.github.io/python-lib-xulbux"><img height="64" src="https://github.com/xulbux/python-lib-xulbux/blob/main/assets/icon.svg?raw=true"></a>
<br>
Python library <code>xulbux</code>
<br><br>
<a href="https://pypi.org/project/xulbux"><img src="https://img.shields.io/pypi/v/xulbux?style=flat&labelColor=404060&color=7075FF"/></a> <a href="https://clickpy.clickhouse.com/dashboard/xulbux"><img src="https://img.shields.io/pepy/dt/xulbux?style=flat&labelColor=404060&color=7075FF"/></a> <a href="https://github.com/xulbux/python-lib-xulbux/blob/main/LICENSE"><img src="https://img.shields.io/github/license/xulbux/python-lib-xulbux?style=flat&labelColor=404060&color=A6A8FF"/></a> <a href="https://github.com/xulbux/python-lib-xulbux/commits"><img src="https://img.shields.io/github/last-commit/xulbux/python-lib-xulbux?style=flat&labelColor=554046&color=FF6680"/></a> <a href="https://github.com/xulbux/python-lib-xulbux/issues"><img src="https://img.shields.io/github/issues/xulbux/python-lib-xulbux?style=flat&labelColor=554046&color=FF6680"/></a> <a href="https://github.com/xulbux/python-lib-xulbux/stargazers"><img src="https://img.shields.io/github/stars/xulbux/python-lib-xulbux?label=★&style=flat&labelColor=554046&color=FF8FA2"/></a>
</h1>
<h3>A modern, high-performance Python library to simplify common tasks.</h3>
<br><br>
</div>

**`xulbux`** is a library that contains many useful classes, types, and functions,
ranging from terminal logging and working with colors to file management and system operations.
The library is designed to simplify common programming tasks and improve code readability through its collection of tools.

For precise information about the library, see the library's [**documentation**](https://xulbux.github.io/python-lib-xulbux/docs).<br>
For the library's latest changes and updates, see the [**change log**](https://xulbux.github.io/python-lib-xulbux/changelog).

> <br>
> ⚡ To see what this library can do, check out the <a href="#modules"><b>modules overview</b></a> or explore the <a href="#example-usage"><b>live example</b></a>.
> <br>
> <br>

<br>
<br>

<span id="installation" />

## Installation 📦

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

<span id="modules" />

## Modules ⚡

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
      <td>File system utilities including fuzzy path resolution, enhanced JSON file handling, safe directory creation, and common system path lookups.</td>
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

<span id="usage" />

## Usage ⚙️

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

<span id="cli-commands" />

## CLI Commands 🔧

When the library is installed, the following commands are available in the terminal:

<table>
  <thead>
    <tr>
      <th align="left">Command</th>
      <th align="left">Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>xulbux-lib</code></td>
      <td>Show some information about the library.</td>
    </tr>
    <tr>
      <td><code>xulbux-lib <b>ansi</b></code></td>
      <td>Preview all possible ANSI styles in the terminal.</td>
    </tr>
    <tr>
      <td><code>xulbux-lib <b>c256</b></code></td>
      <td>Show a map of all 256-colors in the terminal.</td>
    </tr>
    <tr>
      <td><code>xulbux-lib <b>tc</b></code></td>
      <td>Show a true-color gradient map in the terminal.</td>
    </tr>
  </tbody>
</table>

<br>

<span id="example-usage" />

## Example Usage ✨

This is what a simple but very good-looking color converter looks like in action:

<a href="https://github.com/xulbux/python-lib-xulbux/blob/main/assets/example.png"><img width="520" src="https://github.com/xulbux/python-lib-xulbux/blob/main/assets/example.png?raw=true" alt="Example color converter terminal output"></a>

<br>

### Code

```python
import xulbux as xx
from xulbux import S, hexa


def hex_validator(input_str: str) -> str | None:
    """User input validator for hex color strings."""

    if xx.color.is_valid_hexa(input_str):
        if xx.color.has_alpha(input_str):
            return "The input color cannot contain an alpha channel."
        return None  # Return `None` if the input is valid.
    return f"{input_str!r} is not a valid hex color."


def main() -> None:

    # User input with realtime validation:
    input_hexa_str = xx.console.input(
        (S.BOLD("Enter a hex color in any format"), S.DIM(" > ")),
        start="\n",
        end="\n",
        placeholder="#FF3D5D",
        validator=hex_validator,
    )

    # Initialize the already validated hex color string as a `hexa()` object:
    hexa_color = hexa(input_hexa_str)

    # Pretty print the color in different formats:
    xx.console.box(
        (S.BOLD | S.BG.hex(hexa_color).with_text_fg())("           Preview           "),
        "{hr}",
        (S.BOLD("HEXA: "), S.ITALIC(str(hexa_color))),
        (S.BOLD("RGBA: "), S.ITALIC(str(hexa_color.as_rgba()))),
        (S.BOLD("HSLA: "), S.ITALIC(str(hexa_color.as_hsla()))),
        border_style=S.DIM,
        end="\n\n",
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
```

<br>
<br>
<br>

## Enjoying this library? Have suggestions?

Please consider giving a ⭐ on [**GitHub**](https://github.com/xulbux/python-lib-xulbux) or suggesting improvements in the [**Discussions**](https://github.com/xulbux/python-lib-xulbux/discussions).

<br>
<br>
<br>

---

✨ Always creating more cool stuff for you! ✨ —⠀[**XulbuX**](https://xulbux.com)
