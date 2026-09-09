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



def check_llms_txt() -> None:
    p = ROOT / 'llms.txt'
    if not p.exists():
        add_warn('llms.txt is missing. Add it for production AI-discovery readiness.')
        return
    text = p.read_text(errors='ignore').strip()
    if not re.search(r'^#\s+\S+', text, re.M):
        add_fail('llms.txt needs a Markdown H1, e.g. # Restaurant Name.')
    if not re.search(r'^>\s+\S+', text, re.M):
        add_fail('llms.txt needs a blockquote summary line starting with >.')
    if not re.search(r'^##\s+\S+', text, re.M):
        add_fail('llms.txt needs Markdown ## sections.')
    md_links = re.findall(r'\[[^\]]+\]\(https?://[^)]+\)', text)
    bare_urls = re.findall(r'(?<!\()https?://[^\s)]+', text)
    if not md_links:
        add_fail('llms.txt has no Markdown links. Bare URLs do not satisfy the audit; use - [Label](https://example.com/).')
    if bare_urls and len(bare_urls) > len(md_links):
        add_warn('llms.txt appears to contain bare URLs outside Markdown link syntax.')
    print(f'llms_markdown_links={len(md_links)}')

SCRIPT_STYLE_RE = re.compile(r'<(script|style)\b[^>]*>.*?</\1>', re.S | re.I)
# House style bans em/en dashes and emoji in shipped copy. Emoji ranges kept
# conservative (pictographs + symbols + flags + variation selector) so ordinary
# punctuation and math symbols do not false-positive.
DASH_RE = re.compile('[–—]')
EMOJI_RE = re.compile(
    '[\U0001F300-\U0001FAFF\U0001F1E6-\U0001F1FF'
    '\U00002600-\U000027BF\U00002B00-\U00002BFF️]')


def check_typography(files: list[Path]) -> None:
    """No em/en dashes and no emoji in visible content (scripts/styles stripped)."""
    for p in files:
        visible = SCRIPT_STYLE_RE.sub('', p.read_text(errors='ignore'))
        dashes = DASH_RE.findall(visible)
        if dashes:
            add_fail(f'{rel(p)} has {len(dashes)} em/en dash(es) in visible copy; house style forbids em/en dashes (AI tell).')
        emoji = EMOJI_RE.findall(visible)
        if emoji:
            add_fail(f'{rel(p)} contains emoji {sorted(set(emoji))!r}; use inline SVG, no emoji on sites.')


def check_tel_links(files: list[Path]) -> None:
    """A US tel: link must be +1 plus exactly 10 digits (catches doubled country code)."""
    bad: dict[str, int] = {}
    for p in files:
        for m in re.finditer(r'tel:\+1(\d+)', p.read_text(errors='ignore')):
            if len(m.group(1)) != 10:
                bad['+1' + m.group(1)] = bad.get('+1' + m.group(1), 0) + 1
    for token, n in bad.items():
        add_fail(f'Malformed US tel link {token} on {n} page(s); a US tel: is +1 plus exactly 10 digits.')


def check_links_page() -> None:
    """Every build ships a Linktree-style /links/ page (Roman Group pattern)."""
    if not (ROOT / 'links' / 'index.html').exists() and not (ROOT / 'links.html').exists():
        add_warn('No /links/ page found; every build should ship a Linktree-style /links/ page (see GOTCHAS).')


def check_canonical_host(files: list[Path]) -> None:
    """Canonical, og:url, and sitemap must all use one host; flag apex-vs-www to verify against prod."""
    hosts: set[str] = set()
    for p in files:
        text = p.read_text(errors='ignore')
        for m in re.finditer(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']https?://([^/"\']+)', text):
            hosts.add(m.group(1))
        for m in re.finditer(r'og:url["\'][^>]+content=["\']https?://([^/"\']+)', text):
            hosts.add(m.group(1))
    sm = ROOT / 'sitemap.xml'
    if sm.exists():
        for m in re.finditer(r'<loc>\s*https?://([^/<]+)', sm.read_text(errors='ignore')):
            hosts.add(m.group(1))
    if len(hosts) > 1:
        add_fail(f'Mixed canonical/og/sitemap hosts {sorted(hosts)!r}; use one host consistently or launch URLs will 404/redirect for crawlers.')
    elif hosts:
        host = next(iter(hosts))
        print(f'canonical_host={host}')
        tag = ' (apex, no www)' if not host.startswith('www.') else ''
        add_warn(f'Canonical host is {host}{tag}; verify production serves this host and does NOT 301 to the other. Check: curl -sI https://{host}/ | grep -i ^location')


def check_index_state(files: list[Path]) -> None:
    """Surface noindex/Disallow so a human confirms it matches preview-vs-production intent."""
    noindex = sum(1 for p in files
                  if re.search(r'<meta[^>]+name=["\']robots["\'][^>]+noindex', p.read_text(errors='ignore'), re.I))
    print(f'noindex_pages={noindex}')
    if noindex:
        add_warn(f'{noindex}/{len(files)} pages carry meta robots noindex. Confirm intent (preview=noindex OK; production launch must be indexable).')
    robots = ROOT / 'robots.txt'
    if robots.exists() and re.search(r'(?im)^\s*Disallow:\s*/\s*$', robots.read_text(errors='ignore')):
        add_warn('robots.txt Disallows all crawling; confirm this is an intentional preview state, not a production launch.')


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
    check_typography(files)
    check_tel_links(files)
    check_links_page()
    check_canonical_host(files)
    check_index_state(files)
    check_menu_generator()
    check_llms_txt()

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
