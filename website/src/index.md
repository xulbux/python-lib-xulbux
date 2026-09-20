---
layout: home

hero:
  name: 'XulbuX'
  text: 'Python Library'
  tagline: 'A modern, high-performance Python library to simplify common tasks.'
  image:
    src: /logo.svg
    alt: XulbuX Logo
  actions:
    - theme: brand
      text: Get Started
      link: /docs/guide/get-started
    - theme: alt
      text: View on GitHub
      link: https://github.com/xulbux/python-lib-xulbux

features:
  - icon: '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15.914 4a1.5 1.5 0 0 0-2.474-1.561l-9 9A1.5 1.5 0 0 0 5.5 14h4.002a.5.5 0 0 1 .471.666L8.086 20a1.5 1.5 0 0 0 2.475 1.56l9-9A1.5 1.5 0 0 0 18.5 10h-3.997a.5.5 0 0 1-.472-.667z"/></svg>'
    title: Strongly Typed & C-Compiled
    details: Fully compiled to C via MyPyC with strict static typing for maximum execution speed.
  - icon: '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="15" cy="9" r="7"/><circle cx="9" cy="15" r="7"/></svg>'
    title: Color Engineering
    details: Manipulate, blend, and convert across RGBA, HSLA, and hex spaces with rich formatting and interpolation.
  - icon: '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m7 11 2-2-2-2"/><path d="M11 13h4"/><rect width="18" height="18" x="3" y="3" rx="2" ry="2"/></svg>'
    title: Terminal & Console UI
    details: Expressive ANSI styling via operator syntax, styled loggers, interactive prompts, and progress bars.
  - icon: '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13c0 1.1.9 2 2 2Z"/><circle cx="12" cy="13" r="1"/></svg>'
    title: System & File Automation
    details: Fuzzy path resolution, safe JSON and directory handling, and cross-platform OS helpers.
  - icon: '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 12h.01"/><path d="M16 12h.01"/><path d="m17 7 5 5-5 5"/><path d="m7 7-5 5 5 5"/><path d="M8 12h.01"/></svg>'
    title: Modern Data & Text Tools
    details: Path-based key access, data cleansing, syntax-highlighted rendering, and dynamic regex builders.
  - icon: '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m17 11-5-5-5 5"/><path d="m17 18-5-5-5 5"/></svg>'
    title: Zero Bloat & Lazy Loading
    details: Engineered for instantaneous startup times with PEP 562 modular lazy loading and minimal dependencies.
---

<br>
<br>

## Quick Installation

```bash
pip install xulbux
```

<br>

## Expressive Code at a Glance

```python
import xulbux as xx
from xulbux import S, hexa

# Prompt the user with styled input:
input_hexa_str = xx.console.input(
    (S.BOLD("Enter a hex color"), S.DIM(" > ")),
    placeholder="#FF3D5D",
)

# Initialize the input string as a `hexa()` object:
hexa_color = hexa(input_hexa_str)

# Nicely display the color in different formats:
xx.console.box(
    (S.BOLD | S.BG.hex(hexa_color).with_text_fg())("          Preview          "),
    "{hr}",
    (S.BOLD("HEXA: "), S.ITALIC(str(hexa_color))),
    (S.BOLD("RGBA: "), S.ITALIC(str(hexa_color.as_rgba()))),
    (S.BOLD("HSLA: "), S.ITALIC(str(hexa_color.as_hsla()))),
    border_style=S.DIM,
    end="\n\n",
)
```

<TerminalOutput>
<span class="b">Enter a hex color</span><span class="dim"> > </span>a8f

<span class="dim">╭─────────────────────────────╮</span>
<span class="dim">│</span> <span class="#000 bg-#A8F">          Preview          </span> <span class="dim">│</span>
<span class="dim">├─────────────────────────────┤</span>
<span class="dim">│</span> <span class="b">HEXA: </span><span class="i">#AA88FF</span>               <span class="dim">│</span>
<span class="dim">│</span> <span class="b">RGBA: </span><span class="i">rgba(170, 136, 255)</span>   <span class="dim">│</span>
<span class="dim">│</span> <span class="b">HSLA: </span><span class="i">hsla(257°, 100%, 77%)</span> <span class="dim">│</span>
<span class="dim">╰─────────────────────────────╯</span>
</TerminalOutput>

<br>

<div align="center" style="margin-top: 2.5rem; margin-bottom: 2.5rem;">
  <a href="/python-lib-xulbux/docs/guide/get-started" style="font-weight: 600; text-decoration: none; display: inline-flex; align-items: center; justify-content: center; gap: 0.35rem;">
    Explore the Getting Started Guide
    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"/></svg>
  </a>
</div>
