"""Regenerate public integrity manifests after intentional reviewed changes."""
from pathlib import Path
import hashlib

root = Path(__file__).resolve().parent.parent
paths = sorted((root / 'diagnostic-source/Multiprotocol').rglob('*'))
paths += [root / name for name in (
    'LICENSE', 'diagnostic-source/LICENSE', 'captures/serial-fixtures.log',
    'fixture-provenance.json', 'test_bench.py', 'test_diagnostic.py', 'run-tests.sh')]
lines = []
for path in paths:
    if path.is_file():
        lines.append(f'{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(root)}\n')
(root / 'SOURCE_SHA256SUMS').write_text(''.join(sorted(lines)))
binary = root / 'releases/v0.1.0-rc1/fms-beaver-0.1.0-rc1.bin'
(binary.parent / 'SHA256SUMS').write_text(f'{hashlib.sha256(binary.read_bytes()).hexdigest()}  {binary.name}\n')
print('Generated source/test and release-binary integrity manifests')
