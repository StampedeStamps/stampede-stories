#!/usr/bin/env python3
"""Stamp Stories static site builder (stdlib only). Usage: build.py [outdir]"""
import csv, datetime, html, io, json, os, re, shutil, sys, urllib.request
from collections import defaultdict
from pathlib import Path
from urllib.parse import quote, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent / "tools"))
from make_blurbs import blurb, category, check as check_blurb  # blurbs are written fresh on every build

ROOT = Path(__file__).resolve().parent
SITE_URL = os.environ.get("SITE_URL", "https://stampedestamps.github.io/stampede-stories").rstrip("/")
# The workflow builds SITE_URL from the account name "StampedeStamps"; hosts are case-insensitive, but the address
# Google Search Console verified is all lowercase, so every canonical, sitemap and feed link uses a lowercase host.
_scheme, _, _rest = SITE_URL.partition("://")
_host, _slash, _path = _rest.partition("/")
SITE_URL = f"{_scheme}://{_host.lower()}{_slash}{_path}"
STORE = "https://www.ebay.com/str/stampedeusa"
# ONE catalog on the store's own site (Douglas, Sun 2026-10-11, ruling D1; done Fri 2026-10-16): an item page whose
# listing has a page on www.stampedestamps.store names that page as its canonical and links shoppers to it.
STORE_SITE = "https://www.stampedestamps.store"
CATALOG = f"{STORE_SITE}/catalog/"
# Photos from the store's public photo list. OFF: on Sun 2026-10-11 Douglas chose "Submit, stay text-only meanwhile".
# Set True only on his word; the photo layout then turns on everywhere with no other change.
STORE_PHOTOS = False
PURPLE = "#4B006E"
SIGN = "- StampedeUSA"
SITE_NAME = "Stamp Stories"
OG_DEFAULT = "assets/og-stamp-stories.png"  # 1200x630, made once by tools/make_og_image.js, never at build time
# Google Search Console ownership proof for the URL-prefix property https://stampedestamps.github.io/stampede-stories/
# (Douglas, Sun 2026-10-11 "go traffic"). Removing it un-verifies the site, so tests/test_build.py checks it stays.
GOOGLE_SITE_VERIFICATION = "LLXJ-AdRojWsQOPVel5D4eVxu6o9vwAzJJ_nle-0bQ8"
FONT = "assets/fonts/league-gothic-latin-400-normal.woff2"
DECADE_MIN = 30  # a category this big gets decade sub-headings, taken only from a year the title itself states
FORMATS = {"FIXED_PRICE": "Buy It Now", "AUCTION": "Auction"}
e = html.escape


def read(data, name):
    # utf-8-sig: a CSV saved on Windows with a byte-order mark reads the same as one without.
    with open(Path(data) / name, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def fmt_name(row):
    return FORMATS.get((row.get("format") or "").strip().upper(), "")


def title_year(title):
    """The first year a title mentions, or None. Catalog numbers are not years: a number right after '#', '-',
    '/', 'Plate ' or a letter is skipped, and so is a run of bare numbers that continues a '#' number
    ("Scott #1928 1929 1930 1931 (MNH) 1981" -> 1981)."""
    prev = None
    for m in re.finditer(r"(#)?([A-Z]{0,3})(\d{3,5})\b|\S+", title):
        if m.group(3) is None:
            prev = None if m.group(0) not in ("+", "&", ",") else prev
            continue
        num, start = int(m.group(3)), m.start(3)
        if m.group(1) or m.group(2):
            prev = num
            continue
        if prev is not None and abs(num - prev) <= 50:
            prev = num
            continue
        prev = None
        before = title[:start]
        if re.search(r"(?:[-/\w]|Plate )$", before) or not re.fullmatch(r"1[89]\d\d|20\d\d", m.group(3)):
            continue
        if 1840 <= num <= datetime.date.today().year + 1:
            return num
    return None


def face(title):
    """What a photo-less stamp prints as its big figure, taken only from the title: a cents denomination ("3c"),
    else "Forever", else the first year the title states, else nothing. Dollar figures are never printed outside
    the full title."""
    m = re.search(r"(?<![\w.$])(\d{1,3})c\b", title)
    if m:
        return m.group(1) + "c"
    if re.search(r"\bForever\b", title):
        return "Forever"
    y = title_year(title)
    return str(y) if y else ""


def slug(text):
    return "cat-" + (re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "other")


def jsonld(obj):
    return ('<script type="application/ld+json">'
            + json.dumps(obj, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + "</script>")


def clip(text, n=200):
    text = " ".join(text.split())
    if len(text) <= n:
        return text
    return text[:n].rsplit(" ", 1)[0].rstrip(",;:") + "..."


def postmark(day, uid):
    """A circular date cancel in brand ink: the site name around the ring, the date inside, wavy killer bars.
    Decorative only (aria-hidden); each one on a page needs its own uid for the text path. The page prints the build
    date; POSTMARK_JS then sets the visitor's own date, because the site is rebuilt only on mornings when the
    listings change (no rebuild on 10-13 or 10-14), and a postmark should never read yesterday."""
    arc = f"pm-{uid}"
    return (f'<svg class="postmark" viewBox="0 0 250 120" aria-hidden="true" focusable="false">'
            f'<defs><path id="{arc}" d="M60 60m-41 0a41 41 0 1 1 82 0a41 41 0 1 1-82 0"/></defs>'
            '<g fill="none" stroke="currentColor"><circle cx="60" cy="60" r="55" stroke-width="3.2"/>'
            '<circle cx="60" cy="60" r="31" stroke-width="1.6"/>'
            + "".join(f'<path d="M126 {y}q12-7 24 0t24 0t24 0t24 0t24 0" stroke-width="5"/>' for y in (33, 50, 67, 84))
            + '</g><text class="ring"><textPath href="#' + arc + '" startOffset="1%">'
            'STAMP STORIES &#8226; STAMPEDEUSA &#8226;</textPath></text>'
            f'<text class="date pm-md" x="60" y="57" text-anchor="middle">{e(day.strftime("%b").upper())} {day.day}</text>'
            f'<text class="date pm-y" x="60" y="77" text-anchor="middle">{day.year}</text></svg>')


POSTMARK_JS = ("<script>(function(){var d=new Date(),m='JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC'.split(' ');"
               "[].forEach.call(document.querySelectorAll('.postmark .pm-md'),function(t){t.textContent=m[d.getMonth()]"
               "+' '+d.getDate();});[].forEach.call(document.querySelectorAll('.postmark .pm-y'),function(t){"
               "t.textContent=d.getFullYear();});})();</script>")


def stamp_html(r, img, cls="", lazy=True):
    """The stamp itself: its photo inside perforated paper, or, without a photo, a printed stamp built only from
    the title (its figure and its category). Decorative beside a heading that names it, so the photo's alt is the
    title only where no heading does that job (cls says which)."""
    load = ' loading="lazy" decoding="async"' if lazy else ""
    if img:
        return (f'<span class="stamp perf edged photo {cls}"><img src="{e(img)}" alt=""{load}></span>')
    f = face(r["title"])
    return (f'<span class="stamp perf edged type-stamp {cls}"><span class="frame">'
            f'<span class="face{" long" if len(f) > 4 else ""}">{e(f)}</span>'
            f'<span class="ins">{e(category(r))}</span></span></span>')


def page(title, desc, body, canon, depth=0, base=None, image=None, extra_head="", main_class="", noindex=False,
         catalog_link=False):
    """catalog_link: also link the store's photo catalog in the header and footer (home page only: an item page
    links to its own store page, and only when that page exists)."""
    pre = f"{base}/" if base else "../" * depth
    img = image or f"{SITE_URL}/{OG_DEFAULT}"
    robots = '\n<meta name="robots" content="noindex">' if noindex else ""
    cat_nav = f'<a href="{CATALOG}">Photo catalog</a>' if catalog_link else ""
    cat_foot = f'<p><a href="{CATALOG}">Browse the photo catalog</a></p>' if catalog_link else ""
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}">{robots}
<link rel="canonical" href="{e(canon)}">
<meta property="og:site_name" content="{SITE_NAME}"><meta property="og:type" content="website">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{e(canon)}"><meta property="og:image" content="{e(img)}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(desc)}"><meta name="twitter:image" content="{e(img)}">
<meta name="theme-color" content="{PURPLE}">
<meta name="google-site-verification" content="{GOOGLE_SITE_VERIFICATION}">
<link rel="icon" href="{pre}assets/favicon.svg" type="image/svg+xml">
<link rel="preload" href="{pre}{FONT}" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{pre}assets/site.css">
<link rel="alternate" type="application/rss+xml" title="{SITE_NAME}" href="{pre}feed.xml">{extra_head}
</head><body>
<a class="skip" href="#main">Skip to the stamps</a>
<header class="selvage"><div class="top"><a class="mark" href="{pre}index.html">{SITE_NAME}<small>by StampedeUSA</small></a>
<nav class="links" aria-label="StampedeUSA shops">{cat_nav}<a class="store" href="{STORE}">eBay store</a></nav></div></header>
<main id="main"{f' class="{main_class}"' if main_class else ""}>{body}</main>
<footer class="selvage"><div class="foot"><p class="sign">{SIGN}</p>
<p><a href="{STORE}">Visit the StampedeUSA store on eBay</a></p>{cat_foot}
<p><a href="{pre}feed.xml">New listings by RSS</a></p></div></footer>
</body></html>
"""


def load_stories(data, rows):
    """data/stories.csv is used for an item only while it is listed AND its title still equals title_at_writing;
    otherwise the page falls back to the generated blurb. source_url holds one or more https addresses separated by
    spaces. A story with at least one is a sourced story: only those are featured and marked "Has a story". A story
    with NO SOURCE is a warm, claim-free line shown on its own page only. headline, hook and fact are optional."""
    if not (Path(data) / "stories.csv").exists():
        return {}
    titles = {r["item"]: r["title"] for r in rows}
    out = {}
    for s in read(data, "stories.csv"):
        it = (s.get("item") or "").strip()
        story = (s.get("story") or "").strip()
        if it in titles and story and s.get("title_at_writing") == titles[it]:
            extra = {k: (s.get(k) or "").strip() for k in ("headline", "hook", "fact")}
            for text in [story] + [v for v in extra.values() if v]:
                check_blurb({"item": it, "title": titles[it]}, text)
            sources = [u for u in (s.get("source_url") or "").split() if u.startswith("https://")]
            out[it] = dict(story=story, sources=sources, **extra)
    return out


def store_pages(timeout=20):
    """{item: True when its store page shows a photo} for every listing with a page on www.stampedestamps.store,
    read from the store's public sitemap and photo list. {} when the store cannot be read: every item page then stays
    canonical to itself, so no page ever points at a store page that does not exist. The store refresh runs after
    ours (3:45 vs 3:30 AM ET), so a brand-new listing gets its store link at the next build."""
    def get(path):
        req = urllib.request.Request(STORE_SITE + path, headers={"User-Agent": "StampStories-build"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8")
    try:
        pages = set(re.findall(r"/catalog/item/(\d+)\.html</loc>", get("/sitemap.xml")))
    except Exception as ex:  # noqa: BLE001 - any failure means "no store links this build", never a failed build
        print(f"store pages not read ({type(ex).__name__}); every item page stays canonical to itself")
        return {}
    try:
        photos = {r["item"] for r in csv.DictReader(io.StringIO(get("/data/catalog_images.csv")))}
    except Exception:  # noqa: BLE001 - without the photo list the link just does not promise a photo
        photos = set()
    return {it: it in photos for it in pages}


def store_photos(timeout=20):
    """{item: https photo address} from the store's public photo list (columns item,image; image is a path on the
    store's site). {} on any failure, so the site simply stays text-only for that build."""
    try:
        req = urllib.request.Request(STORE_SITE + "/data/catalog_images.csv", headers={"User-Agent": "StampStories-build"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            rows = list(csv.DictReader(io.StringIO(r.read().decode("utf-8"))))
    except Exception as ex:  # noqa: BLE001
        print(f"store photos not read ({type(ex).__name__}); pages stay text-only")
        return {}
    return {r["item"]: f"{STORE_SITE}/{r['image'].lstrip('/')}" for r in rows
            if (r.get("item") or "").isdigit() and (r.get("image") or "").startswith("images/")}


def main(out, data=None, store=None, photos=None, today=None):
    """store: {item: has a photo} from store_pages(); None or {} builds every item page canonical to itself.
    photos: {item: https photo address} (store_photos() when STORE_PHOTOS is on); data/images.csv also works.
    today: the date on the postmarks and the pick of today's story (tests pin it)."""
    data = Path(data) if data else ROOT / "data"
    out = Path(out)
    store = store or {}
    today = today or datetime.datetime.now(datetime.timezone.utc).date()
    if out.exists():
        shutil.rmtree(out)
    (out / "item").mkdir(parents=True)
    shutil.copytree(ROOT / "assets", out / "assets")
    rows = read(data, "listings.csv")
    # Written fresh from the current title/category/format on every build, so a refresh that ends,
    # adds, retitles or recategorizes a listing can never leave a stale claim on a page.
    blurbs = {r["item"]: blurb(r) for r in rows}
    for r in rows:
        check_blurb(r, blurbs[r["item"]])
    stories = load_stories(data, rows)
    text_of = {it: (stories[it]["story"] if it in stories else blurbs[it]) for it in blurbs}
    imgs = {}
    if (data / "images.csv").exists():
        imgs = {r["item"]: r["image_url"].strip() for r in read(data, "images.csv")
                if (r.get("image_url") or "").strip().startswith("https://")}
    imgs.update({k: v for k, v in (photos or {}).items() if v.startswith("https://")})
    rows.sort(key=lambda r: int(r["item"]), reverse=True)
    by_item = {r["item"]: r for r in rows}
    lastmod = os.environ.get("SITE_LASTMOD") or datetime.datetime.now(datetime.timezone.utc).date().isoformat()

    groups = defaultdict(list)
    for r in rows:
        groups[category(r)].append(r)
    cats = sorted(groups, key=lambda c: (-len(groups[c]), c))
    same_title = defaultdict(list)  # identical titles: shown once on the home page, with each listing linked
    for r in rows:
        same_title[r["title"]].append(r)

    # Sourced stories, in the order stories.csv lists them (the writer's running order), one per title.
    told = [by_item[it] for it, s in stories.items() if s["sources"] and same_title[by_item[it]["title"]][0] is by_item[it]]
    headline = {r["item"]: stories[r["item"]]["headline"] or r["title"] for r in told}

    def sources_html(srcs):
        links = ", ".join(f'<a href="{e(u)}" rel="noopener">{e(urlparse(u).netloc.removeprefix("www."))}</a>'
                          for u in srcs)
        return f'<p class="source">Sources for the history: {links}</p>' if srcs else ""

    def more_stories(skip, pre):
        picks = [r for r in told if r["item"] != skip][:3]
        if not picks:
            return ""
        return ('<section class="more-stories"><h2>Stories worth a read</h2><ul>'
                + "".join(f'<li><a href="{pre}{r["item"]}.html">{e(headline[r["item"]])}</a></li>' for r in picks)
                + "</ul></section>")

    # ---- item pages
    for r in rows:
        it, t, cat = r["item"], r["title"], category(r)
        twins = same_title[t]
        nth = f" (listing {twins.index(r) + 1} of {len(twins)})" if len(twins) > 1 else ""
        img = imgs.get(it)
        st = stories.get(it)
        facts = [f"<span>Category: {e(cat)}</span>"]
        if fmt_name(r):
            facts.append(f"<span>Format: {fmt_name(r)}</span>")
        if (r.get("condition") or "").strip():
            facts.append(f"<span>Condition: {e(r['condition'].strip())}</span>")
        # Related: the next listings in the same category (wrapping around), one per title, never this title.
        k = next(i for i, x in enumerate(groups[cat]) if x is r)
        seen, rel = {t}, []
        for x in groups[cat][k + 1:] + groups[cat][:k]:
            if x["title"] not in seen and len(rel) < 6:
                seen.add(x["title"])
                rel.append(x)
        related = (f'<section class="related"><h2>More from {e(cat)}</h2><ul>'
                   + "".join(f'<li><a href="{x["item"]}.html">{e(x["title"])}</a></li>' for x in rel)
                   + "</ul></section>") if rel else ""
        own = f"{SITE_URL}/item/{it}.html"
        shop = f"{STORE_SITE}/catalog/item/{it}.html" if it in store else ""
        canon = shop or own
        store_link = (f'<p class="store-link"><a href="{shop}">See it {"with its photo " if store[it] else ""}'
                      f'at stampedestamps.store</a></p>') if shop else ""
        buy = (f'<a class="btn" href="{e(r["ebay_url"])}" rel="nofollow noopener">See it on eBay</a>{store_link}'
               f'<p><a href="{STORE}">Browse everything in the StampedeUSA store</a></p>')
        crumbs_nav = (f'<nav class="crumbs" aria-label="Breadcrumb"><a href="../index.html">{SITE_NAME}</a> / '
                      f'<a href="../index.html#{slug(cat)}">{e(cat)}</a></nav>')
        script = ""
        if st and st["sources"] and st["headline"]:
            # The story layout: the stamp (cancelled) beside the story, written up like an album page.
            hl = st["headline"]
            share = (f'https://www.facebook.com/sharer/sharer.php?u={quote(own, safe="")}',
                     f'https://www.pinterest.com/pin/create/button/?url={quote(own, safe="")}'
                     f'&description={quote(hl, safe="")}' + (f'&media={quote(img, safe="")}' if img else ""),
                     f'mailto:?subject={quote(hl)}&body={quote((st["hook"] + " " if st["hook"] else "") + own)}')
            fact = (f'<aside class="fact" aria-labelledby="fact-h"><h2 id="fact-h">Did you know?</h2>'
                    f'<p>{e(st["fact"])}</p></aside>') if st["fact"] else ""
            body = (crumbs_nav + '<article class="story">'
                    f'<div class="story-stamp">{stamp_html(r, img, "big", lazy=False)}{postmark(today, "item")}</div>'
                    f'<div class="story-body"><h1 class="headline">{e(hl)}</h1>'
                    f'<p class="listing-title">{e(t)}</p><p class="facts">{"".join(facts)}</p>'
                    + (f'<p class="standfirst">{e(st["hook"])}</p>' if st["hook"] else "")
                    + f'<div class="story-text"><p>{e(st["story"])}</p></div>{fact}{sources_html(st["sources"])}'
                    f'{buy}<p class="share">Share this story: <a href="{e(share[0])}" rel="noopener">Facebook</a> '
                    f'<a href="{e(share[1])}" rel="noopener">Pinterest</a> <a href="{e(share[2])}">Email</a> '
                    f'<button type="button" id="copy" data-url="{e(own)}" hidden>Copy the link</button></p>'
                    f'</div></article>{more_stories(it, "")}{related}')
            script = ("<script>(function(){var b=document.getElementById('copy');if(!b||!navigator.clipboard)return;"
                      "b.hidden=false;b.addEventListener('click',function(){navigator.clipboard.writeText("
                      "b.getAttribute('data-url')).then(function(){b.textContent='Link copied';});});})();</script>"
                      + POSTMARK_JS)
            title = f"{hl}: {t}{nth} | {SITE_NAME}"
            desc = clip(f"{hl}. {st['hook']} {st['story']}")
            main_class = "story-page"
        else:
            if img:
                stamp = (f'<figure class="perf edged item-stamp"><div class="frame"><img src="{e(img)}" alt="{e(t)}">'
                         f'</div></figure><h1 class="photo-title">{e(t)}</h1>')
            else:  # no photo: the title itself is printed as the stamp's design
                stamp = f'<div class="perf edged item-stamp"><div class="frame"><h1>{e(t)}</h1></div></div>'
            text = f'<p class="text">{e(st["story"] if st else blurbs[it])}</p>'
            if st:
                text += sources_html(st["sources"])
            body = crumbs_nav + f'{stamp}<p class="facts">{"".join(facts)}</p>{text}{buy}{more_stories(it, "")}{related}'
            title = f"{t}{nth} | {SITE_NAME}"
            desc = clip(f"{t}{nth}. {text_of[it]}")
            main_class = "narrow"
        product = {"@context": "https://schema.org", "@type": "Product", "name": t, "url": canon, "category": cat,
                   "description": text_of[it], "brand": {"@type": "Brand", "name": "StampedeUSA"}}
        if img:
            product["image"] = img
        crumbs = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": SITE_NAME, "item": f"{SITE_URL}/index.html"},
            {"@type": "ListItem", "position": 2, "name": cat, "item": f"{SITE_URL}/index.html#{slug(cat)}"},
            {"@type": "ListItem", "position": 3, "name": t, "item": own}]}
        (out / "item" / f"{it}.html").write_text(
            page(title, desc, body + script, canon, 1, image=img, extra_head=jsonld(crumbs) + jsonld(product),
                 main_class=main_class), encoding="utf-8")

    # ---- home page
    def row_html(r):
        twins = same_title[r["title"]]
        img = imgs.get(r["item"])
        thumb = f'<img src="{e(img)}" alt="" width="64" height="64" loading="lazy" decoding="async">' if img else ""
        sub = [fmt_name(r)] if fmt_name(r) else []
        if any(x["item"] in stories and stories[x["item"]]["sources"] for x in twins):
            sub.append('<span class="story-mark">Has a story</span>')
        if len(twins) > 1:
            sub.append("Separate listings: " + ", ".join(
                f'<a href="item/{x["item"]}.html">Listing {i}</a>' for i, x in enumerate(twins, 1)))
        search = " ".join(filter(None, [r["title"], category(r), fmt_name(r)]))
        return (f'<li class="row" data-n="{len(twins)}" data-s="{e(search)}">{thumb}<span>'
                f'<a class="tt" href="item/{r["item"]}.html">{e(r["title"])}</a>'
                + (f'<span class="sub">{"; ".join(sub)}</span>' if sub else "") + "</span></li>")

    secs = []
    for cat in cats:
        firsts = [r for r in groups[cat] if same_title[r["title"]][0] is r]
        if len(groups[cat]) >= DECADE_MIN:
            dec = defaultdict(list)
            for r in firsts:
                y = title_year(r["title"])
                dec[y // 10 * 10 if y else None].append(r)
            inner = '<p class="note">Grouped by the first year each title mentions.</p>' + "".join(
                f'<div class="decade"><h3>{f"{d}s" if d is not None else "Year not in the title"}</h3>'
                f'<ul class="rows">{"".join(row_html(r) for r in dec[d])}</ul></div>'
                for d in sorted(dec, key=lambda d: (d is None, d or 0)))
        else:
            inner = '<ul class="rows">' + "".join(row_html(r) for r in firsts) + "</ul>"
        secs.append(f'<section class="cat" id="{slug(cat)}" data-cat="{e(cat)}">'
                    f"<h2>{e(cat)} ({len(groups[cat])})</h2>{inner}</section>")

    # Category pane: the biggest categories as stamps on a purple sheet margin, plus one stamp for all the rest.
    top = cats[:8] if len(cats) > 9 else cats
    tiles = [f'<li><a class="tile perf" href="#{slug(c)}"><b>{e(c)}</b><span>{len(groups[c])} listed</span></a></li>'
             for c in top]
    if len(cats) > len(top):
        rest = cats[len(top):]
        tiles.append(f'<li class="rest"><a class="tile perf" href="#{slug(rest[0])}"><b>{len(rest)} more categories</b>'
                     f"<span>{sum(len(groups[c]) for c in rest)} listed, {e(rest[0])} to {e(rest[-1])}</span></a></li>")

    # Today's story: the sourced stories take turns on the cover, one a day. The rest fill "Stories worth a read".
    cover_r = told[today.toordinal() % len(told)] if told else None
    feat = [r for r in told if r is not cover_r][:8]
    fresh = not feat
    if fresh:  # nothing (else) to feature yet: the newest listing from each of the biggest categories
        feat = [groups[c][0] for c in cats[:6] if groups[c][0] is not cover_r]

    def story_card(r):
        it = r["item"]
        st = stories.get(it) if not fresh else None
        hook = f'<span class="k">{e(st["hook"])}</span>' if st and st["hook"] else ""
        head = headline.get(it, r["title"]) if not fresh else r["title"]
        return (f'<li class="story-card"><a href="item/{it}.html">{stamp_html(r, imgs.get(it))}'
                f'<span class="h">{e(head)}</span>{hook}<span class="c">{e(category(r))}</span></a></li>')

    featured = (f'<section class="featured" id="featured"><h2 id="stories">'
                f'{"Fresh from the shelf" if fresh else "Stories worth a read"}</h2>'
                f'<ul class="stories">{"".join(story_card(r) for r in feat)}</ul></section>') if feat else ""
    cover = ""
    if cover_r:
        cs = stories[cover_r["item"]]
        cover = (f'<article class="cover" aria-labelledby="cover-h"><p class="from">Stamp Stories<br>StampedeUSA</p>'
                 f'<div class="corner">{stamp_html(cover_r, imgs.get(cover_r["item"]), "small", lazy=False)}'
                 f'{postmark(today, "cover")}</div><div class="to"><p class="label">Today&#8217;s story</p>'
                 f'<h2 id="cover-h">{e(headline[cover_r["item"]])}</h2>'
                 + (f'<p class="hook">{e(cs["hook"])}</p>' if cs["hook"] else "")
                 + f'<a class="btn small" href="item/{cover_r["item"]}.html">Read the story</a></div></article>')
    n = len(rows)
    js = """<script>
(function(){var q=document.getElementById('q'),cnt=document.getElementById('count'),em=document.getElementById('empty'),
ew=document.getElementById('empty-q'),ft=document.getElementById('featured'),total=%d;
var rows=[].slice.call(document.querySelectorAll('.row')).map(function(r){return [r,r.getAttribute('data-s').toLowerCase(),+r.getAttribute('data-n')];});
var groups=[].slice.call(document.querySelectorAll('.decade,.cat'));
function run(push){var raw=q.value.trim(),w=raw.toLowerCase().split(/\\s+/).filter(Boolean),n=0;
rows.forEach(function(x){var ok=w.every(function(t){return x[1].indexOf(t)>-1;});x[0].hidden=!ok;if(ok)n+=x[2];});
groups.forEach(function(g){g.hidden=!g.querySelector('.row:not([hidden])');});
if(ft)ft.hidden=!!raw;cnt.textContent=raw?(n===1?'1 listing matches':n+' listings match'):'Showing all '+total+' listings';
em.hidden=!!n;ew.textContent=raw;
if(push&&history.replaceState)history.replaceState(null,'',raw?'?q='+encodeURIComponent(raw):location.pathname);}
q.addEventListener('input',function(){run(true);});
document.getElementById('clear').addEventListener('click',function(){q.value='';run(true);q.focus();});
window.addEventListener('pageshow',function(){if(!q.value){var m=/[?&]q=([^&]*)/.exec(location.search);
if(m)q.value=decodeURIComponent(m[1].replace(/\\+/g,' '));}run(false);});})();
</script>""" % n
    jump = (f'<p class="jump"><a href="#stories">{"See what is new" if fresh else "Read more stories"}</a>'
            f'<a href="#shelf">Browse all {n} listings</a><a href="{CATALOG}">See them all with photos</a></p>')
    body = (f'<section class="hero{" with-cover" if cover else ""}"><div class="intro"><h1>Every stamp has a story.</h1>'
            '<p class="lede">Who is on the stamp, what happened, and why collectors still grin about it. Read a story, '
            f"then see the stamp itself on eBay. {n} listings are on the StampedeUSA shelf today.</p>{jump}</div>"
            f"{cover}</section>{featured}"
            '<div class="find" id="shelf" role="search"><label for="q">Search the shelf</label>'
            '<input type="search" id="q" autocomplete="off" placeholder="Try Batman, eagle, Boston or 1962">'
            f'<p class="count" id="count" aria-live="polite">Showing all {n} listings</p>'
            '<div class="empty" id="empty" hidden><p>Nothing on the shelf matches "<span id="empty-q"></span>" yet.</p>'
            "<p>Try one word, a Scott number like 3099, or a year. "
            '<button type="button" id="clear">Clear the search</button> to see everything, or '
            f'<a href="{STORE}">browse the whole StampedeUSA store on eBay</a>.</p></div></div>'
            f'<nav aria-label="Categories"><ul class="pane">{"".join(tiles)}'
            '<li class="inscription" aria-hidden="true">Mail early in the day</li></ul></nav>'
            + "".join(secs) + js + (POSTMARK_JS if cover else ""))
    site_ld = {"@context": "https://schema.org", "@type": "WebSite", "name": SITE_NAME, "url": f"{SITE_URL}/index.html",
               "publisher": {"@type": "Organization", "name": "StampedeUSA"},
               "potentialAction": {"@type": "SearchAction", "target": f"{SITE_URL}/index.html?q={{search_term_string}}",
                                   "query-input": "required name=search_term_string"}}
    org_ld = {"@context": "https://schema.org", "@type": "Organization", "name": "StampedeUSA", "url": STORE,
              "logo": f"{SITE_URL}/{OG_DEFAULT}", "sameAs": [STORE]}
    (out / "index.html").write_text(
        page(f"{SITE_NAME} | StampedeUSA",
             f"The stories behind {n} U.S. stamps, sheets, covers and postal history on the StampedeUSA shelf, "
             "one page per eBay listing.",
             body, f"{SITE_URL}/index.html", extra_head=jsonld(site_ld) + jsonld(org_ld), catalog_link=True),
        encoding="utf-8")

    # ---- feed, sitemap, robots, 404
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    items = []
    for r in rows:
        link = f"{SITE_URL}/item/{r['item']}.html"
        enc = f'<enclosure url="{e(imgs[r["item"]])}" type="image/jpeg" length="0"/>' if r["item"] in imgs else ""
        items.append(f"<item><title>{e(r['title'])}</title><link>{link}</link><guid isPermaLink=\"true\">{link}</guid>"
                     f"<category>{e(category(r))}</category><description>{e(text_of[r['item']])}</description>{enc}</item>")
    (out / "feed.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel>'
        f"<title>{SITE_NAME}</title><link>{SITE_URL}/index.html</link>"
        f'<atom:link href="{SITE_URL}/feed.xml" rel="self" type="application/rss+xml"/>'
        f"<description>Stamps and postal history from StampedeUSA. {SIGN}</description>"
        f"<language>en-us</language><lastBuildDate>{now}</lastBuildDate>"
        f"<image><url>{SITE_URL}/{OG_DEFAULT}</url><title>{SITE_NAME}</title><link>{SITE_URL}/index.html</link></image>"
        + "".join(items) + "</channel></rss>\n", encoding="utf-8")
    # Only canonical pages belong in a sitemap: an item page that names its store page as canonical is left out.
    urls = [f"{SITE_URL}/index.html"] + [f"{SITE_URL}/item/{r['item']}.html" for r in rows if r["item"] not in store]
    (out / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + "".join(f"<url><loc>{u}</loc><lastmod>{lastmod}</lastmod></url>" for u in urls) + "</urlset>\n",
        encoding="utf-8")
    (out / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8")
    # GitHub Pages serves 404.html at whatever path was asked for, so its links are absolute.
    nf = ('<div class="perf edged item-stamp"><div class="frame"><h1>This stamp story has wrapped up</h1></div></div>'
          '<p class="text">That listing has ended, or the link took a wrong turn at the post office. '
          "Plenty more stamps and covers are on the shelf.</p>"
          f'<a class="btn" href="{STORE}">Visit the StampedeUSA eBay store</a>'
          f'<p><a href="{SITE_URL}/index.html">See all {n} stamp stories</a></p>')
    (out / "404.html").write_text(
        page(f"Page not found | {SITE_NAME}", "That page has moved on. Browse stamps and postal history from StampedeUSA.",
             nf, f"{SITE_URL}/404.html", base=SITE_URL, main_class="narrow", noindex=True), encoding="utf-8")
    (out / ".nojekyll").write_text("")
    print(f"built {len(rows)} item pages ({len(told)} sourced stories, photos {len(imgs)}) -> {out}")


if __name__ == "__main__":
    # Only the real build reads the live store; tests call main() with their own `store` and stay offline.
    main(sys.argv[1] if len(sys.argv) > 1 else ROOT / "site", store=store_pages(),
         photos=store_photos() if STORE_PHOTOS else None)
