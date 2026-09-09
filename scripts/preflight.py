#!/usr/bin/env python3
"""Chowdown static-site preflight checks.

This script catches recurring launch gotchas before deploy. It is intentionally
conservative: warnings should be reviewed, failures should be fixed or documented.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_SKIP = {'.git', 'node_modules'}
IMAGE_EXTS = {'.png', '.jpg', '.jpeg', '.webp', '.avif'}
MAX_LOGO_BYTES = 40 * 1024
MAX_PNG_BYTES = 120 * 1024
MAX_JPG_BYTES = 220 * 1024

failures: list[str] = []
warnings: list[str] = []


def public_html_files() -> list[Path]:
    files: list[Path] = []
    for p in ROOT.rglob('*.html'):
        rel = p.relative_to(ROOT)
        if rel.parts and rel.parts[0] in PUBLIC_SKIP:
            continue
        if rel.parts and rel.parts[0] == '.chowdown':
            continue
        files.append(p)
    return sorted(files)


def rel(p: Path) -> str:
    return str(p.relative_to(ROOT))


def add_fail(msg: str) -> None:
    failures.append(msg)


def add_warn(msg: str) -> None:
    warnings.append(msg)


def check_json_ld(files: list[Path]) -> None:
    count = 0
    for p in files:
        text = p.read_text(errors='ignore')
        for m in re.finditer(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', text, re.S | re.I):
            count += 1
            try:
                data = json.loads(m.group(1))
            except Exception as exc:
                add_fail(f'{rel(p)} has invalid JSON-LD: {exc}')
                continue
            nodes = data.get('@graph', [data]) if isinstance(data, dict) else []
            for node in nodes:
                if isinstance(node, dict) and node.get('@type') == 'BreadcrumbList':
                    for item in node.get('itemListElement', []):
                        name = item.get('name') if isinstance(item, dict) else None
                        if isinstance(name, str) and name.startswith('/'):
                            add_fail(f'{rel(p)} breadcrumb name is a raw path: {name}')
    if count == 0:
        add_fail('No JSON-LD scripts found on public HTML pages.')
    else:
        print(f'json_ld_scripts={count}')


def check_nav_footer(files: list[Path]) -> None:
    for p in files:
        text = p.read_text(errors='ignore')
        if re.search(r'href=["\'][^"\']*/index\.html["\']', text):
            add_warn(f'{rel(p)} contains an internal /index.html link; prefer clean slash URLs on Cloudflare Pages.')
        footer_i = text.rfind('<footer')
        footer = text[footer_i:] if footer_i >= 0 else ''
        if not footer:
            add_warn(f'{rel(p)} has no footer element.')
        if 'Signatures' in footer:
            add_fail(f'{rel(p)} footer links to Signatures; remove unless the destination is a real page.')
        for dead in ('href="#"', "href='#'"):
            if dead in text:
                add_warn(f'{rel(p)} contains placeholder link {dead}.')


def check_assets(files: list[Path]) -> None:
    for p in (ROOT / 'assets').rglob('*') if (ROOT / 'assets').exists() else []:
        if not p.is_file() or p.suffix.lower() not in IMAGE_EXTS:
            continue
        size = p.stat().st_size
        name = p.name.lower()
        if 'logo' in name and size > MAX_LOGO_BYTES:
            add_warn(f'{rel(p)} is {size // 1024}KB; nav/footer logos should usually be under 40KB.')
        if p.suffix.lower() == '.png' and size > MAX_PNG_BYTES:
            add_warn(f'{rel(p)} is a {size // 1024}KB PNG; consider WebP/AVIF or smaller dimensions.')
        if p.suffix.lower() in {'.jpg', '.jpeg'} and size > MAX_JPG_BYTES:
            add_warn(f'{rel(p)} is a {size // 1024}KB JPEG; consider WebP/AVIF and responsive sizes.')

    html = '\n'.join(p.read_text(errors='ignore') for p in files)
    if 'fonts.googleapis.com' in html or 'fonts.gstatic.com' in html:
        add_fail('Remote Google Fonts found in public HTML; self-host fonts instead.')
    if '@font-face' in ''.join(p.read_text(errors='ignore') for p in (ROOT / 'assets' / 'css').glob('*.css')):
        css = ''.join(p.read_text(errors='ignore') for p in (ROOT / 'assets' / 'css').glob('*.css'))
        if 'font-display:swap' not in css.replace(' ', ''):
            add_warn('Self-hosted fonts found, but font-display: swap was not detected.')


def check_forms(files: list[Path]) -> None:
    text = '\n'.join(p.read_text(errors='ignore') for p in files)
    if 'window.SITE_CONFIG' not in text:
        add_warn('No window.SITE_CONFIG found; confirm forms/VIP are wired another way.')
    if '<form' in text and ('chowdownos' not in text.lower() and 'SITE_CONFIG' not in text):
        add_warn('Forms exist but no ChowdownOS/GHL config was detected.')
    if 'vip' in text.lower() and 'client' not in text.lower():
        add_warn('VIP copy/page detected, but no client config string was obvious.')


def check_menu_generator() -> None:
    if (ROOT / 'build_menu.py').exists():
        generated = ROOT / 'assets' / 'js' / 'menu-index.js'
        if not generated.exists():
            add_warn('build_menu.py exists but assets/js/menu-index.js is missing; run the generator.')
    else:
        add_warn('No build_menu.py found. If this site has generated menus, add or document the generator.')


def main() -> int:
    os.chdir(ROOT)
    files = public_html_files()
    if not files:
        add_fail('No public HTML files found.')
    check_json_ld(files)
    check_nav_footer(files)
    check_assets(files)
    check_forms(files)
    check_menu_generator()

    print(f'public_html_files={len(files)}')
    print(f'warnings={len(warnings)}')
    for msg in warnings:
        print(f'WARN: {msg}')
    print(f'failures={len(failures)}')
    for msg in failures:
        print(f'FAIL: {msg}')
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
