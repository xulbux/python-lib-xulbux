# Getting Started

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

## Example Usage

This example demonstrates building an interactive CLI color converter, with its styled terminal output shown below the code:

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

<TerminalOutput>
<span class="b">Enter a hex color in any format</span><span class="dim"> > </span>a8f

<span class="dim">╭───────────────────────────────╮</span>
<span class="dim">│</span> <span class="#000 bg-#A8F">           Preview           </span> <span class="dim">│</span>
<span class="dim">├───────────────────────────────┤</span>
<span class="dim">│</span> <span class="b">HEXA: </span><span class="i">#AA88FF</span>                 <span class="dim">│</span>
<span class="dim">│</span> <span class="b">RGBA: </span><span class="i">rgba(170, 136, 255)</span>     <span class="dim">│</span>
<span class="dim">│</span> <span class="b">HSLA: </span><span class="i">hsla(257°, 100%, 77%)</span>   <span class="dim">│</span>
<span class="dim">╰───────────────────────────────╯</span>
</TerminalOutput>
