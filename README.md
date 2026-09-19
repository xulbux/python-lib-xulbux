<span id="top" />

<div align="center">
<br><br>
<h1>
<a href="https://xulbux.github.io/python-lib-xulbux"><img height="64" src="https://github.com/xulbux/python-lib-xulbux/blob/main/assets/icon.svg?raw=true"></a>
<br>
Python library <code>xulbux</code>
<br><br>
<a href="https://pypi.org/project/xulbux"><img src="https://img.shields.io/pypi/v/xulbux?style=flat&labelColor=404060&color=7075FF"/></a> <a href="https://clickpy.clickhouse.com/dashboard/xulbux"><img src="https://img.shields.io/pepy/dt/xulbux?style=flat&labelColor=404060&color=7075FF"/></a> <a href="https://github.com/xulbux/python-lib-xulbux/blob/main/LICENSE"><img src="https://img.shields.io/github/license/xulbux/python-lib-xulbux?style=flat&labelColor=404060&color=A6A8FF"/></a> <a href="https://github.com/xulbux/python-lib-xulbux/commits"><img src="https://img.shields.io/github/last-commit/xulbux/python-lib-xulbux?style=flat&labelColor=554046&color=FF6680"/></a> <a href="https://github.com/xulbux/python-lib-xulbux/issues"><img src="https://img.shields.io/github/issues/xulbux/python-lib-xulbux?style=flat&labelColor=554046&color=FF6680"/></a> <a href="https://github.com/xulbux/python-lib-xulbux/stargazers"><img src="https://img.shields.io/github/stars/xulbux/python-lib-xulbux?label=★&style=flat&labelColor=554046&color=FF8FA2"/></a>
</h1>
<h3>A modern, high-performance Python library to simplify common tasks.</h3>
<br><br>
</div>

**`xulbux`** is a modern, high-performance Python library compiled to C using MyPyC.<br>
It provides a clean, unified suite of utilities for typed terminal styling, color space manipulation, data processing, file system operations, and system automation.

<br>

> <br>
> 🌐 <b>Official Website:</b> Visit <a href="https://xulbux.github.io/python-lib-xulbux"><b>xulbux.github.io/python-lib-xulbux</b></a><br>
> ⚡ <b>Live Example:</b> Check out the <a href="https://xulbux.github.io/python-lib-xulbux/docs/guide/get-started#example-usage"><b>example CLI color converter</b></a> with live terminal preview.<br>
> 📖 <b>API Reference:</b> Explore all modules in the <a href="https://xulbux.github.io/python-lib-xulbux/docs"><b>API Documentation</b></a>.
> <br><br>

<br>
<br>

<span id="installation" />

## Installation 📦

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

<span id="quick-start" />

## Quick Start ⚙️

```python
import xulbux as xx
from xulbux import S

# Operator-based terminal styling:
(S.BOLD | S.BR.BLUE)("Hello from xulbux!").print()

# Interactive terminal box:
xx.console.box("Ready to build something great.")
```

For full usage guides, visit the [**Getting Started Guide**](https://xulbux.github.io/python-lib-xulbux/docs/guide/get-started) and [**CLI Tools Guide**](https://xulbux.github.io/python-lib-xulbux/docs/guide/cli-tools).

<br>
<br>
<br>

<span id="feedback" />

## Enjoying this library? Have suggestions?

Please consider giving a ⭐ on [**GitHub**](https://github.com/xulbux/python-lib-xulbux) or suggesting improvements in the [**Discussions**](https://github.com/xulbux/python-lib-xulbux/discussions).

<br>
<br>
<br>

---

✨ Always creating more cool stuff for you! ✨ —⠀[**XulbuX**](https://xulbux.com)
