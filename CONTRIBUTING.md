# Contributing to `xulbux`

Thanks for contributing to the Python library [**`xulbux`**](https://xulbux.github.io/python-lib-xulbux)!

<br>

## <a href="#table-of-contents"><img src="https://svg.xul.is/icon/list?size=32&stroke=2" align="left" /></a>Table of Contents

-   [Ways to Contribute](#ways-to-contribute)
-   [Getting Started](#getting-started)
-   [Project Structure](#project-structure)
-   [Code Style & Gotchas](#code-style--gotchas)
-   [Branching & Pull Requests](#branching--pull-requests)

<br>
<br>

## <a href="#ways-to-contribute"><img src="https://svg.xul.is/icon/compass?size=32&stroke=2" align="left" /></a>Ways to Contribute

-   **Bug Fixes:** Fixes across any module or CLI command paired with cross-platform regression tests (`100%` coverage).
-   **Features & Utilities:** Clean, typed utilities, color/string/data helpers, or CLI improvements aligned with existing APIs.
-   **Performance & MyPyC:** C-compilation optimizations, lazy imports, or algorithmic speedups.
-   **Docs & Website:** Docstring examples, clearer guides, or VitePress documentation site polish (`website/`).

> [!NOTE]<br>
> Planning a new module, breaking API change, or major feature? Open an [**Issue**](https://github.com/xulbux/python-lib-xulbux/issues) first so we can align on the design.

<br>

## <a href="#getting-started"><img src="https://svg.xul.is/icon/rocket?size=32&stroke=2" align="left" /></a>Getting Started

-   **Python:** `>= 3.12` (`3.12` – `3.14`), plus a C compiler (MSVC Build Tools on Windows, `gcc`/`clang` on Linux/macOS) when testing full MyPyC compilation
-   **Website (optional):** **Node.js** `>= 26` and **pnpm** `>= 11` (only needed when working on `website/`)

```bash
git clone https://github.com/xulbux/python-lib-xulbux.git
cd python-lib-xulbux

# Create & activate a virtual environment (Linux/macOS; on Windows PowerShell: .venv\Scripts\Activate.ps1):
python -m venv .venv
source .venv/bin/activate

# Install in editable mode with all dev & type-checking tools:
pip install -e ".[dev]"

# Format, lint, type-check & run tests (enforces 100% coverage):
ruff format --check .
ruff check .
pyright
mypy .
pytest
```

To verify `.pyi` stub generation and a full MyPyC C-extension compile:

```bash
python setup.py --gen-stubs
pip install . --no-deps --no-cache-dir --force-reinstall -vv
```

To preview and validate the documentation website (`website/`):

```bash
pnpm --dir website install
python website/build.py --dev   # Local VitePress preview
pnpm --dir website run check    # Format, lint, Markdown lint & type-check
```

<br>

## <a href="#project-structure"><img src="https://svg.xul.is/icon/layers?size=32&stroke=2" align="left" /></a>Project Structure

-   **`src/xulbux/`** – Library source compiled to native C extensions via **MyPyC** (`setup.py`), with public modules (`ansi`, `cli`, `color`, `console`, `data`, `fs`, `regex`, `string`, `system`) and shared internals (`base/`).
-   **`tests/`** – Domain-split `pytest` suite (`tests/test_<module>/`) mirroring `src/xulbux/` with `100%` line and branch coverage.
-   **`website/`** – Custom documentation pipeline (`website/build.py`) that extracts API references from docstrings and `.pyi` stubs into VitePress (`website/src/`).

<br>

## <a href="#code-style--gotchas"><img src="https://svg.xul.is/icon/shield-check?size=32&stroke=2" align="left" /></a>Code Style & Gotchas

-   **Strict Typing (MyPyC):** Every file in `src/xulbux/` compiles to C via MyPyC – type-hint everything strictly, avoid `Any`, and never use `# type:ignore` (`enableTypeIgnoreComments = false`; use explicit `# pyright:ignore[ruleId]`).
-   **MyPyC Performance Idioms:** Wrap comprehensions in `[…]` instead of passing bare generators to `join()`, `sum()`, `tuple()`, `max()`, or `min()`; unroll `any()` / `all()` / `next()` into explicit `for`-loops; use `set` literals for `in` checks; and avoid `map()`, `filter()`, or `+=` string concatenation in loops.
-   **Naming & Exports:** Use descriptive variable names (no single-letter names except `i`, `j`, `n`), `.as_…()` for instance conversions, `to_…()` for standalone conversions, `extract_…()` for parsers, `is_` / `has_` for predicates, and the walrus operator (`:=`) where applicable. Export public modules/classes in `src/xulbux/__init__.py` (excluding custom types and `base.*`).
-   **Docstrings & Comments:** Every symbol requires a docstring (`<= 99` chars wide, `100`-char `---…` dividers, class parameters documented on the class rather than `__init__`, `…` instead of `...`). Backtick code in comments, end block comments with `:`, and end inline comments with `.`.
-   **100% Cross-Platform Coverage:** All Windows and POSIX branches must be covered (`100%` enforced by `pytest-cov`). Mock `ctypes.windll` (via `mock_ctypes_windll` or `raising=False`) and `msvcrt` (via `sys.modules`) safely so tests pass on every OS.
-   **Dependencies:** Only bump minimum dependency versions in `pyproject.toml` to the lowest version introducing a required feature, and keep `__dependencies__` in `src/xulbux/__init__.py` in sync.
-   **Full Guidelines:** See [`.agents/AGENTS.md`](.agents/AGENTS.md) and `.agents/skills/` ([`docs`](.agents/skills/docs/SKILL.md), [`test`](.agents/skills/test/SKILL.md), [`build`](.agents/skills/build/SKILL.md)) for complete architecture, docstring, and testing specifications.

<br>

## <a href="#branching--pull-requests"><img src="https://svg.xul.is/icon/git-pull-request?size=32&stroke=2" align="left" /></a>Branching & Pull Requests

-   **Target the Active `dev/x.y.z` Branch:** `main` tracks the latest published PyPI release and live documentation site – **never open contributor PRs against `main`**. Branch from and open your PR against the active `dev/x.y.z` branch (e.g., `dev/2.0.1`).
-   **Changelog:** Document public API additions, changes, fixes, or breaking changes under the topmost unreleased `<Release>` block (`date=""`) in [`CHANGELOG.md`](CHANGELOG.md) (never edit already published releases).
-   **Verify & Submit:** Ensure Ruff, PyRight, MyPy, `pytest` (`100%` coverage), and MyPyC compilation pass, then open a Pull Request. Code contributions are licensed under the [**MIT License**](LICENSE) (project artwork and branding in `assets/` remain reserved).
