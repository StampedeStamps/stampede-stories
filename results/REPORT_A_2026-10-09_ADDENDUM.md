# REPORT A addendum, Fri 2026-10-09 (ET)

## What happened since the 2026-10-08 addendum
- PR #1 (branch `stamp-stories-site-2026-10`, tip e5573c4) was merged into `main` on Fri 2026-10-09 1:38 PM ET.
- The first Pages run on the merge commit failed: `test_blurbs_have_no_price` raised KeyError '168756442288'
  (that listing ended in the 2026-10-09 refresh but its row was still in `data/blurbs.csv`). Commit d934503
  (1:39 PM ET) relaxed the test and the second run deployed the site.
- A four-lens review with adversarial verification (hard rules, refresh robustness, site quality, Windows) then
  found real problems in what went live. This branch fixes them.

## Fixes in this branch (on top of d934503)
1. Hard rule 2 (no invented facts): the "Listed under Scott #..." sentence is removed. It cut titles such as
   "Scott #RB32/RB44 ..." to "Scott #RB32" and named only the first number of multi-stamp lots (about 45 pages).
   The heading already shows the title's Scott numbers verbatim. (This sentence was added on 2026-10-08 to make
   blurbs less repetitive; wording variety now does that job: 422 distinct blurbs of 427.)
2. Tag wording follows the title: "perfin" for a single Perfin, and "Flat Plate" no longer yields a "plate" tag.
3. Blurbs are built fresh from the current listing on every build, so ended, new, retitled or recategorized
   listings can never carry a stale blurb (the 2026-10-08 fix covered new listings only).
4. CSV reads accept a UTF-8 byte-order mark (files saved on Windows).
5. The workflow also rebuilds when `tools/**` changes (build.py imports tools/make_blurbs.py).
6. Site: dark-mode headings were dark purple on near-black (now light lilac, about 10:1 contrast); search no
   longer matches the item counts in headings; the filter is re-applied after the Back button; a 404 page
   points visitors back to the index and the eBay store.
7. `tools/make_blurbs.py` works from any folder.
8. A blank category reads "Other" everywhere (blurb, Category line, index heading), and a format other than
   AUCTION / FIXED_PRICE gets no auction or buy-now wording at all instead of a guess.
9. The "listed in <category>" wording is replaced ("part of our <category> selection"), because for categories
   such as Victoria or Ukraine it read like a location.

## Checks run (cloud session, Fri 2026-10-09)
- `python3 -m unittest discover -s tests`: 12 tests, OK (Python 3.13; CI uses 3.12). The new tests fail on
  d934503, so they catch the problems above.
- Two rounds of independent review with adversarial verification (hard rules read against all 427 rows,
  regressions, refresh robustness with BOM/CRLF/blank/odd-format/duplicate data, Windows). Every confirmed
  finding is fixed here; findings the verifiers could not reproduce were dropped.
- Built with the current `main` listings (427): 427 item pages plus index, 404, feed, sitemap, robots;
  0 HTML tag mismatches; feed.xml and sitemap.xml are well-formed XML; no "Listed under Scott" anywhere.
- Headless Chromium: search shows 427 by default, "hologram" 4, "178" 2 (the two titles containing 178),
  "revenues" 73, "zzzz" 0; after Back the box keeps "hologram" with 4 shown; dark h2 rgb(217,179,238),
  light h2 rgb(75,0,110).
- Not checkable from the cloud: the live site (github.io is blocked from this container) and eBay pages.

## Three sample item pages, quoted in full (as built from this branch)

### item/168402100776.html
```html
<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Scott #RB32/RB44 &amp; RB34/RB46 1914 1/8c 3/8c Proprietary Lot of 2 Wmk Undeterm | Stamp Stories</title><meta name="description" content="Part of the StampedeUSA herd: on the Revenues shelf, available to buy now. It&#x27;s waiting for you on eBay.">
<meta name="theme-color" content="#4B006E"><link rel="canonical" href="https://stampedestamps.github.io/stampede-stories/item/168402100776.html">
<link rel="alternate" type="application/rss+xml" title="Stamp Stories" href="../feed.xml">
<style>
:root{--p:#4B006E;--bg:#fff;--fg:#222;--soft:#f4ecf8}
@media(prefers-color-scheme:dark){:root{--bg:#16101a;--fg:#eee;--soft:#2a1f33}}
*{box-sizing:border-box}body{margin:0;font:16px/1.5 system-ui,sans-serif;background:var(--bg);color:var(--fg)}
header{background:var(--p);color:#fff;padding:1rem}header a{color:#fff;text-decoration:none;font-weight:700;font-size:1.3rem}
header p{margin:.2rem 0 0;opacity:.9}main{max-width:46rem;margin:0 auto;padding:1rem}
h1{color:var(--p);font-size:1.4rem}
h2{color:var(--p);border-bottom:2px solid var(--soft);padding-bottom:.2rem}@media(prefers-color-scheme:dark){h1,h2{color:#d9b3ee}}
.btn{display:block;text-align:center;background:var(--p);color:#fff;padding:.9rem 1rem;border-radius:.6rem;
text-decoration:none;font-weight:700;font-size:1.15rem;margin:1.2rem 0}
.card{background:var(--soft);border-radius:.6rem;padding:.8rem;margin:.6rem 0}
.card img,.photo{max-width:100%;height:auto;border-radius:.4rem}
ul.items{list-style:none;padding:0}ul.items li{padding:.35rem 0;border-bottom:1px solid var(--soft)}
a{color:var(--p)}@media(prefers-color-scheme:dark){a{color:#d9b3ee}}
input[type=search]{width:100%;padding:.7rem;font-size:1rem;border:2px solid var(--p);border-radius:.5rem;margin:.5rem 0}
footer{text-align:center;padding:1.5rem;opacity:.8}.meta{opacity:.8;font-size:.95rem}
</style></head><body>
<header><a href="../index.html">Stamp Stories</a><p>Stamps and postal history from StampedeUSA</p></header>
<main><h1>Scott #RB32/RB44 &amp; RB34/RB46 1914 1/8c 3/8c Proprietary Lot of 2 Wmk Undeterm</h1><p class="meta">Category: Revenues</p><p>Part of the StampedeUSA herd: on the Revenues shelf, available to buy now. It&#x27;s waiting for you on eBay.</p><a class="btn" href="https://www.ebay.com/itm/168402100776" rel="nofollow noopener">See it on eBay</a><p><a href="../index.html">&larr; All stamp stories</a></p><p>- StampedeUSA</p></main>
<footer><p>- StampedeUSA</p><p><a href="https://www.ebay.com/str/stampedeusa">Visit the StampedeUSA store on eBay</a></p></footer>
</body></html>
```

### item/168479445526.html
```html
<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Scott #3409 + #3410 + #3411 + #3412 + #3413 (MNH) Holograms Expo 2000 Lot of 5 | Stamp Stories</title><meta name="description" content="Look what turned up: found in our Sheets section, available to buy now. Noted in the title: MNH. Come see it on eBay.">
<meta name="theme-color" content="#4B006E"><link rel="canonical" href="https://stampedestamps.github.io/stampede-stories/item/168479445526.html">
<link rel="alternate" type="application/rss+xml" title="Stamp Stories" href="../feed.xml">
<style>
:root{--p:#4B006E;--bg:#fff;--fg:#222;--soft:#f4ecf8}
@media(prefers-color-scheme:dark){:root{--bg:#16101a;--fg:#eee;--soft:#2a1f33}}
*{box-sizing:border-box}body{margin:0;font:16px/1.5 system-ui,sans-serif;background:var(--bg);color:var(--fg)}
header{background:var(--p);color:#fff;padding:1rem}header a{color:#fff;text-decoration:none;font-weight:700;font-size:1.3rem}
header p{margin:.2rem 0 0;opacity:.9}main{max-width:46rem;margin:0 auto;padding:1rem}
h1{color:var(--p);font-size:1.4rem}
h2{color:var(--p);border-bottom:2px solid var(--soft);padding-bottom:.2rem}@media(prefers-color-scheme:dark){h1,h2{color:#d9b3ee}}
.btn{display:block;text-align:center;background:var(--p);color:#fff;padding:.9rem 1rem;border-radius:.6rem;
text-decoration:none;font-weight:700;font-size:1.15rem;margin:1.2rem 0}
.card{background:var(--soft);border-radius:.6rem;padding:.8rem;margin:.6rem 0}
.card img,.photo{max-width:100%;height:auto;border-radius:.4rem}
ul.items{list-style:none;padding:0}ul.items li{padding:.35rem 0;border-bottom:1px solid var(--soft)}
a{color:var(--p)}@media(prefers-color-scheme:dark){a{color:#d9b3ee}}
input[type=search]{width:100%;padding:.7rem;font-size:1rem;border:2px solid var(--p);border-radius:.5rem;margin:.5rem 0}
footer{text-align:center;padding:1.5rem;opacity:.8}.meta{opacity:.8;font-size:.95rem}
</style></head><body>
<header><a href="../index.html">Stamp Stories</a><p>Stamps and postal history from StampedeUSA</p></header>
<main><h1>Scott #3409 + #3410 + #3411 + #3412 + #3413 (MNH) Holograms Expo 2000 Lot of 5</h1><p class="meta">Category: Sheets</p><p>Look what turned up: found in our Sheets section, available to buy now. Noted in the title: MNH. Come see it on eBay.</p><a class="btn" href="https://www.ebay.com/itm/168479445526" rel="nofollow noopener">See it on eBay</a><p><a href="../index.html">&larr; All stamp stories</a></p><p>- StampedeUSA</p></main>
<footer><p>- StampedeUSA</p><p><a href="https://www.ebay.com/str/stampedeusa">Visit the StampedeUSA store on eBay</a></p></footer>
</body></html>
```

### item/168402099773.html
```html
<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Scott #RD189 US Series 1945 5c Stock Transfer Campbell Green Perfin Cancel Used | Stamp Stories</title><meta name="description" content="Here&#x27;s one with a story to tell: found in our Revenues section, available to buy now. Noted in the title: used, perfin. Come see it on eBay.">
<meta name="theme-color" content="#4B006E"><link rel="canonical" href="https://stampedestamps.github.io/stampede-stories/item/168402099773.html">
<link rel="alternate" type="application/rss+xml" title="Stamp Stories" href="../feed.xml">
<style>
:root{--p:#4B006E;--bg:#fff;--fg:#222;--soft:#f4ecf8}
@media(prefers-color-scheme:dark){:root{--bg:#16101a;--fg:#eee;--soft:#2a1f33}}
*{box-sizing:border-box}body{margin:0;font:16px/1.5 system-ui,sans-serif;background:var(--bg);color:var(--fg)}
header{background:var(--p);color:#fff;padding:1rem}header a{color:#fff;text-decoration:none;font-weight:700;font-size:1.3rem}
header p{margin:.2rem 0 0;opacity:.9}main{max-width:46rem;margin:0 auto;padding:1rem}
h1{color:var(--p);font-size:1.4rem}
h2{color:var(--p);border-bottom:2px solid var(--soft);padding-bottom:.2rem}@media(prefers-color-scheme:dark){h1,h2{color:#d9b3ee}}
.btn{display:block;text-align:center;background:var(--p);color:#fff;padding:.9rem 1rem;border-radius:.6rem;
text-decoration:none;font-weight:700;font-size:1.15rem;margin:1.2rem 0}
.card{background:var(--soft);border-radius:.6rem;padding:.8rem;margin:.6rem 0}
.card img,.photo{max-width:100%;height:auto;border-radius:.4rem}
ul.items{list-style:none;padding:0}ul.items li{padding:.35rem 0;border-bottom:1px solid var(--soft)}
a{color:var(--p)}@media(prefers-color-scheme:dark){a{color:#d9b3ee}}
input[type=search]{width:100%;padding:.7rem;font-size:1rem;border:2px solid var(--p);border-radius:.5rem;margin:.5rem 0}
footer{text-align:center;padding:1.5rem;opacity:.8}.meta{opacity:.8;font-size:.95rem}
</style></head><body>
<header><a href="../index.html">Stamp Stories</a><p>Stamps and postal history from StampedeUSA</p></header>
<main><h1>Scott #RD189 US Series 1945 5c Stock Transfer Campbell Green Perfin Cancel Used</h1><p class="meta">Category: Revenues</p><p>Here&#x27;s one with a story to tell: found in our Revenues section, available to buy now. Noted in the title: used, perfin. Come see it on eBay.</p><a class="btn" href="https://www.ebay.com/itm/168402099773" rel="nofollow noopener">See it on eBay</a><p><a href="../index.html">&larr; All stamp stories</a></p><p>- StampedeUSA</p></main>
<footer><p>- StampedeUSA</p><p><a href="https://www.ebay.com/str/stampedeusa">Visit the StampedeUSA store on eBay</a></p></footer>
</body></html>
```
