<!-- IMPORTANT: Target the active `dev/x.y.z` branch as the base branch – never `main`! -->

## Summary

<!-- What changed and why? Link any related issue (e.g., Closes #12). -->

## Checklist

-   [ ] Base branch is set to the active `dev/x.y.z` branch (not `main`).
-   [ ] `ruff format --check .`, `ruff check .`, `pyright`, `mypy .`, and `pytest` (`100%` coverage) pass with zero errors or warnings.
-   [ ] MyPyC compilation and `.pyi` stub generation (`python setup.py --gen-stubs`) verified if `src/xulbux/` changed.
-   [ ] Docstrings, [`CHANGELOG.md`](CHANGELOG.md) (unreleased `<Release>` block), and `website/` updated where applicable.

