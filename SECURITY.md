# Security Notes

## Dependency advisory exception

The security workflow intentionally ignores these ChromaDB advisories:

- PYSEC-2026-311
- PYSEC-2026-3813
- PYSEC-2026-3814
- PYSEC-2026-3815

These advisories currently affect the latest ChromaDB release resolved through the CrewAI dependency tree, and upstream does not currently publish a fixed release for the affected range.

The project does not expose a standalone ChromaDB server endpoint. Memory is used as an application dependency, which reduces the network attack surface but does not make the advisories irrelevant.

## Review policy

- Keep the exceptions narrowly scoped to the known advisory IDs.
- Do not use a blanket pip-audit ignore.
- Re-run the audit on every push, pull request, and weekly schedule.
- Remove the exceptions immediately after a patched upstream release is available.
- Treat any new advisory as a normal security failure.

For API security controls, see security.py and the security tests under tests/.