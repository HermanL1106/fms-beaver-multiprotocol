"""Verify published source/fixtures and the known RC1 binary; no device access."""
from pathlib import Path
import hashlib
import json

root = Path(__file__).resolve().parent.parent
count = 0
for manifest in (root / 'SOURCE_SHA256SUMS', root / 'releases/v0.1.0-rc1/SHA256SUMS'):
    for line in manifest.read_text().splitlines():
        expected, name = line.split('  ', 1)
        base = root if manifest.name == 'SOURCE_SHA256SUMS' else manifest.parent
        path = (base / name).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise SystemExit(f'Invalid or missing manifest path: {name}')
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            raise SystemExit(f'Checksum mismatch: {name}')
        count += 1
binary = root / 'releases/v0.1.0-rc1/fms-beaver-0.1.0-rc1.bin'
assert len(binary.read_bytes()) == 51076
assert hashlib.sha256(binary.read_bytes()).hexdigest() == '027fd8cd35f0f3d9778fe8fe427fa97fbee40d250871144e599ecfd08d2d14ac'
fixture = root / 'captures/serial-fixtures.log'
provenance = json.loads((root / 'fixture-provenance.json').read_text())
assert hashlib.sha256(fixture.read_bytes()).hexdigest() == provenance['fixture_sha256']
assert provenance['counts'] == {'wire': 128, 'decoder': 137}
print(f'PASS: {count} source/test/binary checksums and captured-fixture provenance')
