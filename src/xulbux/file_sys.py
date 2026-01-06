"""
This module provides the `FileSys` class, which includes
methods to work with the file system and directories.
"""

from .base.types import PathsList
from .base.exceptions import PathNotFoundError
from .base.decorators import mypyc_attr

from typing import Optional
from pathlib import Path
import tempfile as _tempfile
import difflib as _difflib
import shutil as _shutil
import sys as _sys
import os as _os


@mypyc_attr(native_class=False)
class _FileSysMeta(type):

    @property
    def cwd(cls) -> Path:
        """The path to the current working directory."""
        return Path.cwd()

    @property
    def home(cls) -> Path:
        """The path to the user's home directory."""
        return Path.home()

    @property
    def script_dir(cls) -> Path:
        """The path to the directory of the current script."""
        if getattr(_sys, "frozen", False):
            base_path = Path(_sys.executable).parent
        else:
            main_module = _sys.modules["__main__"]
            if hasattr(main_module, "__file__") and main_module.__file__ is not None:
                base_path = Path(main_module.__file__).resolve().parent
            elif (hasattr(main_module, "__spec__") and main_module.__spec__ and main_module.__spec__.origin is not None):
                base_path = Path(main_module.__spec__.origin).resolve().parent
            else:
                raise RuntimeError("Can only get base directory if accessed from a file.")
        return base_path


class FileSys(metaclass=_FileSysMeta):
    """This class provides methods to work with file and directory paths."""

    @classmethod
    def extend_path(
        cls,
        rel_path: Path | str,
        search_in: Optional[Path | str | PathsList] = None,
        raise_error: bool = False,
        use_closest_match: bool = False,
    ) -> Optional[Path]:
        """Tries to resolve and extend a relative path to an absolute path.\n
        -------------------------------------------------------------------------------------------
        - `rel_path` -⠀the relative path to extend
        - `search_in` -⠀a directory or a list of directories to search in,
          in addition to the predefined directories (see exact procedure below)
        - `raise_error` -⠀if true, raises a `PathNotFoundError` if
          the path couldn't be found (otherwise it returns `None`)
        - `use_closest_match` -⠀if true, it will try to find the closest matching file/folder
          names in the `search_in` directories, allowing for typos in `rel_path` and `search_in`\n
        -------------------------------------------------------------------------------------------
        If the `rel_path` couldn't be located in predefined directories,
        it will be searched in the `search_in` directory/s.<br>
        If the `rel_path` is still not found, it returns `None` or
        raises a `PathNotFoundError` if `raise_error` is true."""
        search_dirs: list[Path] = []

        if search_in is not None:
            if isinstance(search_in, (str, Path)):
                search_dirs.extend([Path(search_in)])
            elif isinstance(search_in, list):
                search_dirs.extend([Path(p) for p in search_in])
            else:
                raise TypeError(
                    f"The 'search_in' parameter must be a string, Path, or a list of strings/Paths, got {type(search_in)}"
                )

        # CONVERT rel_path TO PATH
        path = Path(str(rel_path)) if rel_path else None

        if not path or str(path) == "":
            if raise_error:
                raise PathNotFoundError("Path is empty.")
            else:
                return None

        # IF ALREADY ABSOLUTE, RETURN IT
        if path.is_absolute():
            return path

        # EXPAND ENVIRONMENT VARIABLES AND NORMALIZE
        path = Path(cls._expand_env_path(str(path)))

        if path.is_absolute():
            # SPLIT DRIVE AND PATH ON WINDOWS
            if path.drive:
                search_dirs.extend([Path(path.drive + _os.sep)])
                path = Path(*path.parts[1:])  # REMOVE DRIVE FROM PARTS
            else:
                search_dirs.extend([Path(_os.sep)])
                path = Path(*path.parts[1:])  # REMOVE ROOT FROM PARTS
        else:
            search_dirs.extend([Path.cwd(), cls.script_dir, Path.home(), Path(_tempfile.gettempdir())])

        for search_dir in search_dirs:
            full_path = search_dir / path
            if full_path.exists():
                return full_path
            if use_closest_match:
                if (match := cls._find_path(search_dir, path.parts, use_closest_match)):
                    return match

        if raise_error:
            raise PathNotFoundError(f"Path {rel_path!r} not found in specified directories.")
        else:
            return None

    @classmethod
    def extend_or_make_path(
        cls,
        rel_path: Path | str,
        search_in: Optional[Path | str | list[Path | str]] = None,
        prefer_script_dir: bool = True,
        use_closest_match: bool = False,
    ) -> Path:
        """Tries to locate and extend a relative path to an absolute path, and if the `rel_path`
        couldn't be located, it generates a path, as if it was located.\n
        -------------------------------------------------------------------------------------------
        - `rel_path` -⠀the relative path to extend or make
        - `search_in` -⠀a directory or a list of directories to search in,
          in addition to the predefined directories (see exact procedure below)
        - `prefer_script_dir` -⠀if true, the script directory is preferred
          when making a new path (otherwise the CWD is preferred)
        - `use_closest_match` -⠀if true, it will try to find the closest matching file/folder
          names in the `search_in` directories, allowing for typos in `rel_path` and `search_in`\n
        -------------------------------------------------------------------------------------------
        If the `rel_path` couldn't be located in predefined directories,
        it will be searched in the `search_in` directory/s.<br>
        If the `rel_path` is still not found, it will makes a path
        that points to where the `rel_path` would be in the script directory,
        even though the `rel_path` doesn't exist there.<br>
        If `prefer_script_dir` is false, it will instead make a path
        that points to where the `rel_path` would be in the CWD."""
        try:
            result = cls.extend_path(
                rel_path=rel_path,
                search_in=search_in,
                raise_error=True,
                use_closest_match=use_closest_match,
            )
            return result if result is not None else Path()

        except PathNotFoundError:
            path = Path(str(rel_path))
            base_dir = cls.script_dir if prefer_script_dir else Path.cwd()
            return base_dir / path

    @classmethod
    def remove(cls, path: Path | str, only_content: bool = False) -> None:
        """Removes the directory or the directory's content at the specified path.\n
        -----------------------------------------------------------------------------
        - `path` -⠀the path to the directory or file to remove
        - `only_content` -⠀if true, only the content of the directory is removed
          and the directory itself is kept"""
        if not (path_obj := Path(path)).exists():
            return None

        if not only_content:
            if path_obj.is_file() or path_obj.is_symlink():
                path_obj.unlink()
            elif path_obj.is_dir():
                _shutil.rmtree(path_obj)

        elif path_obj.is_dir():
            for item in path_obj.iterdir():
                try:
                    if item.is_file() or item.is_symlink():
                        item.unlink()
                    elif item.is_dir():
                        _shutil.rmtree(item)
                except Exception as e:
                    fmt_error = "\n  ".join(str(e).splitlines())
                    raise Exception(f"Failed to delete {item!r}:\n  {fmt_error}") from e

    @staticmethod
    def _expand_env_path(path_str: str) -> str:
        """Internal method that expands all environment variables in the given path string."""
        if "%" not in path_str:
            return path_str

        for i in range(1, len(parts := path_str.split("%")), 2):
            if parts[i].upper() in _os.environ:
                parts[i] = _os.environ[parts[i].upper()]

        return "".join(parts)

    @classmethod
    def _find_path(cls, start_dir: Path, path_parts: tuple[str, ...], use_closest_match: bool) -> Optional[Path]:
        """Internal method to find a path by traversing the given parts from
        the start directory, optionally using closest matches for each part."""
        current_path: Path = start_dir

        for part in path_parts:
            if current_path.is_file():
                return current_path
            if (closest_match := cls._get_closest_match(current_path, part) if use_closest_match else part) is None:
                return None
            current_path = current_path / closest_match

        return current_path if current_path.exists() and current_path != start_dir else None

    @staticmethod
    def _get_closest_match(dir: Path, path_part: str) -> Optional[str]:
        """Internal method to get the closest matching file or folder name
        in the given directory for the given path part."""
        try:
            items = [item.name for item in dir.iterdir()]
            return matches[0] if (matches := _difflib.get_close_matches(path_part, items, n=1, cutoff=0.6)) else None
        except Exception:
            return None
