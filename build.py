#!/usr/bin/env python3
"""Stamp Stories static site builder (stdlib only). Usage: build.py [outdir]"""
import csv, datetime, html, json, os, re, shutil, sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent / "tools"))
from make_blurbs import blurb, category, check as check_blurb  # blurbs are written fresh on every build

ROOT = Path(__file__).resolve().parent
SITE_URL = os.environ.get("SITE_URL", "https://stampedestamps.github.io/stampede-stories").rstrip("/")
STORE = "https://www.ebay.com/str/stampedeusa"
PURPLE = "#4B006E"
SIGN = "- StampedeUSA"
SITE_NAME = "Stamp Stories"
OG_DEFAULT = "assets/og-stamp-stories.png"  # 1200x630, made once by tools/make_og_image.js, never at build time
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


def page(title, desc, body, canon, depth=0, base=None, image=None, extra_head="", narrow=False, noindex=False):
    pre = f"{base}/" if base else "../" * depth
    img = image or f"{SITE_URL}/{OG_DEFAULT}"
    robots = '\n<meta name="robots" content="noindex">' if noindex else ""
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
<link rel="icon" href="{pre}assets/favicon.svg" type="image/svg+xml">
<link rel="preload" href="{pre}{FONT}" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{pre}assets/site.css">
<link rel="alternate" type="application/rss+xml" title="{SITE_NAME}" href="{pre}feed.xml">{extra_head}
</head><body>
<a class="skip" href="#main">Skip to the stamps</a>
<header class="selvage"><div class="top"><a class="mark" href="{pre}index.html">{SITE_NAME}<small>by StampedeUSA</small></a>
<a class="store" href="{STORE}">Visit the eBay store</a></div></header>
<main id="main"{' class="narrow"' if narrow else ""}>{body}</main>
<footer class="selvage"><div class="foot"><p class="sign">{SIGN}</p>
<p><a href="{STORE}">Visit the StampedeUSA store on eBay</a></p><p><a href="{pre}feed.xml">New listings by RSS</a></p></div></footer>
</body></html>
"""


def load_stories(data, rows):
    """data/stories.csv is used for an item only while it is listed AND its title still equals title_at_writing;
    otherwise the page falls back to the generated blurb."""
    if not (Path(data) / "stories.csv").exists():
        return {}
    titles = {r["item"]: r["title"] for r in rows}
    out = {}
    for s in read(data, "stories.csv"):
        it = (s.get("item") or "").strip()
        story = (s.get("story") or "").strip()
        if it in titles and story and s.get("title_at_writing") == titles[it]:
            check_blurb({"item": it, "title": titles[it]}, story)
            src = (s.get("source_url") or "").strip()
            out[it] = (story, src if src.startswith("https://") else "")
    return out


def main(out, data=None):
    data = Path(data) if data else ROOT / "data"
    out = Path(out)
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
    text_of = {it: (stories[it][0] if it in stories else blurbs[it]) for it in blurbs}
    imgs = {}
    if (data / "images.csv").exists():
        imgs = {r["item"]: r["image_url"].strip() for r in read(data, "images.csv")
                if (r.get("image_url") or "").strip().startswith("https://")}
    rows.sort(key=lambda r: int(r["item"]), reverse=True)
    lastmod = os.environ.get("SITE_LASTMOD") or datetime.datetime.now(datetime.timezone.utc).date().isoformat()

    groups = defaultdict(list)
    for r in rows:
        groups[category(r)].append(r)
    cats = sorted(groups, key=lambda c: (-len(groups[c]), c))
    same_title = defaultdict(list)  # identical titles: shown once on the home page, with each listing linked
    for r in rows:
        same_title[r["title"]].append(r)

    # ---- item pages
    for r in rows:
        it, t, cat = r["item"], r["title"], category(r)
        twins = same_title[t]
        nth = f" (listing {twins.index(r) + 1} of {len(twins)})" if len(twins) > 1 else ""
        img = imgs.get(it)
        if img:
            stamp = (f'<figure class="perf edged item-stamp"><div class="frame"><img src="{e(img)}" alt="{e(t)}">'
                     f'</div></figure><h1 class="photo-title">{e(t)}</h1>')
        else:  # no photo: the title itself is printed as the stamp's design
            stamp = f'<div class="perf edged item-stamp"><div class="frame"><h1>{e(t)}</h1></div></div>'
        facts = [f"<span>Category: {e(cat)}</span>"]
        if fmt_name(r):
            facts.append(f"<span>Format: {fmt_name(r)}</span>")
        if (r.get("condition") or "").strip():
            facts.append(f"<span>Condition: {e(r['condition'].strip())}</span>")
        if it in stories:
            story, src = stories[it]
            text = f'<p class="text">{e(story)}</p>'
            if src:
                host = urlparse(src).netloc.removeprefix("www.")
                text += f'<p class="source">Background on the subject: <a href="{e(src)}" rel="noopener">{e(host)}</a></p>'
        else:
            text = f'<p class="text">{e(blurbs[it])}</p>'
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
        body = (f'<nav class="crumbs" aria-label="Breadcrumb"><a href="../index.html">{SITE_NAME}</a> / '
                f'<a href="../index.html#{slug(cat)}">{e(cat)}</a></nav>'
                f'{stamp}<p class="facts">{"".join(facts)}</p>{text}'
                f'<a class="btn" href="{e(r["ebay_url"])}" rel="nofollow noopener">See it on eBay</a>'
                f'<p><a href="{STORE}">Browse everything in the StampedeUSA store</a></p>{related}')
        canon = f"{SITE_URL}/item/{it}.html"
        product = {"@context": "https://schema.org", "@type": "Product", "name": t, "url": canon, "category": cat,
                   "description": text_of[it], "brand": {"@type": "Brand", "name": "StampedeUSA"}}
        if img:
            product["image"] = img
        crumbs = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": SITE_NAME, "item": f"{SITE_URL}/index.html"},
            {"@type": "ListItem", "position": 2, "name": cat, "item": f"{SITE_URL}/index.html#{slug(cat)}"},
            {"@type": "ListItem", "position": 3, "name": t, "item": canon}]}
        (out / "item" / f"{it}.html").write_text(
            page(f"{t}{nth} | {SITE_NAME}", clip(f"{t}{nth}. {text_of[it]}"), body, canon, 1, image=img,
                 extra_head=jsonld(crumbs) + jsonld(product), narrow=True), encoding="utf-8")

    # ---- home page
    def row_html(r):
        twins = same_title[r["title"]]
        img = imgs.get(r["item"])
        thumb = f'<img src="{e(img)}" alt="" width="64" height="64" loading="lazy" decoding="async">' if img else ""
        sub = [fmt_name(r)] if fmt_name(r) else []
        if any(x["item"] in stories for x in twins):
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

    # Hero pane: the biggest categories as stamps, plus one stamp for all the rest.
    top = cats[:8] if len(cats) > 9 else cats
    tiles = [f'<li><a class="tile perf" href="#{slug(c)}"><b>{e(c)}</b><span>{len(groups[c])} listed</span></a></li>'
             for c in top]
    if len(cats) > len(top):
        rest = cats[len(top):]
        tiles.append(f'<li class="rest"><a class="tile perf" href="#{slug(rest[0])}"><b>{len(rest)} more categories</b>'
                     f"<span>{sum(len(groups[c]) for c in rest)} listed, {e(rest[0])} to {e(rest[-1])}</span></a></li>")

    # Featured: listings with a story, one per category in turn (biggest category first), up to 6.
    pool = [[r for r in groups[c] if r["item"] in stories and same_title[r["title"]][0] is r] for c in cats]
    if not any(pool):
        pool = [groups[c][:1] for c in cats]
    feat = []
    while len(feat) < 6 and any(pool):
        for p in pool:
            if p and len(feat) < 6:
                feat.append(p.pop(0))

    def stamp_card(r):
        img = imgs.get(r["item"])
        pic = f'<img src="{e(img)}" alt="" loading="lazy" decoding="async">' if img else ""
        return (f'<li class="edged"><a class="perf" href="item/{r["item"]}.html">{pic}'
                f'<span class="t">{e(r["title"])}</span><span class="c">{e(category(r))}</span></a></li>')

    featured = (f'<section class="featured" id="featured"><h2>{"Stories worth a read" if stories else "Fresh from the shelf"}</h2>'
                f'<ul class="stamps">{"".join(stamp_card(r) for r in feat)}</ul></section>') if feat else ""
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
    body = (f'<section class="hero"><h1>Every stamp has a story.</h1>'
            f'<p class="lede">{n} of them are on the StampedeUSA shelf right now: U.S. sheets and panes, singles, '
            "covers, revenues and a few travelers from abroad. Pick a category, or search for something you love.</p>"
            f'<nav aria-label="Categories"><ul class="pane">{"".join(tiles)}'
            '<li class="inscription" aria-hidden="true">Mail early in the day</li></ul></nav></section>'
            '<div class="find" role="search"><label for="q">Search the shelf</label>'
            '<input type="search" id="q" autocomplete="off" placeholder="Try Batman, eagle, Boston or 1962">'
            f'<p class="count" id="count" aria-live="polite">Showing all {n} listings</p>'
            '<div class="empty" id="empty" hidden><p>Nothing on the shelf matches "<span id="empty-q"></span>" yet.</p>'
            "<p>Try one word, a Scott number like 3099, or a year. "
            '<button type="button" id="clear">Clear the search</button> to see everything, or '
            f'<a href="{STORE}">browse the whole StampedeUSA store on eBay</a>.</p></div></div>'
            + featured + "".join(secs) + js)
    site_ld = {"@context": "https://schema.org", "@type": "WebSite", "name": SITE_NAME, "url": f"{SITE_URL}/index.html",
               "publisher": {"@type": "Organization", "name": "StampedeUSA"},
               "potentialAction": {"@type": "SearchAction", "target": f"{SITE_URL}/index.html?q={{search_term_string}}",
                                   "query-input": "required name=search_term_string"}}
    org_ld = {"@context": "https://schema.org", "@type": "Organization", "name": "StampedeUSA", "url": STORE,
              "logo": f"{SITE_URL}/{OG_DEFAULT}", "sameAs": [STORE]}
    (out / "index.html").write_text(
        page(f"{SITE_NAME} | StampedeUSA",
             f"Browse {n} U.S. stamps, sheets, covers and postal history from StampedeUSA, one page per eBay listing.",
             body, f"{SITE_URL}/index.html", extra_head=jsonld(site_ld) + jsonld(org_ld)), encoding="utf-8")

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
    urls = [f"{SITE_URL}/index.html"] + [f"{SITE_URL}/item/{r['item']}.html" for r in rows]
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
             nf, f"{SITE_URL}/404.html", base=SITE_URL, narrow=True, noindex=True), encoding="utf-8")
    (out / ".nojekyll").write_text("")
    print(f"built {len(rows)} item pages -> {out}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ROOT / "site")
