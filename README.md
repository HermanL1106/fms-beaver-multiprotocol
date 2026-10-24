# FMS Beaver / F4 experimental MULTI control firmware

[繁體中文](README.zh-TW.md) · [Setup](docs/SETUP.md) · [Build](docs/BUILD.md) · [Protocol](docs/PROTOCOL.md) · [Validation](docs/VALIDATION.md)

Independently reverse-engineered control firmware for one FMS F4 / Beaver receiver combination, tested with a RadioMaster Pocket and an external STM32 4-in-1 MULTI module.

**Ground-tested release candidate only. Not official FMS firmware, not an upstream MULTI protocol, not universally compatible and not verified for flight.** Power remains the lowest predefined range-test chip setting. Range, radiated power and GPS-enabled lost-link/return-to-home behavior have not been verified. Do not fly on the strength of these results.

## Working on the tested aircraft

- Aileron, elevator, rudder and throttle; rudder polarity corrected in the protocol.
- Three mode commands and the momentary GPS-wait cancellation command.
- Separate RF and motor switches, low-throttle motor interlock, no automatic re-arm after a detected input interruption.
- A dedicated `FMSBeav` menu entry, rebuildable source, application binary and captured-fixture offline tests.

The owner reported normal ground operation with RC1, including after restoring it from a receive-only diagnostic build. This is an operator report, not independent flight certification.

## Critical: fixed shared identity, not generic binding

Only **one original F4 / Beaver pairing** has been validated. Its captured address and opaque identity bytes are fixed. There is no generic bind implementation or independently generated model identity. Another receiver may not respond at all.

**Matching firmware copies can transmit the same identity. Never operate matching copies, or this firmware and the original F4, simultaneously near a compatible powered aircraft.** Receiver number `5` is a profile gate, not a new RF identity.

## Pocket quick setup

Propeller removed, aircraft battery disconnected, original F4 OFF. This binary is for the **external module, not the Pocket radio**. Tested hardware is an STM32F103CBT6 4-in-1 with CC2500 and an existing STM32duino USB bootloader; other MCUs/bootloaders and internal Pocket RF hardware are not supported by these test results.

This minimal build enables only FMSBeav, not the module's usual collection of protocols. Obtain the correct vendor firmware/recovery method before replacing a general-purpose module image.

External RF: MULTI, channels1–16; Internal RF OFF. Select `FMSBeav` / private protocol `125`, subtype `0`, receiver number `5`, Option `42`. Leave Bind / Auto bind / Bind CH disabled. ID125 is not upstream-assigned and can conflict with other firmware. Option42 is an enable key, **not a fixed RF channel or fine tune**.

Configure AETR plus CH5 mode, CH7 momentary command, CH8 motor request and CH16 RF request. See [full output mapping and safe arming](docs/SETUP.md). Switch names describe the tested owner's model, not an automatically installed EdgeTX configuration. No unverified model import file is supplied.

**RF OFF is not motor cut:** it can invoke receiver lost-link behavior, potentially RTH with GPS. Use the separate motor switch. Finish by locking the motor, lowering throttle and disconnecting the aircraft battery before switching RF/radio off.

## Download, build and test

Use the `v0.1.0-rc1` **pre-release** or the binary under `releases/v0.1.0-rc1/`. SHA-256:

```text
027fd8cd35f0f3d9778fe8fe427fa97fbee40d250871144e599ecfd08d2d14ac
```

See [build and application-only update instructions](docs/BUILD.md). Do not guess module wiring or overwrite an unknown bootloader. Keep a recoverable backup for your own hardware.

```sh
python3 scripts/verify.py
sh run-tests.sh
sh scripts/build.sh
```

Verification and host tests need Python3 and clang++ with ASan/UBSan; building also needs Arduino CLI and the pinned board package. None of these commands flashes hardware. Host tests do not access USB or transmit RF.

## No fabricated telemetry

No aircraft RSSI, telemetry or confirmed aircraft-connected indicator is implemented. Module status/software transmission is not an aircraft acknowledgement. Limited receive-only comparisons did not establish return packets; they do not prove all FMS implementations are unidirectional. No fake RSSI/LQ is emitted.

Contributions are welcome for independent identities, reproducible binding, receiver variants, measured RF behavior and safely captured return-link evidence. Open an issue with hardware/build versions, output mapping and propeller-off observations. Do not upload account credentials, private firmware backups or unreviewed personal logs.

## Attribution and license

Based on [DIY-Multiprotocol-TX-Module](https://github.com/pascallanger/DIY-Multiprotocol-TX-Module), tag `v1.3.4.63`, commit `79b09468ac6d9e069b44becf46e67518072b2c8b`. This is a modified snapshot, not upstream Git history or an official upstream release. Existing notices are retained; see [NOTICE](NOTICE.md), [upstream README](docs/UPSTREAM_README.md) and [GPLv3](LICENSE). No affiliation with the hardware manufacturers is implied.
