# FMSBeav v0.1.0-rc1 — experimental ground-tested profile

First public release candidate for one captured FMS F4 / Beaver pairing, used with Pocket and an external STM32F103CB 4-in-1 module.

- Independent FMSBeav protocol125; subtype0, profile5, Option42.
- AETR control, three modes and momentary GPS-wait command.
- Separate RF and motor requests with startup, low-throttle and no-auto-rearm interlocks.
- Complete matching source, pinned build instructions, reviewed capture fixtures and actual-source sanitizer tests.
- English and Traditional Chinese setup, compatibility and safety documentation.

**Pre-release, not flight-ready.** Fixed shared identity, no generic bind or guaranteed compatibility with another receiver. Never operate matching copies/original F4 concurrently near a compatible powered aircraft. Range-test chip power remains in use; range/EIRP and GPS-enabled lost-link/RTH are unverified. No aircraft RSSI or authenticated connected indicator is supplied.

The application binary is51076 bytes; SHA-256:

```text
027fd8cd35f0f3d9778fe8fe427fa97fbee40d250871144e599ecfd08d2d14ac
```

It is for a compatible external module, **not the Pocket itself**. Read README and docs/BUILD.md before updating. Propeller removed, aircraft battery disconnected, original F4 OFF; verify your own bootloader/layout and recovery backup. No bootloader or private stock Flash backup is included.

Supplied assets include the application and checksum; GitHub's tagged source archives contain the complete sketch and offline tests. GPL notices and upstream attribution are preserved.
