#!/usr/bin/env python3
"""Stamp Stories static site builder (stdlib only). Usage: build.py [outdir]"""
import csv, html, os, shutil, sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "tools"))
from make_blurbs import blurb, category, check as check_blurb  # blurbs are written fresh on every build

ROOT = Path(__file__).resolve().parent
SITE_URL = os.environ.get("SITE_URL", "https://stampedestamps.github.io/stampede-stories").rstrip("/")
STORE = "https://www.ebay.com/str/stampedeusa"
PURPLE = "#4B006E"
SIGN = "- StampedeUSA"
e = html.escape

CSS = f"""
:root{{--p:{PURPLE};--bg:#fff;--fg:#222;--soft:#f4ecf8}}
@media(prefers-color-scheme:dark){{:root{{--bg:#16101a;--fg:#eee;--soft:#2a1f33}}}}
*{{box-sizing:border-box}}body{{margin:0;font:16px/1.5 system-ui,sans-serif;background:var(--bg);color:var(--fg)}}
header{{background:var(--p);color:#fff;padding:1rem}}header a{{color:#fff;text-decoration:none;font-weight:700;font-size:1.3rem}}
header p{{margin:.2rem 0 0;opacity:.9}}main{{max-width:46rem;margin:0 auto;padding:1rem}}
h1{{color:var(--p);font-size:1.4rem}}
h2{{color:var(--p);border-bottom:2px solid var(--soft);padding-bottom:.2rem}}@media(prefers-color-scheme:dark){{h1,h2{{color:#d9b3ee}}}}
.btn{{display:block;text-align:center;background:var(--p);color:#fff;padding:.9rem 1rem;border-radius:.6rem;
text-decoration:none;font-weight:700;font-size:1.15rem;margin:1.2rem 0}}
.card{{background:var(--soft);border-radius:.6rem;padding:.8rem;margin:.6rem 0}}
.card img,.photo{{max-width:100%;height:auto;border-radius:.4rem}}
ul.items{{list-style:none;padding:0}}ul.items li{{padding:.35rem 0;border-bottom:1px solid var(--soft)}}
a{{color:var(--p)}}@media(prefers-color-scheme:dark){{a{{color:#d9b3ee}}}}
input[type=search]{{width:100%;padding:.7rem;font-size:1rem;border:2px solid var(--p);border-radius:.5rem;margin:.5rem 0}}
footer{{text-align:center;padding:1.5rem;opacity:.8}}.meta{{opacity:.8;font-size:.95rem}}
"""

def read(data, name):
    # utf-8-sig: a CSV saved on Windows with a byte-order mark reads the same as one without.
    with open(Path(data) / name, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def page(title, desc, body, canon, depth=0, base=None):
    pre = f"{base}/" if base else "../" * depth
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}">
<meta name="theme-color" content="{PURPLE}"><link rel="canonical" href="{e(canon)}">
<link rel="alternate" type="application/rss+xml" title="Stamp Stories" href="{pre}feed.xml">
<style>{CSS}</style></head><body>
<header><a href="{pre}index.html">Stamp Stories</a><p>Stamps and postal history from StampedeUSA</p></header>
<main>{body}</main>
<footer><p>{SIGN}</p><p><a href="{STORE}">Visit the StampedeUSA store on eBay</a></p></footer>
</body></html>
"""

def main(out, data=None):
    data = Path(data) if data else ROOT / "data"
    out = Path(out)
    if out.exists():
        shutil.rmtree(out)
    (out / "item").mkdir(parents=True)
    rows = read(data, "listings.csv")
    # Written fresh from the current title/category/format on every build, so a refresh that ends,
    # adds, retitles or recategorizes a listing can never leave a stale claim on a page.
    blurbs = {r["item"]: blurb(r) for r in rows}
    for r in rows:
        check_blurb(r, blurbs[r["item"]])
    imgs = {}
    if (data / "images.csv").exists():
        imgs = {r["item"]: r["image_url"] for r in read(data, "images.csv") if r.get("image_url")}
    rows.sort(key=lambda r: int(r["item"]), reverse=True)

    for r in rows:
        it, t = r["item"], r["title"]
        text = blurbs[it]
        img = imgs.get(it)
        photo = f'<p><img class="photo" src="{e(img)}" alt="{e(t)}" loading="lazy"></p>' if img else ""
        meta = f'<p class="meta">Category: {e(category(r))}'
        if r.get("condition"):
            meta += f' &middot; Condition: {e(r["condition"])}'
        meta += "</p>"
        body = (f"<h1>{e(t)}</h1>{photo}{meta}<p>{e(text)}</p>"
                f'<a class="btn" href="{e(r["ebay_url"])}" rel="nofollow noopener">See it on eBay</a>'
                f'<p><a href="../index.html">&larr; All stamp stories</a></p><p>{SIGN}</p>')
        (out / "item" / f"{it}.html").write_text(
            page(f"{t} | Stamp Stories", text, body, f"{SITE_URL}/item/{it}.html", 1), encoding="utf-8")

    groups = defaultdict(list)
    for r in rows:
        groups[category(r)].append(r)
    secs = []
    for cat in sorted(groups, key=lambda c: (-len(groups[c]), c)):
        li = "".join(f'<li><a href="item/{r["item"]}.html">{e(r["title"])}</a></li>'
                     for r in groups[cat])
        secs.append(f'<section class="cat" data-cat="{e(cat)}"><h2>{e(cat)} ({len(groups[cat])})</h2><ul class="items">{li}</ul></section>')
    js = """<script>
var q=document.getElementById('q');function f(){var v=q.value.toLowerCase().trim();
document.querySelectorAll('.cat').forEach(function(s){var n=0;s.querySelectorAll('li').forEach(function(l){
var ok=!v||(l.textContent+' '+s.getAttribute('data-cat')).toLowerCase().indexOf(v)>-1;l.style.display=ok?'':'none';if(ok)n++;});s.style.display=n?'':'none';});}
q.addEventListener('input',f);window.addEventListener('pageshow',f);f();
</script>"""
    body = (f"<h1>Stamp Stories</h1><p>Every stamp has a story. Browse what's on the shelf at StampedeUSA, "
            f"then hop over to eBay for the details.</p>"
            f'<a class="btn" href="{STORE}">Visit the StampedeUSA eBay store</a>'
            f'<input type="search" id="q" placeholder="Search {len(rows)} stamps and covers..." aria-label="Search">'
            + "".join(secs) + js + f"<p>{SIGN}</p>")
    (out / "index.html").write_text(
        page("Stamp Stories | StampedeUSA", "Stamps and postal history from StampedeUSA, one page per listing.",
             body, f"{SITE_URL}/index.html"), encoding="utf-8")

    items = []
    for r in rows:
        link = f"{SITE_URL}/item/{r['item']}.html"
        enc = f'<enclosure url="{e(imgs[r["item"]])}" type="image/jpeg" length="0"/>' if r["item"] in imgs else ""
        desc = e(blurbs[r["item"]])
        items.append(f"<item><title>{e(r['title'])}</title><link>{link}</link><guid isPermaLink=\"true\">{link}</guid>"
                     f"<description>{desc}</description>{enc}</item>")
    (out / "feed.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel><title>Stamp Stories</title>'
        f"<link>{SITE_URL}/index.html</link><description>Stamps and postal history from StampedeUSA. {SIGN}</description>"
        "<language>en-us</language>" + "".join(items) + "</channel></rss>\n", encoding="utf-8")
    urls = [f"{SITE_URL}/index.html"] + [f"{SITE_URL}/item/{r['item']}.html" for r in rows]
    (out / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + "".join(f"<url><loc>{u}</loc></url>" for u in urls) + "</urlset>\n", encoding="utf-8")
    (out / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8")
    # GitHub Pages serves 404.html at whatever path was asked for, so its links are absolute.
    nf = ("<h1>This stamp story has wrapped up</h1><p>That listing has ended or the link took a wrong turn. "
          "Plenty more stamps and covers are on the shelf!</p>"
          f'<a class="btn" href="{STORE}">Visit the StampedeUSA eBay store</a>'
          f'<p><a href="{SITE_URL}/index.html">&larr; All stamp stories</a></p><p>{SIGN}</p>')
    (out / "404.html").write_text(
        page("Not found | Stamp Stories", "Stamps and postal history from StampedeUSA.", nf,
             f"{SITE_URL}/index.html", base=SITE_URL), encoding="utf-8")
    (out / ".nojekyll").write_text("")
    print(f"built {len(rows)} item pages -> {out}")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ROOT / "site")
