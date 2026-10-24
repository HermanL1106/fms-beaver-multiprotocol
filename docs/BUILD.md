# Rebuild and application-only update

## Pinned source and tools

- Upstream sketch base: v1.3.4.63, commit79b09468ac6d9e069b44becf46e67518072b2c8b.
- Arduino CLI and board package `multi4in1:STM32F1@1.3.1`.
- Board package dependency: ARM GCC8.3.1-1.4.
- FQBN: `multi4in1:STM32F1:multistm32f103cb:debug_option=native,usb_support=enabled`.
- Application origin:0x08002000 on the tested STM32duino bootloader. Do not assume this layout for other hardware.

The actual firmware build was checked on Apple Silicon macOS using the installed Intel toolchain via Rosetta. Host tests also run separately in GitHub Actions. Neither statement promises the board package works on every OS.

Install Arduino CLI using its official distribution. The board index is maintained by the upstream MULTI project:

```sh
arduino-cli core update-index --additional-urls https://raw.githubusercontent.com/pascallanger/DIY-Multiprotocol-TX-Module-Boards/master/package_multi_4in1_board_index.json
arduino-cli core install multi4in1:STM32F1@1.3.1 --additional-urls https://raw.githubusercontent.com/pascallanger/DIY-Multiprotocol-TX-Module-Boards/master/package_multi_4in1_board_index.json
```

From this repository root:

```sh
python3 scripts/verify.py
sh run-tests.sh
sh scripts/build.sh
```

Host tests require Python3 and clang++ with AddressSanitizer/UndefinedBehaviorSanitizer. The build script compiles only; it never enters DFU, opens serial devices or uploads anything.

Output: `build/rc1/Multiprotocol.ino.bin`. The exact supplied image is51076 bytes, SHA-256:

```text
027fd8cd35f0f3d9778fe8fe427fa97fbee40d250871144e599ecfd08d2d14ac
```

The compiler reports51052 bytes sketch flash and5576 bytes static RAM; the51076-byte binary file includes its actual linker output layout. Two independent working build directories and an extracted source archive produced the same binary in the tested environment. Publication-source rebuild is recorded in VALIDATION.md.

`-DFMS_RELEASE` is required. Without it, this source snapshot defaults to receive diagnostics, not FMS control. Do not use `FMS_BUILD_BENCH`, substitute a current upstream source tree, or change board/MCU settings and assume equivalence.

The pinned package emits pre-existing `ctags_target_for_gcc_minus_e.cpp` grep warnings during preprocessing; successful builds are not claimed to be warning-free.

## Flash only when hardware is known

The supplied image is for an **external STM32F103CB 4-in-1 module**, not the Pocket radio. Disconnect aircraft power, remove the propeller, turn the original F4 OFF, set RF/motor switches OFF and throttle low. Save a recoverable backup appropriate to your own module before its first modification. No original module backup or bootloader image is distributed here.

Use your module manufacturer's documented bootloader entry and the upstream MULTI flashing method for that exact hardware. This project deliberately does not provide a one-click script that resets/flashes the first connected USB device.

For the tested STM32duino layout only, `dfu-util -l` showed VID:PID1eaf:0003, application alternate2 at0x08002000. **Verify your own device serial, target address and alternate setting.** If they differ or are unknown, stop; do not guess wiring, select a broad DFU target or overwrite a bootloader.

Example after entering a verified compatible DFU bootloader (replace the placeholder with your own serial):

```sh
dfu-util -l
dfu-util -R -a 2 -d 1eaf:0003 -S YOUR_OWN_VERIFIED_SERIAL -D releases/v0.1.0-rc1/fms-beaver-0.1.0-rc1.bin
```

On the tested bootloader, runtime reset returned exit74 despite a completed download. Do not treat that exit code as success or failure by itself: inspect100% completion, device status and runtime re-enumeration, then select protocol125 and verify the RC1 banner/status and safe idle behavior. Flash readback was not performed in this project; bootloader overwrite is not part of the procedure.

Reapply all settings in SETUP.md, with aircraft power disconnected, before performing propeller-off checks. Firmware rollback also requires matching the radio model/protocol settings of the restored image.
