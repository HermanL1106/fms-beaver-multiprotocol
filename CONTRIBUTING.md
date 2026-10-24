# Reproducing and extending the experiment

Start with README.md and docs/VALIDATION.md. This is a fixed-profile ground-test candidate, not generic FMS support.

For a compatibility report, provide module MCU/board type, radio/EdgeTX version, release hash, receiver/flight-controller markings, your channel-output mapping and propeller-off results. Do not post authentication tokens, USB serial numbers, private module Flash backups or unreviewed complete personal logs. State whether you tested a factory-new binding procedure or only reconnection to an already paired receiver.

When changing code:

1. Preserve upstream licensing and identify your modifications.
2. Reproduce the unmodified binary with the pinned board package before interpreting a difference.
3. Run the actual-source host tests. Add a failing regression for an interlock/encoding bug before fixing it.
4. Separate a new receiver/identity profile from the known working defaults. Changing a receiver number does not generate an independent RF identity.
5. Validate packet source, framing and CRC independently. A raw RSSI, matching sync word or passing checksum alone does not prove aircraft telemetry.
6. Record hardware power, direction/neutral, switch and lost-input behavior honestly. Host tests are not a substitute for propeller-off physical checks or verified flight safety.

Research priorities: independently captured receiver variants and identities; a real new-receiver bind sequence; measured RF behavior and usable range; safe, source-attributed return-link observations. Keep RF-enable and motor-enable semantics explicit. Do not remove the low-throttle interlock or present a transmit counter as a connected-aircraft sensor.

`fixture-provenance.json` describes the reviewed sample lines. `test_bench.py` extracts the actual upstream writer and actual callback; `test_diagnostic.py` extracts the actual receiver decoder. Tests generate host binaries only in temporary directories. After intentional reviewed source/fixture changes, regenerate checksums with `python3 scripts/make-manifest.py`; checksums are integrity bookkeeping, not a cryptographic signature or proof of correctness.

Any future full-power or flight claim needs new evidence and applicable compliance work. No such claim is part of RC1.
