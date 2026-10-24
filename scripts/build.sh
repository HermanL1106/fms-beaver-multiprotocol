#!/bin/sh
# Compile only: no upload, serial, DFU or device access.
set -eu
task_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$task_root"
arduino-cli core list | awk '$1=="multi4in1:STM32F1" && $2=="1.3.1" {found=1} END {exit !found}'
arduino-cli compile \
  -b multi4in1:STM32F1:multistm32f103cb:debug_option=native,usb_support=enabled \
  --build-property compiler.cpp.extra_flags=-DFMS_RELEASE \
  --build-path "$task_root/build/rc1" "$task_root/diagnostic-source/Multiprotocol"
python3 -c 'import hashlib,pathlib; p=pathlib.Path("build/rc1/Multiprotocol.ino.bin"); print(hashlib.sha256(p.read_bytes()).hexdigest(),p)'
