from setuptools import setup
from pathlib import Path
import os


def find_python_files(directory: str) -> list[str]:
    python_files: list[str] = []
    for file in Path(directory).rglob("*.py"):
        python_files.append(str(file))
    return python_files


# OPTIONALLY USE MYPYC COMPILATION
ext_modules = []
if os.environ.get("XULBUX_USE_MYPYC", "1") == "1":
    try:
        from mypyc.build import mypycify
        print("\nCompiling with mypyc...\n")
        source_files = find_python_files("src/xulbux")
        ext_modules = mypycify(source_files)

    except (ImportError, Exception) as e:
        fmt_error = "\n  ".join(str(e).splitlines())
        print(
            f"\n[WARNING] mypyc compilation disabled (not available or failed):\n  {fmt_error}\n"
            "\nInstalling as pure Python package...\n"
        )

setup(
    name="xulbux",
    ext_modules=ext_modules,
)
