# Provenance and modification notice

Firmware derives from DIY-Multiprotocol-TX-Module by Pascal Langer and contributors:

- https://github.com/pascallanger/DIY-Multiprotocol-TX-Module
- Base: v1.3.4.63, commit79b09468ac6d9e069b44becf46e67518072b2c8b.
- Original GPLv3-or-later source notices and the full license are retained.

This modified snapshot supplies the complete sketch for the application binary, not the upstream Git history. The external board package/toolchain is documented in docs/BUILD.md. See docs/UPSTREAM_README.md for the original introduction.

Modifications add a captured FMS encoder/hopping profile, motor and RF interlocks, a private protocol entry, receive diagnostics, bounded diagnostic formatting and interrupt-safe diagnostic counters. Captured-data regression tests and documentation accompany the source.

No manufacturer affiliation or endorsement is implied. Fixed RF identity is an experimental compatibility limitation, not generic binding. Only a reviewed subset of captured packet fixtures is published; private backups, computer paths, USB serial identifiers and full session logs are excluded.
