from mypyc.build import mypycify
from setuptools import setup
from pathlib import Path


def find_python_files(directory: str) -> list[str]:
    python_files: list[str] = []
    for file in Path(directory).rglob("*.py"):
        python_files.append(str(file))
    return python_files


source_files = find_python_files("src/xulbux")

setup(
    name="xulbux",
    ext_modules=mypycify(source_files),
)
