# Build Agent Instructions

Read this file before starting any site build, redesign, menu rebuild, deploy, or optimization pass.

## Required Playbook

1. Read `BUILD_PLAYBOOK.md` before making build decisions.
2. Read `CLIENT_HANDOFF.md` and `CLAUDE_DESIGN_HANDOFF.md` when present or requested.
3. Use generators such as `build_menu.py` for generated pages. Do not hand-edit generated menu pages when a source generator exists.
4. Run `python3 scripts/preflight.py` before calling the work done.
5. For deploy readiness, run Lighthouse/PageSpeed using the commands in `scripts/lighthouse_local.sh` or PSI against the Cloudflare preview.
6. Treat SEO score exceptions as valid only when the preview is intentionally `noindex`.
7. Commit only after preflight passes or after documenting a deliberate exception.

## Non-Negotiables

- Self-host fonts. Avoid remote font/CDN dependencies unless explicitly approved.
- Optimize images before deployment. Use responsive `srcset`, correct `sizes`, modern formats, and small logo assets.
- Keep nav and footer consistent across all static and generated pages.
- Remove dead nav/footer links.
- Keep footer business data aligned with JSON-LD: name, phone, address, hours, maps/place ID, and order URL.
- Validate JSON-LD. Menu structured data must parse and represent current menu sections/items.
- Wire forms to ChowdownOS/GHL with the correct client IDs and endpoints.
- VIP/Boomerang flows must be configured and tested when included.
- Check desktop and mobile UX, including tap targets, menu switching, category back paths, readable side rails, and PDF downloads.

## Done Done Gate

A build is not done until:

- Local build/generator completes.
- `scripts/preflight.py` passes or exceptions are documented.
- Lighthouse/PSI mobile performance, accessibility, and best-practices are 100 or any misses are explicitly accepted.
- SEO state matches preview/production intent.
- Forms and VIP submit paths are tested or clearly marked as pending credentials.
- Cloudflare preview is checked after deploy.
