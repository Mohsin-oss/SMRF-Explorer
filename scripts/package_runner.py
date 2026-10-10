#!/usr/bin/env python3
"""Create the downloadable runner ZIP reproducibly using only the standard library."""
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / 'dist/assets/smrf-python-runner.zip'


def main():
    ARCHIVE.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ARCHIVE, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in ('smrf_runner.py', 'README.md'):
            entry = zipfile.ZipInfo(name, date_time=(2026, 10, 10, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, (ROOT / 'runner' / name).read_bytes())
    print('Packaged:', ARCHIVE.relative_to(ROOT))


if __name__ == '__main__':
    main()
