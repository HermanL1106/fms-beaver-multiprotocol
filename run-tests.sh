#!/bin/sh
# Offline host tests only: no serial, USB, flashing or RF operations.
set -eu
task_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$task_root"
python3 test_bench.py --continuous --release
python3 test_bench.py --motor
python3 test_bench.py --monitor
python3 test_diagnostic.py
