#!/usr/bin/env python3
"""Tequilas Tacos & Bar — menu board generator.
Faithful port of the Mi Jalapeno menu architecture (mi-jalapeno-website/build.py):
sticky category rail + search + filter chips + Surprise Me + item detail sheet,
skinned in Tequilas' bright tokens. Emits /menu/ + /menu/<slug>/ + menu-index.js.
Run:  python3 build_menu.py
"""
import json, os, re, html, unicodedata

ROOT = os.path.dirname(os.path.abspath(__file__))
DOMAIN = "https://tequilastacosbar.com"
IMG = "/assets/images/menu"
CSS_VER = "mc16"
ORDER_URL = "https://tequilastacosbar.com/comingsoon"
BRAND = "Tequilas Tacos & Bar"

e = html.escape
content = json.load(open(os.path.join(ROOT, ".chowdown/content.json")))
catalog = json.load(open(os.path.join(ROOT, ".chowdown/photo_catalog.json")))["dishes"]

CATS_LIST = [c for t in content["menu"]["tabs"] for c in t["categories"]]
_DROP = {"Mariscos Tequilas (Seafood)", "Mojarras", "Aguachiles", "Ceviches", "Seafood (Entrées)"}
CATS_LIST = [c for c in CATS_LIST if c["name"] not in _DROP]
seafood = json.load(open(os.path.join(ROOT, ".chowdown/seafood.json")))
CATS_LIST += seafood["categories"]
drinks = json.load(open(os.path.join(ROOT, ".chowdown/drinks.json")))
CATS_LIST += drinks["categories"]
CAT_BY_NAME = {c["name"]: c for c in CATS_LIST}

def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"\(.*?\)", "", s)
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-") or "x"
    return {"appetizers-dips": "appetizers",
            "lunch-time": "lunch",
            "combinations-make-your-own-combo": "combos",
            "house-specials-molcajete": "house-specials",
            "mariscos-especialidades": "mariscos",
            "camarones-variedades": "camarones",
            "cocteles-micheladas": "cocteles",
            "aguas-frescas-jarritos": "aguas-frescas",
            "molcajetes-especiales": "molcajetes",
            "fried-grilled-entrees-combos": "grill-combos",
            "other-noted-items-specials": "specials",
            "sopes-small-tacos": "sopes",
            "ceviches-vinagretas": "ceviches",
            "mojarras-fish": "mojarras",
            "soups-caldos": "caldos",
            "side-orders-add-ons": "add-ons",
            "margaritas-frozen-specials": "margaritas",
            "flights-frozen-samplers": "flights",
            "beers-micheladas": "beers",
            "tequilas-specialty-high-end-drinks": "tequilas",
            "mimosas-mojitos": "mimosas",
            "wines-sangria": "wines",
            "aguas-de-sabor": "aguas"}.get(s, s)

def label_of(name):
    if name == "Lunch Time (Mon-Fri 11:00am-2:00pm)": return "Lunch Time"
    return re.sub(r"\s*\(.*?\)", "", name).strip()

COURSE_GROUPS = [
    ("To start", ["Appetizers / Dips", "Loaded Fries", "Fresh Guacamoles", "Nachos",
                  "Nachos Specialties", "Soups & Salads"]),
    ("Plates", ["Tacos (Orders)", "Single Tacos", "Burritos", "Chimichangas", "Quesadillas",
                "Enchiladas", "Sizzling Fajitas", "Fajitas Specialties", "Steak Entrees",
                "Chicken Entrees", "House Specials / Molcajete", "Specialties (General)",
                "All Time Favorites", "Combinations / Make Your Own Combo", "Vegetarian"]),
    ("Lunch, kids & sides", ["Lunch Time (Mon-Fri 11:00am-2:00pm)", "Kids", "Eggs",
                             "Side Orders", "Side Orders / Add-Ons"]),
    ("Seafood House", ["Mariscos (Especialidades)", "Camarones - Variedades (Shell on or off where noted)",
                       "Aguachiles", "Ceviches & Vinagretas", "Mojarras & Fish",
                       "Cocteles & Micheladas", "Molcajetes & Especiales (Choice of two sides)",
                       "Soups & Caldos", "Fried / Grilled Entrees & Combos",
                       "Sopes & Small Tacos", "Sides", "Aguas Frescas & Jarritos",
                       "Other Noted Items / Specials"]),
    ("Cantina", ["Margaritas & Frozen Specials", "Flights & Frozen Samplers",
                 "Beers & Micheladas", "Cocktails", "Other Cocktails",
                 "Tequilas & Specialty High-End Drinks", "Mimosas & Mojitos",
                 "Wines & Sangria", "Aguas de Sabor (Flavored Waters)"]),
    ("Desserts", ["Desserts"]),
]
GROUP_OF = {c: g for g, cats in COURSE_GROUPS for c in cats}

# ---------------------------------------------------------------- photos
# (category, name-substring-lowercase, photo-base) — category-scoped, first match
# wins, exact dish depicted. No cross-category leaks. All bases visually verified.
PHOTO_RULES = [
    ("Appetizers / Dips", "mexican street elote", "elote-hand"),
    ("Loaded Fries", "loaded fries", "loaded-fries"),
    ("Soups & Salads", "menudo", "menudo"),
    ("House Specials / Molcajete", "quesabirria", "quesabirria"),
    ("All Time Favorites", "lunch quesabirria", "quesabirria"),
    ("Steak Entrees", "carne asada", "carne-asada"),
    ("Sizzling Fajitas", "steak and shrimp", "steak-shrimp"),
    ("Camarones - Variedades (Shell on or off where noted)", "camarones a la diabla", "camarones-diabla"),
    ("Soups & Caldos", "menudo", "menudo"),
    ("Specialties (General)", "trompo de pastor", "trompo-tower"),
    ("Margaritas & Frozen Specials", "la paleta margarita", "paleta-margarita"),
    ("Margaritas & Frozen Specials", "mexican lollipop", "mexican-lollipop"),
    ("Margaritas & Frozen Specials", "tropical margarita", "tropical-margarita"),
    ("Beers & Micheladas", "chamochela", "chamochela"),
    ("Desserts", "tres leches", "tres-leches"),
    ("Desserts", "lava cake", "lava-cake"),
    ("Desserts", "brownie", "lava-cake"),
]
def _has(base): return base in catalog
def item_photo(cat, name):
    nl = name.lower()
    for c, sub, base in PHOTO_RULES:
        if c == cat and sub in nl and _has(base):
            return base
    return None
def cat_photo(cat):
    for it in CAT_BY_NAME.get(cat, {}).get("items", []):
        b = item_photo(cat, it["name"])
        if b: return b
    return None
# Decorative card/section photo per category. Reuse is fine (illustrative).
CATEGORY_PHOTO = {
    "Appetizers / Dips": "elote-hand", "Loaded Fries": "loaded-fries",
    "Soups & Salads": "menudo", "Burritos": "burrito-queso",
    "Tacos (Orders)": "tacos-asada", "Single Tacos": "tacos-asada",
    "Quesadillas": "quesadilla-board", "Specialties (General)": "trompo-tower",
    "Fajitas Specialties": "skillet-alambre", "All Time Favorites": "combo-board",
    "Sizzling Fajitas": "skillet-held", "Steak Entrees": "carne-asada",
    "House Specials / Molcajete": "steak-shrimp",
    "Combinations / Make Your Own Combo": "combo-elote",
    "Mariscos (Especialidades)": "camarones-diabla",
    "Camarones - Variedades (Shell on or off where noted)": "camarones-close",
    "Cocteles & Micheladas": "chamochela", "Soups & Caldos": "menudo",
    "Lunch Time (Mon-Fri 11:00am-2:00pm)": "quesabirria",
    "Chimichangas": "burrito-queso-2", "Chicken Entrees": "pollo-plate",
    "Margaritas & Frozen Specials": "paleta-margarita",
    "Flights & Frozen Samplers": "tequila-reposado",
    "Beers & Micheladas": "chamochela", "Cocktails": "tropical-margarita",
    "Other Cocktails": "mexican-lollipop",
    "Tequilas & Specialty High-End Drinks": "tequila-blanco",
    "Mimosas & Mojitos": "marg-spicy", "Desserts": "tres-leches",
}
def card_photo(cat):
    b = CATEGORY_PHOTO.get(cat) or cat_photo(cat)
    return b if (b and _has(b)) else None

def pic(base, ratio, sizes, alt="", eager=False):
    v = catalog[base]["variants"]
    srcset = ", ".join(f"{IMG}/{fn} {fn.rsplit('-',1)[1].split('.')[0]}w" for fn in v)
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return (f'<div class="mph" style="aspect-ratio:{ratio}">'
            f'<img src="{IMG}/{base}-800.webp" srcset="{srcset}" sizes="{sizes}" '
            f'alt="{e(alt)}" {load} decoding="async"></div>')

# ---------------------------------------------------------------- price / tags
_MONEY = re.compile(r"\$\s*(\d+(?:\.\d{1,2})?)")
_BARE = re.compile(r"(?<![\d($])(\d+\.\d{2})\b")
def _find_money(s):
    m = _MONEY.search(s)
    if m: return m, "$" + m.group(1)
    m = _BARE.search(s)
    if m: return m, "$" + m.group(1)
    return None, None
def parse_price(raw):
    raw = (raw or "").strip()
    amounts = [float(x) for x in _MONEY.findall(raw)] or \
              [float(x) for x in _BARE.findall(raw)]
    minp = min(amounts) if amounts else None
    variants = []
    for part in (raw.split("/") if "/" in raw else [raw]):
        part = part.strip()
        if not part: continue
        m, price = _find_money(part)
        if m:
            lab = (part[:m.start()] + part[m.end():]).strip().strip("-–").strip()
            lab = lab.strip("$").strip() or "Price"
            variants.append({"label": lab, "price": price})
        else:
            variants.append({"label": "Price", "price": part or "—"})
    if not variants:
        variants = [{"label": "Price", "price": raw or "—"}]
    # unsplittable junk (e.g. "1/2 DOZEN $$$"): fall back to the raw string
    if len(variants) > 1 and any(v["price"] == v["label"] == "Price" for v in variants):
        variants = [{"label": "Price", "price": raw}]
    return variants, minp

def price_str(variants):
    if len(variants) == 1 and variants[0]["label"] == "Price":
        return variants[0]["price"]
    return "  ".join(f'{v["label"]} {v["price"]}' for v in variants)
def row_price(variants, minp):
    if len(variants) == 1:
        return variants[0]["price"]
    if minp is not None:
        s = f"{minp:.2f}".rstrip("0").rstrip(".")
        return f"from ${s}"
    return ""

_SEAFOOD = ["shrimp", "camaron", "pulpo", "octopus", "fish", "tilapia", "mojarra", "scallop",
            "crab", "ceviche", "aguachile", "mariscos", "seafood", "del mar", "jaiba", "louisiana"]
_SPICY = ["diabla", "jalape", "chipotle", "toreado", "habanero", "spicy", "cucaracha", "picoso"]
_VEG = ["veggie", "vegetable", "vegetarian", "cheese quesadilla", "bean burrito", "spinach"]
def derive_tags(name, desc, cat):
    s = f"{name} {desc} {cat}".lower()
    t = []
    if "(new)" in s or re.search(r"\bnew\b", s): t.append("New")
    if any(k in s for k in _SEAFOOD): t.append("Seafood")
    if any(k in s for k in _SPICY): t.append("Spicy")
    if cat == "Vegetarian" or any(k in s for k in _VEG): t.append("Veggie")
    if "for two" in s or "para dos" in s or "family" in s: t.append("For two")
    return t

FILTERS = ["New", "Featured", "Spicy", "Seafood", "Veggie", "Under $10", "For two"]

# ---------------------------------------------------------------- board pieces
def rail(active=None):
    out = ['<aside class="mrail"><a class="mrail-brand" href="/menu/">'
           '<img src="/assets/images/favicon-180.png" alt="" width="46" height="46">'
           '<span><b>TEQUILAS</b><i>Full Menu</i></span></a>']
    for g, cats in COURSE_GROUPS:
        present = [c for c in cats if c in CAT_BY_NAME]
        if not present: continue
        out.append(f'<div class="mrg"><h4>{e(g)}</h4>')
        for c in present:
            n = len(CAT_BY_NAME[c]["items"])
            on = ' class="on"' if c == active else ""
            out.append(f'<a{on} href="/menu/{slug(c)}/">{e(label_of(c))}<span class="ct">{n}</span></a>')
        out.append("</div>")
    out.append("</aside>")
    return "".join(out)

def utility():
    chips = '<button class="mchip" type="button" data-t="All" aria-pressed="true">All</button>'
    chips += "".join(f'<button class="mchip" type="button" data-t="{e(f)}" aria-pressed="false">{e(f)}</button>' for f in FILTERS)
    return ('<div class="mutil"><label class="msearch"><span>&#8981;</span>'
            '<input id="msearch" type="search" placeholder="Search the menu" aria-label="Search the menu"></label>'
            '<button class="mfilter-toggle" type="button" aria-label="Filters" aria-expanded="false" aria-controls="mfilters" '
            'onclick="var u=this.closest(&#39;.mutil&#39;);var o=u.classList.toggle(&#39;filters-open&#39;);this.setAttribute(&#39;aria-expanded&#39;,o)">'
            '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true">'
            '<line x1="4" y1="8" x2="20" y2="8"/><line x1="4" y1="16" x2="20" y2="16"/>'
            '<circle cx="9" cy="8" r="2.7" fill="currentColor"/><circle cx="15" cy="16" r="2.7" fill="currentColor"/></svg></button>'
            f'<div class="mfilters" id="mfilters"><div id="mchips">{chips}</div>'
            '<button class="msurprise" id="msurprise" type="button">Surprise me</button></div></div>'
            '<div id="mresults" hidden></div>')

def item_row(it, cat):
    name = it["name"]; desc = (it.get("description") or "").strip()
    variants, minp = parse_price(it.get("price", ""))
    tags = derive_tags(name, desc, cat)
    base = item_photo(cat, name)
    data = {"n": name, "c": label_of(cat), "d": desc, "vars": variants, "tags": tags,
            "img": (IMG + "/" + base) if base else "", "order": ORDER_URL}
    data_attr = e(json.dumps(data, ensure_ascii=False))
    ename, epr, islug = e(name), e(row_price(variants, minp)), slug(name)
    tag_html = ('<div class="mr-tags">' + "".join(f'<span class="mtag">{e(t)}</span>' for t in tags) + "</div>") if tags else ""
    desc_html = f'<p class="mr-desc">{e(desc)}</p>' if desc else ""
    return (f'<div class="mrow" id="{islug}" data-item=\'{data_attr}\' tabindex="0" role="button" aria-label="{ename}">'
            f'<div class="mr-top"><span class="mr-name">{ename}</span><span class="mr-lead"></span><span class="mr-price">{epr}</span></div>'
            f'{tag_html}{desc_html}</div>')

def feat_card(it, cat, base):
    variants, minp = parse_price(it.get("price", ""))
    ename, epr, islug = e(it["name"]), e(row_price(variants, minp)), slug(it["name"])
    desc = (it.get("description") or "").strip()
    desc_html = f'<p class="mc-d">{e(desc)}</p>' if desc else ""
    return (f'<a class="mcard" href="/menu/{slug(cat)}/#{islug}">'
            f'{pic(base, "4/3", "(max-width:860px) 90vw, 320px", alt=it["name"])}'
            f'<div class="mc-b"><div class="mc-h"><span class="mc-n">{ename}</span><span class="mc-p">{epr}</span></div>{desc_html}</div></a>')

def sheet_html():
    return ('<button id="mscrim" hidden aria-label="Close menu item"></button>'
            '<div id="msheet" role="dialog" aria-modal="true" aria-label="Menu item" hidden></div>')

MENU_SCRIPTS = f'<script defer src="/assets/js/menu-index.js?v={CSS_VER}"></script><script defer src="/assets/js/menu.js?v={CSS_VER}"></script>'

# ---------------------------------------------------------------- schema
# schema-only keyword tier (fleet standard: real photo of this kitchen's version
# of the dish type). Never salads/soups.
KEYWORD_PHOTO = [
    ("quesabirria", "quesabirria"), ("birria", "quesabirria"),
    ("quesadilla", "quesadilla-board"), ("burrito", "burrito-queso"),
    ("fajita", "skillet-alambre"), ("asada", "carne-asada"),
    ("elote", "elote-hand"), ("esquite", "elote-hand"),
    ("camaron", "camarones-diabla"), ("taco", "tacos-asada"),
    ("shrimp", "camarones-close"), ("fries", "loaded-fries"),
    ("margarita", "paleta-margarita"), ("michelada", "chamochela"),
    ("tres leches", "tres-leches"),
]
def schema_photo(cat, name):
    n = name.lower()
    if "salad" in n or "soup" in n or "caldo" in n: return None
    for kw, b in KEYWORD_PHOTO:
        if kw in n and _has(b): return b
    return None

def menu_item_ld(it, cat):
    variants, _ = parse_price(it.get("price", ""))
    offers = []
    for v in variants:
        amt = _MONEY.search(v["price"])
        if amt:
            o = {"@type": "Offer", "price": amt.group(), "priceCurrency": "USD"}
            if v["label"] != "Price": o["name"] = v["label"]
            offers.append(o)
    node = {"@type": "MenuItem", "@id": f"{DOMAIN}/menu/{slug(cat)}/#{slug(it['name'])}",
            "name": it["name"].strip()}
    if (it.get("description") or "").strip(): node["description"] = it["description"].strip()
    b = item_photo(cat, it["name"]) or schema_photo(cat, it["name"])
    if b: node["image"] = f"{DOMAIN}{IMG}/{b}-1600.webp"
    if offers: node["offers"] = offers if len(offers) > 1 else offers[0]
    return node

def section_ld(cat):
    c = CAT_BY_NAME[cat]
    return {"@type": "MenuSection", "@id": f"{DOMAIN}/menu/{slug(cat)}/#section", "name": cat,
            "hasMenuItem": [menu_item_ld(it, cat) for it in c["items"]]}

def breadcrumb_ld(pairs):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": DOMAIN + u}
        for i, (n, u) in enumerate(pairs)]}

def ld_block(objs):
    return "".join('<script type="application/ld+json">' + json.dumps(o, ensure_ascii=False) + '</script>' for o in objs)

# ---------------------------------------------------------------- chrome
def chrome(title, desc, canon, og_img=None):
    top = open(os.path.join(ROOT, ".chowdown/chrome/top.html")).read()
    top = top.replace('href="../', 'href="/').replace('src="../', 'src="/')
    top = top.replace("url(../", "url(/")
    top = re.sub(r'<script type="application/ld\+json">.*?</script>', "", top, flags=re.S)
    top = re.sub(r"<title>.*?</title>", f"<title>{e(title)}</title>", top, flags=re.S)
    top = re.sub(r'(<meta name="description" content=")[^"]*(")', r"\g<1>" + e(desc) + r"\2", top)
    top = re.sub(r'(<link rel="canonical" href=")[^"]*(")', r"\g<1>" + canon + r"\2", top)
    top = re.sub(r'(<meta property="og:url" content=")[^"]*(")', r"\g<1>" + canon + r"\2", top)
    top = re.sub(r'(<meta property="og:title" content=")[^"]*(")', r"\g<1>" + e(title) + r"\2", top)
    if og_img:
        top = re.sub(r'(<meta property="og:image" content=")[^"]*(")', r"\g<1>" + DOMAIN + og_img + r"\2", top)
    top = top.replace("</head>", f'<link rel="stylesheet" href="/assets/css/menucards.css?v={CSS_VER}"></head>', 1)
    tail = open(os.path.join(ROOT, ".chowdown/chrome/tail.html")).read()
    tail = tail.replace('href="../', 'href="/').replace('src="../', 'src="/')
    return top, tail

# ---------------------------------------------------------------- pages
def page_category(cat, prev_c, next_c):
    c = CAT_BY_NAME[cat]; items = c["items"]
    lab = label_of(cat); grp = GROUP_OF.get(cat, "Menu")
    note = (c.get("description") or "").strip()
    note_html = f'<p class="msec-note">{e(note)}</p>' if note else ""
    feats = [(it, item_photo(cat, it["name"])) for it in items]
    feats = [(it, b) for it, b in feats if b][:3]
    feat_html = ('<div class="mfeat">' + "".join(feat_card(it, cat, b) for it, b in feats) + "</div>") if feats else ""
    cb = card_photo(cat)
    band = pic(cb, "16/7", "(max-width:860px) 94vw, 900px", alt=lab, eager=True) if (cb and not feats) else ""
    rows = '<div class="mgrid">' + "".join(item_row(it, cat) for it in items) + "</div>"
    prevlink = f'<a href="/menu/{slug(prev_c)}/">&larr; {e(label_of(prev_c))}</a>' if prev_c else "<span></span>"
    nextlink = f'<a href="/menu/{slug(next_c)}/">{e(label_of(next_c))} &rarr;</a>' if next_c else "<span></span>"
    spread = (f'<section id="mspread"><div class="msec-ey">{e(grp)} &middot; {len(items)} items</div>'
              f'<h1 class="msec-h">{e(lab.upper())}</h1>{note_html}{band}{feat_html}{rows}'
              f'<div class="mnav">{prevlink}<a href="/menu/">All</a>{nextlink}</div></section>')
    body = ('<main class="mboard">' + rail(cat) + '<div class="mcontent">' + utility() + spread
            + "</div></main>" + sheet_html())
    top, tail = chrome(f"{lab} | {BRAND} Menu",
                       f"{lab} at {BRAND} in Charlotte, NC. {len(items)} items with prices. Search the menu and order online.",
                       f"{DOMAIN}/menu/{slug(cat)}/",
                       og_img=(f"{IMG}/{cb}-1600.webp" if cb else None))
    ld = ld_block([section_ld(cat), breadcrumb_ld([("Home", "/"), ("Menu", "/menu/"), (lab, f"/menu/{slug(cat)}/")])])
    tail = tail.replace("</body>", MENU_SCRIPTS + "</body>")
    d = os.path.join(ROOT, "menu", slug(cat)); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w").write(top + ld + body + tail)

def page_board_landing(path, hero, groups_subset, title, desc, blurb=None):
    cats_in = [c for g, cats in COURSE_GROUPS if g in groups_subset for c in cats if c in CAT_BY_NAME]
    total = sum(len(CAT_BY_NAME[c]["items"]) for c in cats_in)
    eager_left = 4
    groups_html = ""
    for g, cats in COURSE_GROUPS:
        if g not in groups_subset: continue
        present = [c for c in cats if c in CAT_BY_NAME]
        if not present: continue
        cards = ""
        for c in present:
            n = len(CAT_BY_NAME[c]["items"])
            b = card_photo(c)
            photo = ""
            if b:
                photo = pic(b, "16/10", "(max-width:860px) 90vw, 300px", alt=label_of(c), eager=eager_left > 0)
                eager_left -= 1 if eager_left > 0 else 0
            cards += (f'<a class="mcard" href="/menu/{slug(c)}/">{photo}'
                      f'<div class="mc-b"><div class="mc-h"><span class="mc-n">{e(label_of(c))}</span>'
                      f'<span class="mc-p">{n}</span></div></div></a>')
        groups_html += (f'<section class="mlgroup"><div class="msec-ey">{e(g)}</div>'
                        f'<div class="mfeat mfeat-cats" style="margin:14px 0 0">{cards}</div></section>')
    board_ld = {"@context": "https://schema.org", "@type": "Menu", "@id": f"{DOMAIN}{path}#menu",
                "name": f"{BRAND} {hero.title()} Menu",
                "hasMenuSection": [section_ld(c) for c in cats_in]}
    intro = (f'<section id="mspread"><div class="msec-ey">Kitchen &amp; cantina &middot; {total} items</div>'
             f'<h1 class="msec-h" style="font-size:clamp(58px,13vw,170px);line-height:.8">{e(hero)}</h1>'
             '<p class="mintro">Every dish photo was shot in this kitchen. Search it, filter it, '
             'browse by course, or hit Surprise Me and let the trompo decide.</p>'
             f'<div class="mctas"><a class="btn-order" href="{e(ORDER_URL)}" target="_blank" rel="noopener">Order online</a></div>'
             f'{groups_html}</section>')
    body = ('<main class="mboard">' + rail(None) + '<div class="mcontent">' + utility() + intro
            + "</div></main>" + sheet_html())
    top, tail = chrome(title, desc, f"{DOMAIN}{path}", og_img=f"{IMG}/tacos-asada-1600.webp")
    ld = ld_block([board_ld, breadcrumb_ld([("Home", "/"), (hero.title(), path)])])
    tail = tail.replace("</body>", MENU_SCRIPTS + "</body>")
    d = os.path.join(ROOT, path.strip("/")); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w").write(top + ld + body + tail)

def page_menu_landing():
    page_board_landing("/menu/", "MENU",
                       [g for g, _ in COURSE_GROUPS],
                       f"Our Menu | {BRAND} - Charlotte",
                       "The full Tequilas Tacos & Bar menu: tacos, quesabirria, fajitas, mariscos, "
                       "margaritas and more. Search, filter, order online.")
    page_board_landing("/seafood/", "SEAFOOD", ["Seafood House"],
                       f"Seafood Menu | {BRAND} - Charlotte",
                       "Louisiana-style Mexican seafood in Charlotte: aguachiles, mojarras, camarones, "
                       "ceviches, micheladas. Search the menu and order online.",
                       blurb="Louisiana-style mariscos, aguachiles and mojarras, shot in this kitchen. Search it, filter it, or browse by course.")
    page_board_landing("/drinks/", "DRINKS", ["Cantina", "Desserts"],
                       f"Drinks Menu | {BRAND} - Charlotte",
                       "Margaritas by the glass or pitcher, tequila flights, micheladas, cocktails and "
                       "desserts. Search the menu and order online.",
                       blurb="Margaritas, flights, micheladas and desserts, poured and plated here. Search it, filter it, or hit Surprise Me.")

def build_search_index():
    idx = []
    for c in CATS_LIST:
        cat = c["name"]
        for it in c["items"]:
            variants, minp = parse_price(it.get("price", ""))
            tags = derive_tags(it["name"], it.get("description", ""), cat)
            idx.append({"n": it["name"], "c": label_of(cat),
                        "u": f"/menu/{slug(cat)}/#{slug(it['name'])}",
                        "p": minp, "v": row_price(variants, minp), "t": "|".join(tags),
                        "f": 1 if item_photo(cat, it["name"]) else 0,
                        "d": it.get("description", "")})
    os.makedirs(os.path.join(ROOT, "assets", "js"), exist_ok=True)
    open(os.path.join(ROOT, "assets", "js", "menu-index.js"), "w").write(
        "window.MENU_INDEX=" + json.dumps(idx, ensure_ascii=False, separators=(",", ":")) + ";")
    return len(idx)


# ---------------------------------------------------------------- gallery
GALLERY_SHOTS = [
    "tacos-asada", "quesabirria", "trompo-tower", "loaded-fries",
    "carne-asada", "steak-shrimp", "camarones-diabla", "skillet-alambre",
    "elote-hand", "burrito-queso", "quesadilla-board", "combo-board",
    "pollo-plate", "menudo", "paleta-margarita", "tropical-margarita",
    "mexican-lollipop", "chamochela", "tres-leches", "lava-cake",
    "hero-interior", "hero-photoroom",
]
def page_gallery():
    tiles = "".join(pic(bs, "1/1", "(max-width:860px) 45vw, 22vw", alt="Tequilas Tacos & Bar")
                    for bs in GALLERY_SHOTS if _has(bs))
    body = ('<main class="galmain"><div class="wrap">'
            '<div class="msec-ey">From the kitchen &amp; cantina</div>'
            '<h1 class="msec-h" style="font-size:clamp(58px,13vw,170px);line-height:.8">GALLERY</h1>'
            '<p class="mintro">Every shot below was taken here - the food, the drinks, the room.</p>'
            f'<div class="gal-grid">{tiles}</div></div></main>')
    top, tail = chrome(f"Gallery | {BRAND} - Charlotte",
                       "Photos from Tequilas Tacos & Bar in Charlotte: tacos, quesabirria, the trompo, "
                       "margaritas, desserts and the dining room.",
                       f"{DOMAIN}/gallery/")
    ld = ld_block([breadcrumb_ld([("Home", "/"), ("Gallery", "/gallery/")])])
    d = os.path.join(ROOT, "gallery"); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w").write(top + ld + body + tail)

if __name__ == "__main__":
    n = build_search_index()
    names = [c["name"] for c in CATS_LIST]
    slugs = [slug(x) for x in names]
    dup = [s for s in slugs if slugs.count(s) > 1]
    assert not dup, f"SLUG COLLISION: {set(dup)}"
    page_menu_landing()
    page_gallery()
    for i, cat in enumerate(names):
        page_category(cat, names[i-1] if i > 0 else None,
                      names[i+1] if i < len(names)-1 else None)
    print(f"landing + {len(names)} category pages + search index ({n} items)")
