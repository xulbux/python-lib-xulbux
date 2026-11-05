# Security Policy

## <a href="#reporting-a-vulnerability"><img src="https://svg.xul.is/icon/shield-alert?size=32&stroke=2" align="left" /></a>Reporting a Vulnerability

Please **do not open public issues** for security vulnerabilities in [**`xulbux`**](https://xulbux.github.io/python-lib-xulbux). Report them privately via:

-   [**GitHub Private Vulnerability Reporting**](https://github.com/xulbux/python-lib-xulbux/security/advisories/new) (*preferred*)
-   **Email:** [hi@xul.is](mailto:hi@xul.is)

Include affected versions, Python/OS environment details, and a minimal reproduction script, and allow reasonable time for a fix before disclosure (paid bug bounties aren't offered). Security fixes target the latest `2.x` release on Python `>= 3.12`.

<br>

## <a href="#scope"><img src="https://svg.xul.is/icon/target?size=32&stroke=2" align="left" /></a>Scope

-   **In Scope:** Unintended command or argument injection in `system` or `cli` utilities, path traversal or unsafe file operations in `fs` / `data`, catastrophic regex backtracking (ReDoS) in `regex` or color/string parsers, memory or C-extension safety bugs in MyPyC-compiled modules, and XSS in the documentation build pipeline (`website/`).
-   **Out of Scope:** Intentional command or file execution when callers pass untrusted input directly to low-level system APIs, vulnerabilities in upstream dependencies (`prompt_toolkit`, `regex`, VitePress – report those directly to their maintainers), and unsupported Python (`< 3.12`) or `1.x` versions.

