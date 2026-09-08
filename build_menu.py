#!/usr/bin/env python3
"""Tequilas Tacos & Bar — menu generator (Mi Jalapeno card treatment, Tequilas skin).

Reads .chowdown/content.json (menu source of truth) + .chowdown/photo_catalog.json
(real Drive shoot, every photo visually verified) and emits:
  /menu/index.html            — card landing grouped by course, full Menu schema
  /menu/<slug>/index.html     — per-category page, section schema
Chrome (head/nav/footer) comes from .chowdown/chrome/{top,tail}.html captured from
the live menu page, with paths made absolute so it works at any depth.
Run:  python3 build_menu.py
"""
import json, os, re, html

ROOT = os.path.dirname(os.path.abspath(__file__))
DOMAIN = "https://tequilastacosbar.com"
IMG = "/assets/images/menu"
CSS_VER = "mc1"

e = html.escape
content = json.load(open(os.path.join(ROOT, ".chowdown/content.json")))
catalog = json.load(open(os.path.join(ROOT, ".chowdown/photo_catalog.json")))["dishes"]

CATS = [c for t in content["menu"]["tabs"] for c in t["categories"]]
CAT_BY_NAME = {c["name"]: c for c in CATS}

def slug(name):
    s = re.sub(r"\(.*?\)", "", name).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return {"appetizers-dips": "appetizers", "tacos": "tacos",
            "lunch-time-mon-fri-11-00am-2-00pm": "lunch",
            "combinations-make-your-own-combo": "combos",
            "house-specials-molcajete": "house-specials",
            "mariscos-tequilas": "mariscos",
            "side-orders-add-ons": "add-ons"}.get(s, s)

COURSE_GROUPS = [
    ("Starters", ["Appetizers / Dips", "Loaded Fries", "Fresh Guacamoles", "Nachos",
                  "Nachos Specialties", "Soups & Salads"]),
    ("Tacos & Street", ["Tacos (Orders)", "Single Tacos"]),
    ("Burritos, Quesadillas & More", ["Burritos", "Chimichangas", "Quesadillas", "Enchiladas"]),
    ("Fajitas & Grill", ["Sizzling Fajitas", "Fajitas Specialties", "Steak Entrees", "Chicken Entrees"]),
    ("House Specials", ["House Specials / Molcajete", "Specialties (General)", "All Time Favorites",
                        "Combinations / Make Your Own Combo"]),
    ("Mariscos", ["Mariscos Tequilas (Seafood)", "Mojarras", "Aguachiles", "Ceviches", "Seafood (Entrées)"]),
    ("Lunch, Kids & Sides", ["Lunch Time (Mon-Fri 11:00am-2:00pm)", "Vegetarian", "Kids", "Eggs",
                             "Side Orders", "Side Orders / Add-Ons"]),
]

# Category card photos — representative real shots (photo verified). Missing = honest text tile.
CATEGORY_PHOTO = {
    "Appetizers / Dips": "elote-hand", "Loaded Fries": "loaded-fries",
    "Soups & Salads": "menudo", "Burritos": "burrito-queso",
    "Tacos (Orders)": "tacos-asada", "Single Tacos": "tacos-asada",
    "Quesadillas": "quesadilla-board", "Specialties (General)": "trompo-tower",
    "Fajitas Specialties": "skillet-alambre", "All Time Favorites": "combo-board",
    "Sizzling Fajitas": "skillet-held", "Steak Entrees": "carne-asada",
    "House Specials / Molcajete": "steak-shrimp",
    "Combinations / Make Your Own Combo": "combo-elote",
    "Mariscos Tequilas (Seafood)": "camarones-diabla",
    "Seafood (Entrées)": "camarones-close",
    "Lunch Time (Mon-Fri 11:00am-2:00pm)": "quesabirria",
}

# Item-level photos. Tier 1: EXACT matches (dish in photo == dish on menu).
ITEM_PHOTO = {
    "menudo": "menudo", "loaded fries": "loaded-fries",
    "quesabirria (3)": "quesabirria", "lunch quesabirria (2)": "quesabirria",
    "*carne asada": "carne-asada", "*steak and shrimp (5)": "steak-shrimp",
    "camarones a la diabla": "camarones-diabla", "trompo de pastor": "trompo-tower",
    "mexican street elote": "elote-hand",
}
# Tier 2: keyword matches for the SCHEMA only (the fleet standard: a real photo of
# this kitchen's version of the dish type). Ordered most-specific first; salads
# and soups (other than menudo) never get a photo.
KEYWORD_PHOTO = [
    ("quesabirria", "quesabirria"), ("birria", "quesabirria"),
    ("quesadilla", "quesadilla-board"), ("burrito", "burrito-queso"),
    ("fajita", "skillet-alambre"), ("asada", "carne-asada"),
    ("elote", "elote-hand"), ("esquite", "elote-hand"),
    ("camaron", "camarones-diabla"), ("taco", "tacos-asada"),
    ("shrimp", "camarones-close"), ("fries", "loaded-fries"),
]
def item_photo(name, schema=False):
    n = name.lower().strip()
    if n in ITEM_PHOTO:
        return ITEM_PHOTO[n]
    if not schema:
        return None
    if "salad" in n or ("soup" in n or "caldo" in n):
        return None
    for kw, b in KEYWORD_PHOTO:
        if kw in n:
            return b
    return None

def pic(base, ratio, sizes, alt="", cls="", eager=False):
    v = catalog[base]["variants"]
    srcset = ", ".join(f"{IMG}/{fn} {fn.rsplit('-',1)[1].split('.')[0]}w" for fn in v)
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return (f'<div class="mph {cls}" style="aspect-ratio:{ratio}">'
            f'<img src="{IMG}/{base}-800.webp" srcset="{srcset}" sizes="{sizes}" '
            f'alt="{e(alt)}" {load} decoding="async"></div>')

def price_of(raw):
    m = re.search(r"(\d+(?:\.\d{1,2})?)", str(raw or ""))
    return m.group(1) if m else None

# ---------------------------------------------------------------- schema
def item_ld(it):
    node = {"@type": "MenuItem", "name": it["name"].strip()}
    if it.get("description"): node["description"] = it["description"].strip()
    p = price_of(it.get("price"))
    if p: node["offers"] = {"@type": "Offer", "price": p, "priceCurrency": "USD"}
    b = item_photo(it["name"], schema=True)
    if b: node["image"] = f"{DOMAIN}{IMG}/{b}-1600.webp"
    return node

def section_ld(cat):
    return {"@type": "MenuSection", "name": cat["name"],
            "hasMenuItem": [item_ld(i) for i in cat["items"]]}

def ld_block(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + '</script>'

# ---------------------------------------------------------------- chrome
def chrome(depth_title, desc, canon, og_img=None):
    top = open(os.path.join(ROOT, ".chowdown/chrome/top.html")).read()
    top = top.replace('href="../', 'href="/').replace('src="../', 'src="/')
    top = top.replace("url(../", "url(/")
    # strip old ld+json blocks (page-specific schema gets injected per page)
    top = re.sub(r'<script type="application/ld\+json">.*?</script>', "", top, flags=re.S)
    top = re.sub(r"<title>.*?</title>", f"<title>{e(depth_title)}</title>", top, flags=re.S)
    top = re.sub(r'(<meta name="description" content=")[^"]*(")', r"\g<1>" + e(desc) + r"\2", top)
    top = re.sub(r'(<link rel="canonical" href=")[^"]*(")', r"\g<1>" + canon + r"\2", top)
    top = re.sub(r'(<meta property="og:url" content=")[^"]*(")', r"\g<1>" + canon + r"\2", top)
    top = re.sub(r'(<meta property="og:title" content=")[^"]*(")', r"\g<1>" + e(depth_title) + r"\2", top)
    if og_img:
        top = re.sub(r'(<meta property="og:image" content=")[^"]*(")',
                     r"\g<1>" + DOMAIN + og_img + r"\2", top)
    # menu-cards stylesheet after the site css
    top = top.replace("</head>", f'<link rel="stylesheet" href="/assets/css/menucards.css?v={CSS_VER}"></head>', 1)
    tail = open(os.path.join(ROOT, ".chowdown/chrome/tail.html")).read()
    tail = tail.replace('href="../', 'href="/').replace('src="../', 'src="/')
    return top, tail

# ---------------------------------------------------------------- landing
def build_landing():
    total = sum(len(c["items"]) for c in CATS)
    tiles_i = 0
    eager_left = 4  # first-viewport card photos load eagerly (LCP)
    groups_html = ""
    for g, names in COURSE_GROUPS:
        cards = ""
        for name in names:
            cat = CAT_BY_NAME.get(name)
            if not cat: continue
            n = len(cat["items"]); s = slug(name)
            b = CATEGORY_PHOTO.get(name)
            label = re.sub(r"\s*\(.*?\)", "", name)
            if name == "Lunch Time (Mon-Fri 11:00am-2:00pm)": label = "Lunch Time"
            if b:
                photo = pic(b, "16/10", "(max-width:860px) 92vw, 300px", alt=label,
                            eager=eager_left > 0)
                eager_left -= 1 if eager_left > 0 else 0
                cards += (f'<a class="mcard" href="/menu/{s}/">{photo}'
                          f'<div class="mcb"><span class="mcn">{e(label)}</span>'
                          f'<span class="mcp">{n}</span></div></a>')
            else:
                tone = ["t-blue", "t-pink", "t-teal"][tiles_i % 3]; tiles_i += 1
                cards += (f'<a class="mcard mtile {tone}" href="/menu/{s}/">'
                          f'<span class="mti">{e(label[:1])}</span>'
                          f'<div class="mcb"><span class="mcn">{e(label)}</span>'
                          f'<span class="mcp">{n}</span></div></a>')
        groups_html += (f'<section class="mgroup"><div class="mgey">{e(g)}</div>'
                        f'<div class="mgrid">{cards}</div></section>')
    ld = {"@context": "https://schema.org", "@type": "Menu", "@id": f"{DOMAIN}/menu/#menu",
          "name": "Tequilas Tacos & Bar Menu", "hasMenuSection": [section_ld(c) for c in CATS]}
    crumb = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": DOMAIN + "/"},
        {"@type": "ListItem", "position": 2, "name": "Menu", "item": DOMAIN + "/menu/"}]}
    top, tail = chrome("Our Menu | Tequilas Tacos & Bar - Charlotte",
                       f"Browse the full Tequilas Tacos & Bar menu - {total} dishes across "
                       f"{len(CATS)} categories. Tacos, quesabirria, fajitas, mariscos, margaritas and more in Charlotte, NC.",
                       f"{DOMAIN}/menu/", og_img=f"{IMG}/tacos-asada-1600.webp")
    hero = ('<main id="top" class="menu-main"><section class="mhero"><div class="wrap">'
            '<p class="mhey">Kitchen &amp; Cantina &middot; ' + str(total) + ' dishes</p>'
            '<h1 class="mht">OUR<br>MENU</h1>'
            '<p class="mhsub">Every photo below was shot in this kitchen. Browse by course, '
            'or come hungry and let the trompo decide.</p></div></section>'
            '<div class="wrap mwrap">' + groups_html + "</div></main>")
    page = top + ld_block(ld) + ld_block(crumb) + hero + tail
    out = os.path.join(ROOT, "menu", "index.html")
    open(out, "w").write(page)
    return out

# ---------------------------------------------------------------- category pages
def build_category(cat, prev_cat, next_cat):
    name = cat["name"]; s = slug(name)
    label = re.sub(r"\s*\(.*?\)", "", name)
    if name == "Lunch Time (Mon-Fri 11:00am-2:00pm)": label = "Lunch Time"
    n = len(cat["items"])
    b = CATEGORY_PHOTO.get(name)
    # header
    head_photo = pic(b, "16/11", "(max-width:860px) 94vw, 560px", alt=label, eager=True) if b else ""
    sub = e(cat.get("description") or "")
    header = (f'<section class="cphero{" nophoto" if not b else ""}"><div class="wrap cph-in">'
              f'<div class="cph-txt"><a class="cpback" href="/menu/">&larr; Full menu</a>'
              f'<h1 class="mht cph-t">{e(label.upper())}</h1>'
              f'<p class="mhey">{n} item{"s" if n != 1 else ""}'
              + (f' &middot; {sub}' if sub else "") + "</p></div>"
              + (f'<div class="cph-ph">{head_photo}</div>' if b else "") + "</div></section>")
    # items: photo feature rows first (exact matches), then clean list
    feats, rows = "", ""
    for it in cat["items"]:
        ib = item_photo(it["name"])
        p = price_of(it.get("price"))
        price_html = f'<span class="mip">${e(p)}</span>' if p else ""
        desc = f'<p class="mid">{e(it["description"].strip())}</p>' if it.get("description") else ""
        if ib:
            feats += (f'<div class="mfeat">{pic(ib, "4/3", "(max-width:860px) 94vw, 420px", alt=it["name"])}'
                      f'<div class="mfb"><div class="mih"><span class="min">{e(it["name"])}</span>{price_html}</div>{desc}</div></div>')
        else:
            rows += (f'<div class="mitem"><div class="mih"><span class="min">{e(it["name"])}</span>'
                     f'<span class="mdots"></span>{price_html}</div>{desc}</div>')
    nav_html = '<nav class="cpnav">'
    if prev_cat is not None:
        pl = re.sub(r"\s*\(.*?\)", "", prev_cat["name"])
        nav_html += f'<a href="/menu/{slug(prev_cat["name"])}/">&larr; {e(pl)}</a>'
    nav_html += '<a href="/menu/">All categories</a>'
    if next_cat is not None:
        nl = re.sub(r"\s*\(.*?\)", "", next_cat["name"])
        nav_html += f'<a href="/menu/{slug(next_cat["name"])}/">{e(nl)} &rarr;</a>'
    nav_html += "</nav>"
    ld = {"@context": "https://schema.org", **section_ld(cat),
          "@id": f"{DOMAIN}/menu/{s}/#section"}
    crumb = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": DOMAIN + "/"},
        {"@type": "ListItem", "position": 2, "name": "Menu", "item": DOMAIN + "/menu/"},
        {"@type": "ListItem", "position": 3, "name": label, "item": f"{DOMAIN}/menu/{s}/"}]}
    top, tail = chrome(f"{label} | Menu | Tequilas Tacos & Bar - Charlotte",
                       f"{label} at Tequilas Tacos & Bar in Charlotte, NC - {n} dishes with prices.",
                       f"{DOMAIN}/menu/{s}/",
                       og_img=(f"{IMG}/{b}-1600.webp" if b else None))
    body = (f'<main id="top" class="menu-main">{header}<div class="wrap mwrap">'
            + (f'<div class="mfeats">{feats}</div>' if feats else "")
            + f'<div class="mlist">{rows}</div>{nav_html}</div></main>')
    page = top + ld_block(ld) + ld_block(crumb) + body + tail
    d = os.path.join(ROOT, "menu", s)
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w").write(page)
    return s

if __name__ == "__main__":
    out = build_landing()
    print("landing:", out)
    slugs = []
    for i, cat in enumerate(CATS):
        prev_cat = CATS[i-1] if i > 0 else None
        next_cat = CATS[i+1] if i < len(CATS)-1 else None
        slugs.append(build_category(cat, prev_cat, next_cat))
    print(f"{len(slugs)} category pages:", ", ".join(slugs[:8]), "...")
    dup = [s for s in slugs if slugs.count(s) > 1]
    assert not dup, f"SLUG COLLISION: {set(dup)}"
