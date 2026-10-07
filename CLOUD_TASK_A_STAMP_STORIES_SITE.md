# CLOUD TASK A: Stamp Stories site (NO-COST ADVERTISING)

Staged on OMEN, Tue 2026-10-06, by a local session. Douglas's rulings, 2026-10-06 ~9 PM ET:
lanes A -> B -> C; a PUBLIC repo for the site only; cloud sessions on Sonnet; no cloud start below $20 of credit.

**You are a claude.ai/code cloud session paid by the one-time cloud-session credit. HARD STOP: 2 hours of wall clock
or the end of STEP 5, whichever comes first.** If you hit the stop, commit what you have, write
`results/BLOCKED_A_<yyyy-mm-dd>.md` (machine/environment, last step reached, what stopped you), push, open the PR, end.

## What this is
A free, public, static website on GitHub Pages: one page per active StampedeUSA eBay listing, plus index pages, an RSS
feed (Pinterest can auto-pin from it) and a sitemap (for Google). Every page sends the visitor to the eBay listing. After
this build, **no model runs again**: a GitHub Actions workflow rebuilds the site whenever OMEN pushes a fresh
`data/listings.csv`.

## Hard rules
1. **No prices. Ever.** `data/listings.csv` has no price columns on purpose (PRICE GUARD rule). Dollar amounts inside
   titles (e.g. "$5 Charter Party", "$11.75 Hologram") are stamp FACE VALUES. Keep them as part of the title and never call
   them a price, a value or a deal.
2. **No invented facts.** Blurbs may state only what the title, category and condition fields state. You have no Scott
   catalog here, so never assert a year, printing, variety, rarity or history the title doesn't already say. Warmth,
   invitation and brand voice are fine; claims are not.
3. **Voice:** positive, upbeat, light, a little humorous. Royal purple `#4B006E` is the brand color. Sign-off line on
   every page: "- StampedeUSA". Store link: https://www.ebay.com/str/stampedeusa (if STEP 0 finds a different store URL
   on a listing page, use that one and say so in the report).
4. **No Claude, API key or paid service in the workflow.** Standard library Python only for the build. GitHub Pages
   plus Actions only.
5. Never commit anything beyond public listing data and generated pages: no buyer data, costs or secrets.

## STEP 0: probe (stop if it fails)
- `data/listings.csv` exists and has 427 rows plus a header, with columns item,title,category,condition,format,ebay_url.
  On a mismatch, write BLOCKED_ and stop.
- Fetch ONE listing page (the first row's ebay_url) and look for its `og:image`. Record the HTTP status. If it's 200 with an
  image, photos are IN. Otherwise photos are OUT for this run (text-only cards), and that is NOT a blocker. Say which in
  the report.

## STEP 1: images (only if STEP 0 said IN)
Fetch each listing's `og:image` URL, politely: about one request a second, stop on the first 429 or 403. Write
`data/images.csv` (item,image_url). Hotlink the eBay image URL; do not download images into the repo. Missing rows get
text-only cards.

## STEP 2: blurbs
Write `data/blurbs.csv` (item,blurb): 1-2 sentences per listing, rules 1-3, all 427. Keep a self-check: no
"$" in a blurb unless it is copied verbatim from that item's title.

## STEP 3: the build
`build.py` (stdlib) reads data/*.csv -> `site/`:
- `index.html`: grouped by category, with a search box (plain JS, no library)
- `item/<item>.html`: one per listing (title, category, condition, blurb, photo if any, a big "See it on eBay" button)
- `feed.xml` (RSS 2.0, newest item numbers first; image in an enclosure when present), `sitemap.xml`, `robots.txt`
- mobile-first, no external fonts or trackers
`tests/test_build.py`: build into a temp dir and assert 427 item pages, no price pattern outside titles, and that every
item page links to its ebay_url.

## STEP 4: the deterministic refresh
`.github/workflows/pages.yml`: on push to main touching `data/**` or build files, plus manual dispatch: run the tests,
run build.py, deploy with actions/upload-pages-artifact + actions/deploy-pages. No secrets needed.
Do NOT enable Pages yourself; Douglas turns it on after he reviews the PR.

## STEP 5: report and PR
`results/REPORT_A_<yyyy-mm-dd>.md`: photos IN/OUT and why, row counts per file, test output, anything skipped, and
three sample item pages quoted in full. Branch `stamp-stories-site-2026-10`; open a PR to main. End.
