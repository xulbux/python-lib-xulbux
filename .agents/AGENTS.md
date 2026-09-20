# Agent Guidelines for `xulbux`

When working on this repository, any AI agent or automated assistant must adhere strictly to the following rules to maintain the codebase's integrity, performance, and correctness.

## 1. Strict Typing (MyPyC Compatibility)

This entire library (including all Python files across all subdirectories of `src/xulbux/`, such as `base/`, `cli/`, etc.) is compiled to C using **MyPyC**. Therefore, **EVERYTHING** must be meticulously and strictly type-hinted. Do not ever use `Any` unless it is fundamentally impossible to type-hint otherwise. All changes must be fully statically analyzable to compile correctly.
*   **No `# type:ignore` Comments:** `# type:ignore` comments are generally forbidden across the library. You must instead use specific `# pyright:ignore[…]` comments with explicit rule IDs and no spaces after commas between rule names (e.g., `# pyright:ignore[reportUnknownMemberType,reportAttributeAccessIssue]`). The ONLY exception is for MyPy/MyPyC: you are permitted to use `# type:ignore[...]` (with explicit rule IDs) if and only if it is absolutely fundamentally required to bypass a MyPyC/MyPy compiler error that cannot be resolved via `# pyright:ignore[…]` or standard typing adjustments, AND rewriting the code to bypass the error statically would decrease performance or reduce code readability.

## 2. Validation & Testing

After making any changes, you must validate them by running the full suite of formatters, linters, type checkers, and tests. Fix all problems until they are completely resolved (zero errors, zero warnings, and zero lint issues). Test coverage must always remain at exactly 100% across all platforms (Windows and Unix). Use the `test` skill for testing guidelines and commands, and the `build` skill for compilation and stub generation.

## 3. Ask, Don't Assume

If you run into anything you are not sure about (ambiguous requirements, complex architectural decisions, edge cases), **ask first**. Do not make assumptions about the desired behavior.

## 4. Performance & MyPyC Idioms

*   **Performance First:** This library prioritizes modernity and speed. Avoid eager imports for heavy operations. Utilize lazy loading via PEP 562 (`__getattr__` in `__init__.py`) and lazy compiled regular expressions (`LazyRegex`).
*   **MyPyC Optimization (CRITICAL):** Because the library in its entirety (all modules and subpackages) is compiled to C via MyPyC, standard Python performance advice doesn't always apply. You must strictly follow these rules everywhere across the codebase:
    *   **Generators (CRITICAL):** NEVER pass generator expressions to functions like `any()`, `all()`, `sum()`, `max()`, `min()`, `join()`, `tuple()`, etc.
        *   For full iterations (`join`, `sum`, `tuple`, `max`), ALWAYS wrap them in brackets `[]` to force an optimized list comprehension.
        *   For short-circuiting functions (`any`, `all`, `next`), write explicit unrolled native `for`-loops with `break` or `return`.
    *   **Membership Testing (CRITICAL):** ALWAYS use `set`s for `in` checks instead of lists or tuples (e.g., `if x in {"a", "b"}:` instead of `if x in ("a", "b"):`).
    *   **String Concatenation:** NEVER use `+=` for string concatenation inside loops; prefer `.join()` with list comprehensions.
    *   **Map & Filter:** NEVER use the `map()` or `filter()` builtins. List comprehensions are strictly faster and type-safer in MyPyC.
*   **DRY Principle (Don't Repeat Yourself):** Always strive to prevent redundant code and duplicate logic. Abstract repeated patterns into reusable helper functions or classes.
*   **Internal Module Aliasing:** When importing internal modules, use the `_module` suffix pattern (e.g., `from . import data as _data_module`). This prevents naming collisions and variable shadowing, and keeps the public API completely clean of internal clutter.

## 5. Code Structure & Readability

*   **Logical Placement:** Do not mindlessly append new code (variables, constants, functions, classes, etc.) to the end of a file. Always insert new code in a logical location that groups related functionality together.
*   **Private Constants Placement:** Private constants and module-level variables (e.g., `_PATTERNS`, caches, lookup tables) should always be defined directly below the imports at the very top of the file.
*   **Spacing & Formatting:** Keep the code "spacy" and readable, matching the current formatting conventions of the repository.
*   **Imports Placement:** Always place imports at the top of the file. The only exception is OS-specific libraries (such as `winreg`, `msvcrt`, `termios`, or `tty`) that do not exist on other operating systems and therefore must be imported inside platform-specific code branches.
*   **Explicit Import Styles:** For libraries like `typing`, `typing_extensions`, `collections.abc`, and `pathlib`, always use explicit `from <module> import ...` statements (e.g., `from typing import overload, Any`, `from pathlib import Path`). Never import the entire module as `import typing` or `import pathlib`.
*   **Naming Conventions:**
    *   **Descriptive Variable Names (CRITICAL):** Single-letter variables (e.g., `x`, `c`, `r`) are strictly banned. You MUST use fully descriptive variable names (e.g., `ch` or `channel`, `red`, `modifier`). The ONLY exceptions are `i` (and rarely `j`) for loop indices, and `n` for mathematical counts/parameters.
    *   **Instance Conversions & Representations:** Instance methods that convert or represent the object in another format or representation must always use the **`as_…()`** prefix (e.g., `.as_dict()`, `.as_tuple()`, `.as_rgba()`, `.as_fg()`, `.as_text_fg()`). Never use `.to_…()` or bare data structure names like `.dict()` or `.values()`.
    *   **Standalone Conversions & Transformations:** Standalone functions must always use the **`to_…`** (or `…_to_…`) prefix when converting, casting, or transforming data from one format/casing/type to another (e.g., `to_rgba()`, `to_camel_case()`, `rgba_to_hex_int()`). Never use `as_…` for standalone functions.
    *   **Extraction vs. Conversion:** Functions that search/parse values out of arbitrary text or unstructured data must use the **`extract_…`** prefix (e.g., `extract_rgba()`, `extract_hsla()`), reserving direct `to_…` / `as_…` naming strictly for direct conversions.
    *   **Verb-First for Actions & Getters:** Functions performing actions or fetching data should start with an active verb (e.g., `count_chars()`, `get_paths()`, `remove_duplicates()`).
    *   **Path Resolution:** Always use standard filesystem terminology like **`resolve_path`** and **`resolve_or_create_path`** instead of non-standard terms like `extend_path`.
    *   **Predicates & Booleans:** Predicate functions and boolean properties/methods must always start with `is_` or `has_` (e.g., `is_light()`, `has_alpha()`, `is_valid_rgba()`, `is_tty()`).
*   **Control Flow (If/Elif & Match-Case):**
    *   **Elif Over If:** Always use `elif` when multiple `if`-statements follow each other checking mutually exclusive conditions or when previous conditions exit early (e.g., `break`, `continue`, `return`, `raise`), provided it does not break the logic. For example, write `if x: return` followed by `elif y: return` rather than chaining multiple independent `if` statements.
    *   **Match-Case:** When repeatedly checking the same variable or expression against different values, use `match`/`case` structural pattern matching instead of a chain of `if`/`elif` statements, unless doing so would decrease performance.
*   **Walrus Operator (`:=`) (CRITICAL):** You MUST use the walrus operator (`:=`) wherever applicable. Specifically, when assigning a variable that is immediately evaluated in an `if` (or `while`) condition and reused, you MUST inline the assignment directly into the condition (e.g., `if (result := process_whatever(input_val)) is None:` instead of assigning `result` on the preceding line). Ensure that when used with compound short-circuiting operators (`and` / `or`), the assignment is guaranteed to evaluate before any subsequent access.
*   **Single-Use Variables & Inlining (CRITICAL):** NEVER assign values to temporary variables that are only accessed once. ALWAYS pass expressions directly into the consuming function, return statement, or assertion (e.g., `print(process_whatever(arg))` instead of `result = process_whatever(arg); print(result)`).
    *   **Exceptions:** Assigning a single-use variable is acceptable and encouraged when inlining would cause an expression to become overly convoluted, hurt readability, or force an otherwise clean call across four or more lines (e.g., complex ternaries like in `color.rgba.invert`), or when caching a costly property or calculation outside a loop to avoid redundant re-evaluations during iteration.
*   **Organization:** When introducing large data structures (like hardcoded iterables or dictionaries), keep them strictly organized and structured. Default to sorting elements alphabetically unless a specific logical order is required.
*   **Ellipsis Usage (`…` vs `...`):** Always use the single Unicode ellipsis character `…` instead of three consecutive dots `...` in all documentation, docstrings, comments, and string truncations (even in console/terminal output). The ONLY exceptions are active processing-indicating prints in the console (e.g., `Loading...`, `Connecting...`), which must use three ASCII dots `...`, and native Python syntax ellipsis in code (`...`).

## 6. Documentation & Markdown Formatting

*   **Mandatory Documentation:** Everything in the library's source code (including private variables, constants, functions, classes, and helper constructs) requires at least a one-line docstring quickly describing what it does or what it is for. The only exceptions are internal dunderscore methods where a docstring is truly redundant.
*   **Docstrings & Comments:** Follow the `docs` skill for all docstring structure, styling, `<br>` line wraps, horizontal rules, custom docs components, and comment/separator conventions.
*   **Markdown Linting:** All Markdown files (`.md`) must strictly adhere to the formatting and linting rules defined in `.markdownlint.json`.
*   **Changelog Maintenance:** When modifying or removing public APIs, behaviors, parameters, or constants that existed in the previous release, briefly document the change under the **current unreleased version section** (topmost version in `CHANGELOG.md` that does not yet have a fixed release date in its title). **NEVER** modify the entries of past, already published releases. If the change breaks existing functionality (e.g., renaming a module, removing a parameter, altering a return type), it MUST be clearly documented under the `**BREAKING CHANGES:**` sub-heading.
    *   **New Modules/Features:** If a module or feature is entirely new in the current unreleased version, simply state that the module/feature was added. **DO NOT** list individual additions, changes, or internal development iterations made to it during its development as non-breaking changes. The changelog is a release summary for end users, not a dev log.

## 7. Dependency Management

*   **Minimum Versions:** If you make use of a new feature from a non-dev dependency (e.g., `prompt_toolkit`, `regex`, `typing_extensions`) that isn't already used elsewhere in the library, you must check if that feature is available in the currently listed minimum version in `pyproject.toml`. If it is not, bump the minimum version of that dependency **only** to the lowest stable version where that feature was introduced, never to the absolute latest version by default.
*   **Synchronization:** If you update any dependency version in `pyproject.toml`, you must ensure that the `__dependencies__` list in `src/xulbux/__init__.py` is updated to perfectly match it.

## 8. Exports & `__init__.py`

*   **Top-level Exports:** Everything (modules and classes) should be exported in the main `src/xulbux/__init__.py` file (and therefore also listed in `__all__` and `_SUBMODULES`).
    *   **Exceptions:** Custom types (type aliases, TypedDicts, etc.) and anything inside the `base` module (like `base.exceptions` or `base.consts`) should **not** be exported to the top-level namespace to keep it clean.

## 9. Rule & Skill Authoring (Single Source of Truth)

To keep agent guidelines clean, maintainable, and free of contradictions, adhere strictly to the Single Source of Truth (SSOT) principle:
*   **Define Once:** Every rule, standard, or guideline must be defined in exactly ONE canonical location:
    *   **`AGENTS.md`:** Repository-wide core policies (strict typing and ignore rules, mandatory documentation, performance and MyPyC idioms, code structure, naming conventions, dependency management, exports).
    *   **Skills (`.agents/skills/<skill>/SKILL.md`):** Specialized domain-specific workflows and detailed formatting specifications (`docs` for docstrings, comments, and section separators; `test` for test suite layout, mocks, and test execution; `build` for compilation and stub generation).
*   **Reference, Never Duplicate:** When a rule defined in one location also applies in another, do NOT duplicate or re-explain the rule. Instead, reference and point directly to its canonical definition in the respective skill or `AGENTS.md`.
*   **Synchronize References:** If a canonical rule is updated or moved, verify that all external references pointing to it are kept accurate.
