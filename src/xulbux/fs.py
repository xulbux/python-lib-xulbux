"""
Provides file system and path resolution utilities.

Includes fuzzy matching, recursive searching, safe directory creation,
and dynamic access to common paths like `cwd` and `home`.
"""

from . import data as _data_module
from . import string as _string_module
from .base.exceptions import PathNotFoundError, SameContentFileExistsError
from .base.types import PathsList

import difflib as _difflib
import json as _json
import os as _os
import shutil as _shutil
import sys as _sys
import tempfile as _tempfile
from contextlib import suppress as _suppress
from pathlib import Path
from typing import Any, Literal, cast, overload


def get_cwd() -> Path:
    """The path to the current working directory."""

    return Path.cwd()


def get_home() -> Path:
    """The path to the user's home directory."""

    return Path.home()


def get_script_dir() -> Path:
    """The path to the directory of the current script."""

    if getattr(_sys, "frozen", False):
        return Path(_sys.executable).parent

    main_module = _sys.modules["__main__"]

    if hasattr(main_module, "__file__") and main_module.__file__ is not None:
        return Path(main_module.__file__).resolve().parent
    elif hasattr(main_module, "__spec__") and main_module.__spec__ and main_module.__spec__.origin is not None:
        return Path(main_module.__spec__.origin).resolve().parent

    raise RuntimeError("Can only get base directory if accessed from a file")


def resolve_path(
    rel_path: Path | str,
    /,
    search_in: Path | str | PathsList | None = None,
    *,
    fuzzy_match: bool = False,
    raise_error: bool = False,
) -> Path | None:
    """Tries to resolve and extend a relative path to an absolute path.\n
    ----------------------------------------------------------------------------------------------------
    *   `rel_path` – The relative path to extend.
    *   `search_in` – A directory or a list of directories to search in,
        in addition to the predefined directories (see exact procedure below).
    *   `fuzzy_match` – If true, it will try to find the closest matching file/folder
        names in the `search_in` directories, allowing for typos in `rel_path` and `search_in`.
    *   `raise_error` – If true, raises a `PathNotFoundError` if
        the path couldn't be found (otherwise it returns `None`).\n
    ----------------------------------------------------------------------------------------------------
    If the `rel_path` couldn't be located in predefined directories,
    it will be searched in the `search_in` directory/s.<br>
    If the `rel_path` is still not found, it returns `None` or
    raises a `PathNotFoundError` if `raise_error` is true.\n
    ----------------------------------------------------------------------------------------------------
    #### Example Usage

    ```python
    import xulbux as xx

    # Resolve a relative file with fuzzy matching:
    resolved_path = xx.fs.resolve_path("config.json", search_in="./settings", fuzzy_match=True)
    ```"""

    search_dirs: list[Path] = []
    path: Path

    if isinstance(rel_path, str):
        if not rel_path:
            if raise_error:
                raise PathNotFoundError("Given 'rel_path' is an empty string")
            return None
        path = Path(rel_path)
    else:
        path = rel_path

    if path.is_absolute():
        return path

    elif search_in is not None:
        if isinstance(search_in, (str, Path)):
            search_dirs.append(Path(search_in))
        else:
            search_dirs.extend([Path(path) for path in search_in])

    return _ResolvePathHelper(path, search_dirs=search_dirs, fuzzy_match=fuzzy_match, raise_error=raise_error)()


def resolve_or_create_path(
    rel_path: Path | str,
    /,
    search_in: Path | str | PathsList | None = None,
    *,
    prefer_script_dir: bool = True,
    fuzzy_match: bool = False,
) -> Path:
    """Tries to locate and extend a relative path to an absolute path, and if
    the `rel_path` couldn't be located, it generates a path, as if it was located.\n
    ----------------------------------------------------------------------------------------------------
    *   `rel_path` – The relative path to extend or make.
    *   `search_in` – A directory or a list of directories to search in,
        in addition to the predefined directories (see exact procedure below).
    *   `prefer_script_dir` – If true, the script directory is preferred
        when making a new path (otherwise the CWD is preferred).
    *   `fuzzy_match` – If true, it will try to find the closest matching file/folder
        names in the `search_in` directories, allowing for typos in `rel_path` and `search_in`.\n
    ----------------------------------------------------------------------------------------------------
    If the `rel_path` couldn't be located in predefined directories,
    it will be searched in the `search_in` directory/s.<br>
    If the `rel_path` is still not found, it will makes a path
    that points to where the `rel_path` would be in the script directory,
    even though the `rel_path` doesn't exist there.<br>
    If `prefer_script_dir` is false, it will instead make a path
    that points to where the `rel_path` would be in the CWD.\n
    ----------------------------------------------------------------------------------------------------
    #### Example Usage

    ```python
    import xulbux as xx

    # Resolve existing file or compute fallback path in script directory:
    target_path = xx.fs.resolve_or_create_path("data/cache.json")
    ```"""

    try:
        return resolve_path(rel_path, search_in=search_in, raise_error=True, fuzzy_match=fuzzy_match) or Path()

    except PathNotFoundError:
        return (get_script_dir() if prefer_script_dir else Path.cwd()) / Path(str(rel_path))


def create_file(file_path: Path | str, content: str = "", /, *, force: bool = False) -> Path:
    """Create a file with or without content.\n
    ----------------------------------------------------------------------------------------------------
    *   `file_path` – The path where the file should be created.
    *   `content` – The content to write into the file.
    *   `force` – If true, will overwrite existing files without
        throwing an error (errors explained below).\n
    ----------------------------------------------------------------------------------------------------
    The method will throw a `FileExistsError` if a file with the same
    name already exists and a `SameContentFileExistsError` if a file
    with the same name and same content already exists.\n
    ----------------------------------------------------------------------------------------------------
    #### Example Usage

    ```python
    import xulbux as xx

    # Create file safely or force overwrite:
    file_path = xx.fs.create_file("output/result.txt", "Generated content", force=True)
    ```"""

    path = Path(file_path)

    if path.exists() and not force:
        with open(path, encoding="utf-8") as existing_file:
            if existing_file.read() == content:
                raise SameContentFileExistsError("Already created this file (nothing changed)")
        raise FileExistsError("File already exists")

    with open(path, "w", encoding="utf-8") as file:
        file.write(content)

    return path.resolve()


def rename_file_ext(
    file_path: Path | str,
    new_extension: str,
    /,
    *,
    full_extension: bool = False,
    camel_case_filename: bool = False,
) -> Path:
    """Rename the extension of a file.\n
    ----------------------------------------------------------------------------------------------------
    *   `file_path` – The path to the file whose extension should be changed.
    *   `new_extension` – The new extension for the file (with or without dot).
    *   `full_extension` – Whether to replace the full extension (e.g., `.tar.gz`)
        or just the last part of it (e.g., `.gz`).
    *   `camel_case_filename` – Whether to convert the filename to CamelCase
        in addition to changing the files extension.\n
    ----------------------------------------------------------------------------------------------------
    #### Example Usage

    ```python
    import xulbux as xx

    # Rename single extension:
    new_path = xx.fs.rename_file_ext("archive.tar.gz", ".zip")  # archive.tar.zip

    # Replace full compound extension and convert to CamelCase:
    new_path = xx.fs.rename_file_ext(
        "my_data_file.tar.gz",
        ".zip",
        full_extension=True,
        camel_case_filename=True,
    )  # MyDataFile.zip
    ```"""

    path = Path(file_path)
    filename = path.name.split(".", 1)[0] if full_extension else path.stem

    if camel_case_filename:
        filename = _string_module.to_camel_case(filename)
    if new_extension and not new_extension.startswith("."):
        new_extension = "." + new_extension

    return path.parent / f"{filename}{new_extension}"


def remove(path: Path | str, /, *, only_content: bool = False) -> None:
    """Removes the directory or the directory's content at the specified path.\n
    ----------------------------------------------------------------------------------------------------
    *   `path` – The path to the directory or file to remove.
    *   `only_content` – If true, only the content of the directory
        is removed and the directory itself is kept."""

    if not (path_obj := Path(path)).exists():
        return

    def _remove_item(item: Path) -> None:
        try:
            if item.is_file() or item.is_symlink():
                item.unlink()
            elif item.is_dir():
                _shutil.rmtree(item)
        except Exception as exc:
            raise RuntimeError(f"Failed to delete {item!r}:\n  {'\n  '.join(str(exc).splitlines())}") from exc

    if not only_content:
        _remove_item(path_obj)
    elif path_obj.is_dir():
        for child in path_obj.iterdir():
            _remove_item(child)
    else:
        raise NotADirectoryError(f"Cannot remove only_content of non-directory {path_obj!r}")


@overload
def read_json(
    json_file: Path | str,
    /,
    *,
    comment_start: str = ">>",
    comment_end: str = "<<",
    return_original: Literal[True],
) -> tuple[dict[str, Any], dict[str, Any]]: ...
@overload
def read_json(
    json_file: Path | str,
    /,
    *,
    comment_start: str = ">>",
    comment_end: str = "<<",
    return_original: Literal[False] = False,
) -> dict[str, Any]: ...
@overload
def read_json(
    json_file: Path | str,
    /,
    *,
    comment_start: str = ">>",
    comment_end: str = "<<",
    return_original: bool,
) -> dict[str, Any] | tuple[dict[str, Any], dict[str, Any]]: ...


def read_json(
    json_file: Path | str,
    /,
    *,
    comment_start: str = ">>",
    comment_end: str = "<<",
    return_original: bool = False,
) -> dict[str, Any] | tuple[dict[str, Any], dict[str, Any]]:
    """Read JSON files, ignoring comments.\n
    ----------------------------------------------------------------------------------------------------
    *   `json_file` – The path (relative or absolute) to the JSON file to read.
    *   `comment_start` – The string that indicates the start of a comment.
    *   `comment_end` – The string that indicates the end of a comment.
    *   `return_original` – If true, the original JSON data is returned additionally:
        ```python
        (processed_json, original_json)
        ```\n
    ----------------------------------------------------------------------------------------------------
    For more detailed information about the comment handling,
    see the `_data_module.remove_comments()` method documentation.\n
    ----------------------------------------------------------------------------------------------------
    #### Example Usage

    ```python
    import xulbux as xx

    # Read JSON and strip comments:
    config = xx.fs.read_json("config.json")

    # Read both stripped and raw original data with comments:
    clean_data, raw_data = xx.fs.read_json("config.json", return_original=True)
    ```"""

    if (json_path := Path(json_file) if isinstance(json_file, str) else json_file).suffix != ".json":
        json_path = json_path.with_suffix(".json")
    file_path = resolve_path(json_path) or json_path

    with open(file_path, encoding="utf-8") as file:
        try:
            data = cast("dict[str, Any]", _json.loads(file.read()))
        except _json.JSONDecodeError as exc:
            raise ValueError(f"Error parsing JSON in {file_path!r}:\n  {'\n  '.join(str(exc).splitlines())}") from exc

    if not (processed_data := _data_module.remove_comments(data, comment_start=comment_start, comment_end=comment_end)):
        raise ValueError(f"The JSON file {file_path!r} contains no data")

    return (processed_data, data) if return_original else processed_data


def create_json(
    json_file: Path | str,
    data: dict[str, Any],
    /,
    *,
    indent: int = 2,
    compactness: Literal[0, 1, 2] = 1,
    force: bool = False,
) -> Path:
    """Create a nicely formatted JSON file from a dictionary.\n
    ----------------------------------------------------------------------------------------------------
    *   `json_file` – The path (relative or absolute) to the JSON file to create.
    *   `data` – The dictionary data to write to the JSON file.
    *   `indent` – The amount of spaces to use for indentation.
    *   `compactness` – Can be `0`, `1` or `2` and indicates how compact
        the data should be formatted (see `_data_module.render()` for more info).
    *   `force` – If true, will overwrite existing files
        without throwing an error (errors explained below).\n
    ----------------------------------------------------------------------------------------------------
    The method will throw a `FileExistsError` if a file with the same
    name already exists and a `SameContentFileExistsError` if a file
    with the same name and same content already exists.\n
    ----------------------------------------------------------------------------------------------------
    #### Example Usage

    ```python
    import xulbux as xx

    data = {
        "app": "my-tool",
        "version": "1.0.0",
        "settings": {"debug": True, "workers": 4},
    }

    file_path = xx.fs.create_json("config.json", data, indent=2, force=True)
    ```"""

    if (json_path := Path(json_file) if isinstance(json_file, str) else json_file).suffix != ".json":
        json_path = json_path.with_suffix(".json")

    file_path = resolve_or_create_path(json_path, prefer_script_dir=True)
    create_file(
        file_path,
        _data_module.render(data, indent=indent, compactness=compactness, as_json=True, syntax_highlighting=False).raw,
        force=force,
    )

    return file_path


def update_json(
    json_file: Path | str,
    update_values: dict[str, Any],
    /,
    *,
    comment_start: str = ">>",
    comment_end: str = "<<",
    path_sep: str = "->",
) -> None:
    """Update single/multiple values inside JSON files, without needing to know the rest of the data.\n
    ----------------------------------------------------------------------------------------------------
    *   `json_file` – The path (relative or absolute) to the JSON file to update.
    *   `update_values` – A dictionary where keys are the paths to the values to update
        and values are the new values to set.
        Dictionaries are addressed by key name, and sequences by integer index.<br>
        Missing paths will automatically be created.
    *   `comment_start` – The string that indicates the start of a comment.
    *   `comment_end` – The string that indicates the end of a comment.
    *   `path_sep` – The separator used inside the value-paths in `update_values`.\n
    ----------------------------------------------------------------------------------------------------
    For more detailed information about comment handling,
    see the `data.remove_comments()` method documentation.\n
    ----------------------------------------------------------------------------------------------------
    #### Example Usage

    ```python
    import xulbux as xx

    data = {
        "healthy": {
            "fruits": ["apples", "bananas", "oranges"],
            "vegetables": ["carrots", "broccoli", "celery"],
        },
    }
    xx.fs.create_json("diet.json", data, force=True)

    # Update nested list values by index and dict values by key name:
    xx.fs.update_json(
        "diet.json",
        {
            "healthy->fruits->0": "strawberries",
            "healthy->vegetables": ["spinach", "kale"],
        },
    )
    ```

    <!-- DOCS: <AttachedCode> -->
    Updated JSON Data:

    ```python
    {
        "healthy": {
            "fruits": ["strawberries", "bananas", "oranges"],
            "vegetables": ["spinach", "kale"],
        }
    }
    ```
    <!-- DOCS: </AttachedCode> -->"""

    processed_data, data = read_json(json_file, comment_start=comment_start, comment_end=comment_end, return_original=True)
    path_updates: dict[str, Any] = {}

    for val_path, new_val in update_values.items():
        try:
            if (path_id := _data_module.get_path_id(processed_data, val_path, path_sep=path_sep)) is not None:
                path_updates[path_id] = new_val
            else:
                data = _create_nested_path(data, val_path.split(path_sep), new_val)
        except Exception:
            data = _create_nested_path(data, val_path.split(path_sep), new_val)

    if path_updates:
        data = _data_module.set_value_by_path_id(data, path_updates)

    create_json(json_file, data, force=True)


def _create_nested_path(data_obj: dict[str, Any], path_keys: list[str], value: Any, /) -> dict[str, Any]:
    """Internal method that creates nested dictionaries/lists based on the
    given path keys and sets the specified value at the end of the path."""

    last_idx, current = len(path_keys) - 1, cast("dict[str, Any] | list[Any]", data_obj)

    for i, key in enumerate(path_keys):
        if i == last_idx:
            if isinstance(current, dict):
                current[key] = value

            elif isinstance(current, list) and key.isdigit():  # pyright:ignore[reportUnnecessaryIsInstance]
                idx = int(key)
                while len(current) <= idx:
                    current.append(None)
                current[idx] = value

            else:
                raise TypeError(f"Cannot set key {key!r} on {type(current).__name__!r}")

        else:
            next_key = path_keys[i + 1]
            if isinstance(current, dict):
                if key not in current:
                    current[key] = [] if next_key.isdigit() else {}
                current = cast("dict[str, Any] | list[Any]", current[key])

            elif isinstance(current, list) and key.isdigit():  # pyright:ignore[reportUnnecessaryIsInstance]
                idx = int(key)
                while len(current) <= idx:
                    current.append(None)
                if current[idx] is None:
                    current[idx] = [] if next_key.isdigit() else {}
                current = cast("dict[str, Any] | list[Any]", current[idx])

            else:
                raise TypeError(f"Cannot navigate through {type(current).__name__!r}")

    return data_obj


class _ResolvePathHelper:
    """Internal, callable helper class to find and resolve a relative path to an absolute path."""

    def __init__(self, rel_path: Path, /, search_dirs: list[Path], *, fuzzy_match: bool, raise_error: bool) -> None:
        self.rel_path: Path = rel_path
        self.search_dirs: list[Path] = search_dirs
        self.fuzzy_match: bool = fuzzy_match
        self.raise_error: bool = raise_error

    def __call__(self) -> Path | None:
        """Find the matching path for `self.rel_path` in `self.search_dirs`."""

        expanded_path = self.expand_env_vars(self.rel_path)

        if expanded_path.is_absolute():
            # Add root to search dirs:
            if expanded_path.drive:
                self.search_dirs.append(Path(expanded_path.drive + _os.sep))
            else:
                self.search_dirs.append(Path(_os.sep))

            expanded_path = Path(*expanded_path.parts[1:])  # Remove root from path parts for searching.

        else:
            # Add predefined search dirs:
            predefined_dirs = [get_cwd(), get_home()]
            with _suppress(RuntimeError):
                predefined_dirs.append(get_script_dir())
            predefined_dirs.append(Path(_tempfile.gettempdir()))
            self.search_dirs.extend(predefined_dirs)

        return self.search_in_dirs(expanded_path)

    @staticmethod
    def expand_env_vars(path: Path, /) -> Path:
        """Expand all environment variables in the given path."""

        if "%" not in (str_path := str(path)) and "$" not in str_path:
            return path

        return Path(_os.path.expandvars(str_path))

    def search_in_dirs(self, path: Path, /) -> Path | None:
        """Search for the path in all configured directories."""

        for search_dir in self.search_dirs:
            if (full_path := search_dir / path).exists():
                return full_path
            elif self.fuzzy_match and (match := self.find_path(search_dir, path, fuzzy_match=self.fuzzy_match)) is not None:
                return match

        if self.raise_error:
            raise PathNotFoundError(f"Path {self.rel_path!r} not found in specified directories")

        return None

    def find_path(self, base_dir: Path, target_path: Path, /, *, fuzzy_match: bool) -> Path | None:
        """Find a path by traversing the given parts from the base directory,
        optionally using closest matches for each part."""

        current_path: Path = base_dir

        for part in target_path.parts:
            if current_path.is_file():
                return current_path
            elif (closest_match := self.get_closest_match(current_path, part) if fuzzy_match else part) is None:
                return None
            current_path = current_path / closest_match

        return current_path if current_path.exists() and current_path != base_dir else None

    @staticmethod
    def get_closest_match(directory: Path, path_part: str, /) -> str | None:
        """Internal method to get the closest matching file or folder name
        in the given directory for the given path part."""

        try:
            return (
                matches[0]
                if (
                    matches := _difflib.get_close_matches(
                        path_part, [item.name for item in directory.iterdir()], n=1, cutoff=0.6
                    )
                )
                else None
            )

        except Exception:
            return None
