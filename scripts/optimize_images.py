#!/usr/bin/env python3
"""Create compressed WebP copies for oversized PNG/JPEG source images.

Requires `cwebp` on PATH. This script does not delete originals.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUALITY = '78'
MIN_BYTES = 80 * 1024
EXTS = {'.png', '.jpg', '.jpeg'}


def main() -> int:
    cwebp = shutil.which('cwebp')
    if not cwebp:
        print('cwebp not found. Install webp tools first.', file=sys.stderr)
        return 1
    made = 0
    for src in (ROOT / 'assets').rglob('*'):
        if not src.is_file() or src.suffix.lower() not in EXTS:
            continue
        if src.stat().st_size < MIN_BYTES:
            continue
        out = src.with_suffix('.webp')
        subprocess.run([cwebp, '-q', QUALITY, str(src), '-o', str(out)], check=True)
        made += 1
        print(f'{src.relative_to(ROOT)} -> {out.relative_to(ROOT)}')
    print(f'webp_created_or_updated={made}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
