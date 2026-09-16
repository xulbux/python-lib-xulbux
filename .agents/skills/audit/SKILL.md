---
name: audit
description: Audits the xulbux codebase for Python 3.12+ modernity, MyPyC performance idioms, rule compliance, and quality, then applies fixes and verifies the build and test suite.
---

# Audit

Use this skill to perform an automated, end-to-end quality and performance audit across the `xulbux` library, apply concrete improvements, and verify that all linting, type-checking, tests, and MyPyC builds pass cleanly.

---

## 1. Scope & Execution Principles

1.  **Preparation (SSOT):** You MUST read `AGENTS.md`, the `docs` skill, and the `test` skill to load the canonical rules into your context before beginning the audit. Do not guess the rules or rely solely on this checklist.
2.  **Direct Execution:** Systematically inspect the source files in `src/xulbux/` and their corresponding test files in `tests/`. Apply verified improvements directly to the files.
3.  **Zero Unnecessary Churn:** If a module, function, or class already adheres to repository guidelines, optimal typing, and performant MyPyC idioms, **do not modify it**. If there are no actual improvements to make, state that honestly rather than making arbitrary cosmetic tweaks that offer no practical benefit.

---

## 2. Audit Checklist

While scanning the codebase, specifically evaluate the following areas by cross-referencing the canonical rules you read during Preparation:

### A. Python 3.12+ Modernity

-   **PEP 695 Type Parameters:** Use native type parameter syntax for generic functions and classes where supported by MyPyC.
-   **Type Aliases:** Use the native `type` statement where appropriate.
-   **Union Syntax:** Consistently use pipe syntax (`X | Y`) rather than `Union` or `Optional`.
-   **Standard Library Updates:** Replace obsolete patterns with modern 3.12+ stdlib additions.

### B. Performance & MyPyC Idioms

-   Evaluate all rules listed in **`AGENTS.md` Section 4**.
-   Pay special attention to eliminating generators in favor of list comprehensions/unrolled loops, enforcing `set` lookups, and avoiding `map()`/`filter()` or `+=` string concatenations in loops.

### C. Code Quality, Structure & Idiomatic Conventions

-   Evaluate all rules listed in **`AGENTS.md` Section 5**.
-   Ensure logical grouping, correct private constant placement, and appropriate use of the walrus operator.
-   Check for any redundant, duplicated, or highly convoluted code, abstracting it into reusable helpers or moving duplicate magic methods (e.g. `__or__`, `__add__`) up into common base classes.
-   Check for redundant API options or syntaxes that give the user multiple ways to do the same thing (e.g., alias operators or duplicate methods). **IMPORTANT:** If you find these, you MUST ask the user for their preference before removing or altering anything; do not blindly remove them, as the user may want to keep a specific variation or alter the underlying logic instead.
-   Ensure all single-use variables are inlined.
-   Check that descriptive, multi-letter variable names are used. Single-letter variables like `x` or `c` are strictly banned (except loop indices `i`/`j` and mathematical `n`).
-   Hunt for potential runtime bugs or logical edge cases.

### D. Documentation & Comment Compliance

-   Evaluate all rules listed in the **`docs` Skill**.
-   Verify docstring formatting, text width, HTML tags (`<br>`), exact horizontal rule/section separator lengths, and comment styles (e.g., `[1]` for numbered steps).

---

## 3. Post-Refactor Verification

After applying changes, you MUST run the automated validation commands and resolve any failures:

### [1] Formatters, Linters & Tests (`test` Skill Section 5)

**On Unix:**

```bash
ruff format . && ruff check . --fix && pyright --pythonpath .venv/bin/python . && mypy . && pytest -q --disable-warnings
```

**On Windows:**

```powershell
ruff format . ; if ($?) { ruff check . --fix } ; if ($?) { pyright --pythonpath "$(py -c 'import sys; print(sys.executable)')" . } ; if ($?) { mypy . } ; if ($?) { pytest --basetemp .pytest_tmp -q --disable-warnings }
```

Ensure test coverage remains at exactly **100%**.

### [2] MyPyC Compilation & Stub Generation (`build` Skill)

Verify that all changes compile under MyPyC and generate `.pyi` stubs without errors:

**On Unix:**

```bash
python setup.py --gen-stubs && pip install . --no-deps --no-cache-dir --force-reinstall -vv
```

**On Windows:**

```powershell
py setup.py --gen-stubs ; if ($?) { py -m pip install . --no-deps --no-cache-dir --force-reinstall -vv }
```

---

## 4. Audit Summary Format

Once all steps pass, conclude with a concise summary structured as follows:

-   **MyPyC & Performance Fixes:** Specific loops, comprehensions, sets, or early-binding adjustments applied.
-   **Modernity (Python 3.12+):** Type parameter syntax, type aliases, or stdlib upgrades applied.
-   **Style, Documentation & Rules:** Inlined expressions, walrus usages, docstring formatting, or separator adjustments.
-   **Unchanged Modules:** Note modules that were inspected and found fully optimal.
