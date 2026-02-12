from setuptools import setup
from pathlib import Path
import subprocess
import sys
import os


def find_python_files(directory: str) -> list[str]:
    python_files: list[str] = []
    for file in Path(directory).rglob("*.py"):
        python_files.append(str(file))
    return python_files


def generate_stubs_for_package():
    print("\nGenerating stub files with stubgen...\n")

    try:
        skip_stubgen = {
            Path("src/xulbux/base/types.py"),  # COMPLEX TYPE DEFINITIONS
        }

        src_dir = Path("src/xulbux")
        generated_count = 0
        skipped_count = 0

        for py_file in src_dir.rglob("*.py"):
            pyi_file = py_file.with_suffix(".pyi")
            rel_path = py_file.relative_to(src_dir.parent)

            if py_file in skip_stubgen:
                pyi_file.write_text(py_file.read_text(encoding="utf-8"), encoding="utf-8")
                print(f"  copied {rel_path.with_suffix('.pyi')} (preserving type definitions)")
                skipped_count += 1
                continue

            result = subprocess.run(
                [sys.executable, "-m", "mypy.stubgen",
                 str(py_file),
                 "-o", "src",
                 "--include-private",
                 "--export-less"],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                print(f"  generated {rel_path.with_suffix('.pyi')}")
                generated_count += 1
            else:
                print(f"  failed {rel_path}")
                if result.stderr:
                    print(f"    {result.stderr.strip()}")

        print(f"\nStub generation complete. ({generated_count} generated, {skipped_count} copied)\n")

    except Exception as e:
        fmt_error = "\n  ".join(str(e).splitlines())
        print(f"[WARNING] Could not generate stubs:\n  {fmt_error}\n")


ext_modules = []

# OPTIONALLY USE MYPYC COMPILATION
if os.environ.get("XULBUX_USE_MYPYC", "1") == "1":
    try:
        from mypyc.build import mypycify

        print("\nCompiling with mypyc...\n")
        source_files = find_python_files("src/xulbux")
        ext_modules = mypycify(source_files, opt_level="3")
        print("\nMypyc compilation complete.\n")

        generate_stubs_for_package()

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
