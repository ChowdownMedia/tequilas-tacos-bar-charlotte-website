# Chowdown Site Build Playbook

This is the required operating checklist for restaurant sites. Agents must read this before beginning build work.

## 1. Intake

Confirm the project has the needed client inputs:

- Brand kit and logo files.
- Artistic direction or Claude Design handoff.
- Photo folders and any priority hero/menu/gallery images.
- Menu PDFs, menu data, pricing, and ordering rules.
- Restaurant name, address, phone, hours, Google Place ID, map URL, and social links.
- Order online URL.
- GHL client/location ID and ChowdownOS client ID.
- Boomerang/VIP endpoint or API key when VIP is included.
- Cloudflare Pages project, GitHub repo, preview URL, and production URL intent.
- Preview `noindex` vs production index status.

## 2. Build Structure

- Identify source templates, generators, and generated pages before editing.
- Keep shared nav/footer in source templates when possible.
- Use `build_menu.py` or equivalent scripts for menu pages and search indexes.
- Add scripts for repeated tasks instead of relying on manual edits.
- Keep generated pages in sync after source/template changes.

## 3. Brand And UX

- Apply the brand kit consistently: logo, palette, type scale, spacing, photography, and button style.
- Build the usable site first: home, menus, gallery, events, VIP, contact, footer, and order paths.
- Desktop must use available space well. Mobile must be readable and tappable.
- Provide direct menu switching when multiple menus exist, not only a hamburger path.
- Category/detail pages need an obvious back path to the menu landing.
- Header, hamburger, footer, and CTA links must not point to dead sections.

## 4. Forms And Integrations

- `window.SITE_CONFIG` or equivalent config must include correct form and VIP endpoints.
- Contact/newsletter/event forms submit to ChowdownOS/GHL as required.
- VIP signup uses the correct Boomerang/VIP configuration.
- Hidden honeypot fields and success/error states must exist.
- Test submissions when credentials are available; otherwise mark credentials as pending.

## 5. Images And Fonts

- Self-host all fonts with `font-display: swap`.
- Avoid remote font/CDN dependencies in production pages.
- Convert logos and large UI imagery to WebP or AVIF where supported.
- Use responsive images with accurate `srcset`, `sizes`, width, and height.
- Do not serve large 800/1600 images into tiny nav/footer slots.
- Hero/LCP images should be discoverable in HTML and use `fetchpriority="high"` when appropriate.
- Lazy-load below-the-fold images and category tiles unless they are true LCP candidates.
- Re-run image checks after adding or replacing photography.

## 6. Structured Data

- JSON-LD must parse on every public HTML page.
- Restaurant schema should include name, URL, phone, address, cuisine, price range, hours, map/place ID, geo when available, image, menu URL, and order action when available.
- Menu schema should include Menu/MenuSection/MenuItem structure with prices in USD when available.
- BreadcrumbList names must be human-readable labels, not raw paths.
- Footer visible business data must agree with schema data.

## 7. Performance And Lighthouse

Target Lighthouse/PageSpeed mobile:

- Performance: 100 or documented accepted miss.
- Accessibility: 100.
- Best Practices: 100.
- SEO: 100 in production; preview may be lower only because of intentional `noindex`.

Required local iteration:

- Use `lighthouse@latest`, not stale versions.
- If `npx` is broken, install Lighthouse under `/tmp/lh` and run the binary directly.
- Match mobile form factor for PSI comparison.
- Read failing audits from JSON and fix the specific resources/selectors PSI names.

## 8. Footer/Nav QA

- Footer contains no dead links.
- Footer Explore links match active pages.
- Phone/address/hours/order URL are correct.
- Header nav and hamburger contain the same valid destinations.
- No internal nav links should use `/index.html` on Cloudflare Pages when a clean slash URL exists.

## 9. Deployment

- Commit after validation.
- Push to GitHub to trigger Cloudflare Pages unless the project explicitly uses Wrangler direct deploy.
- After deploy, test the Cloudflare preview URL with cache-busting.
- Run PSI against the deployed preview for final client-facing score.

## 10. Final Handoff

Report:

- Commit hash.
- Preview URL.
- Lighthouse/PSI scores.
- Structured-data validation result.
- Known exceptions or pending credentials.
- Any creative shot list still needed.
