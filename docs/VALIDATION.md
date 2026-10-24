# Evidence and limits for v0.1.0-rc1

Date:2026-10-24, Asia/Taipei. This is one owner's ground-tested receiver/profile, not universal compatibility or flight qualification.

## Physical evidence

The owner reported normal aileron/elevator/rudder, throttle and motor lock operation; three mode positions were identified; momentary GPS-wait cancellation was observed. RC1 was flashed application-only and its dedicated protocol125 banner/status was observed. After a receive-only investigation, the same RC1 binary was restored and the owner again reported normal surfaces and throttle.

Software logs confirm model inputs, transmitted payload values and arming state, **not directly sensed servo/motor movement**. Physical acceptance is the owner's report. No flash readback was performed. Tests do not establish every power-cycle/failure combination.

## Offline tests

- Actual control callback compiled on the host with ASan/UBSan:10 virtual minutes across clock wrap, RF cutoff, independent motor gate, low-throttle enable, failed-enable retry and input-gap no-auto-resume.
- Actual release entry: profile rejection and no arming by correcting invalid menu values while RF request is already high.
- Actual upstream XN297 writer reproduces128 captured address/payload/CRC vectors exactly.
-137 captured receive vectors, corrupted CRC rejection and200000 decoder fuzz inputs.
- Input-only diagnostic callback never transmits across256×2048 Option/CH16 combinations.
- Reviewed capture fixture lines include provenance filenames/line numbers and hashes. They are not a full personal session log. Multiple log representations are not independent RF packet counts.

Python tests inspect/compile actual supplied firmware source, not a separate hand-written replacement. Hardware functions are host stubs, so a green host test does not prove SPI timing, PA behavior or airborne reception. No USB/device access occurs in these tests.

The RC1 binary was reproduced from independent build directories and an extracted source archive using the pinned toolchain. Before public upload, the exported source/tests are also rebuilt locally and compared against the supplied SHA-256; GitHub Actions reruns offline source/fixture checks and host regression tests.

## Unknown / not passed

- Usable range, measured EIRP and regional radio conformity.
- GPS-enabled lost-link, airborne RTH and actual flight behavior.
- Generic binding, independent model identity or other receiver variants.
- Guaranteed operation on other module/MCU/bootloader/OS combinations.
- Aircraft RSSI, authenticated aircraft-connected status or receiver telemetry.

No-GPS motor stop on signal loss was reported on an earlier prototype; this is not a GPS RTH test. Receiver firmware may implement its own behavior when RF is lost.

Limited controlled receive-only experiments on one channel with7/40-byte windows did not identify aircraft-attributable normal/enhanced return packets. One mistuned interval was excluded rather than relabeled. These negative observations do not rule out other addresses, PHYs, frequencies or timing. No synthetic RSSI/LQ/connected sensor was added. Research-only observer firmware is intentionally not presented as the control release.
