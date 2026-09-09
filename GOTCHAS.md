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
