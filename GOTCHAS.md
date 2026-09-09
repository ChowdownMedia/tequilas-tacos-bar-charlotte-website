# Build Gotchas

This is the living list of traps that have already cost time. Add to it whenever a build or audit catches something that should become automatic next time.

## `llms.txt` Must Be Markdown Links

Bare URLs do not count as links for audits that parse `llms.txt` as Markdown. A human-readable file like this can still fail:

```txt
Home: https://www.example.com/
Menu: https://www.example.com/menu/
```

Use real Markdown link syntax:

```md
# Restaurant Name

> Short summary of the restaurant and site.

## Menus

- [Food menu](https://www.example.com/menu/): 163 items
- [Drinks menu](https://www.example.com/drinks/): Cocktails, beer, wine, and tequila
```

Required pattern:

- One `#` H1.
- One `>` blockquote summary.
- `##` sections.
- Bulleted Markdown links with optional `: description` text.

## Verify The Same URL The Audit Uses

Do not rely only on cache-busted verification. If the audit requests plain `/llms.txt`, verify plain `/llms.txt` too.

Useful deployment check:

```bash
curl -s https://example.com/llms.txt
curl -s "https://example.com/llms.txt?cb=$RANDOM"
```

If the cache-busted copy is fixed but plain `/llms.txt` is stale, wait for Cloudflare edge cache before changing working code.

## Fonts Must Be Self-Hosted

Remote font providers can hurt Lighthouse and introduce render-blocking or privacy issues. Ship local font files with `@font-face` and `font-display: swap`.

## Logos Can Quietly Kill Image Delivery

Nav and footer logos must be small, modern assets. A visually tiny PNG can still be 100KB+ and show up in PageSpeed image-delivery savings.

## Responsive Images Need Honest `sizes`

If cards display at 380px wide but load 800px images, PageSpeed will call it out. Keep `srcset` and `sizes` aligned with real rendered dimensions.

## Generated Pages Must Come From Generators

If a project has `build_menu.py` or another generator, update source data/templates and regenerate. Hand-editing generated pages causes drift across nav, footer, JSON-LD, and menus.

## Preview SEO Exceptions Must Be Intentional

Low SEO from `noindex` is fine on preview builds only when documented. Production builds need the index/crawl state checked before launch.

## `tel:` Links With a Doubled Country Code

The harvested phone number produced `tel:+119802265008` (extra leading 1) across all 58 pages — taps dialed a wrong number. Grep every build for `tel:+1` followed by an 11-digit remainder:

```sh
grep -rEo 'tel:\+1[0-9]{11,}' --include='*.html' .
```

A US `tel:` should be `+1` + exactly 10 digits. Fixed site-wide 2026-09-10.

## Apex vs WWW: Canonical Host Must Match The Serving Host

Solved fleet-wide once, cost real time. If the site serves on `www` and the apex 301-forwards to it (the standard), then every `canonical`, `og:url`, JSON-LD `url`/`@id`, sitemap `<loc>`, and internal absolute link must use `www`. Apex tags that point at a host which immediately redirects confuse crawlers about which URL to index. The Roman fleet shipped 1122 apex tags that broke after the apex forward.

Pick one serving host and use it consistently everywhere. `scripts/preflight.py` now fails when canonical/og/sitemap hosts disagree and warns to confirm the redirect direction against production:

```sh
curl -sI https://<apex>/ | grep -i ^location   # expect 301 to https://www/
curl -sI https://www.<domain>/                 # expect 200
```

DNS/GoDaddy side of this is in `BUILD_PLAYBOOK.md` section 12. Never zone-IMPORT a migration (clobbers email); EXPORT to back up, edit inline, leave MX/SPF/DKIM/DMARC alone.

## Every Build Ships a `/links/` Page

Linktree-style page following the Roman Group pattern (`el-jinete/athens/links/` is the reference): logo, name, beads divider, then rows — VIP (gold hi), Order, each menu, Review (Google place id), Gallery, Directions, Call. Self-contained inline styles, brand tokens, self-hosted fonts. Tequilas was missing one until 2026-09-10.
