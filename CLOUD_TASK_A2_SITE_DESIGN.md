# CLOUD TASK A2: Stamp Stories site redesign (NO-COST ADVERTISING)

Staged on OMEN, Sun 2026-10-11, by a local session. Douglas's rulings, 2026-10-11 ~2:45 PM ET: run as a claude.ai/code
cloud session on the gift credit; **Opus** for this one session; royal purple stays the signature color and everything
else is free; scope = look and layout + browsing + share previews/SEO + **stories for the first 50 listings only, for
evaluation**.

**You are a claude.ai/code cloud session paid by the one-time cloud-session credit. HARD STOP: 3 hours of wall clock
or the end of STEP 6, whichever comes first.** If you hit the stop, commit what you have, write
`results/BLOCKED_A2_<yyyy-mm-dd>.md` (environment, last step reached, what stopped you), push, open the PR, end.

## The site today
https://stampedestamps.github.io/stampede-stories/ is a free public site that sends shoppers to the StampedeUSA eBay
store. `build.py` (standard-library Python) generates every page from `data/listings.csv`. GitHub Actions rebuilds and
deploys on every push to `main`. OMEN pushes a fresh `data/listings.csv` every morning at 3:30 AM ET. **Any change
must go into `build.py` / `tools/` / static assets. A hand-edited HTML file is wiped by the next build.** The home page
is one long list of ~420 titles grouped by category. There are no photos yet: eBay has not issued API keys.

The money number this work should move: **days-to-sale** (more visitors who click through to listings that already exist).

## Your design method: the frontend-design skill
Read `.claude/skills/frontend-design/SKILL.md` in full **before STEP 1** and follow it throughout: subject first,
a written plan of 4-6 named colors, type and layout with ASCII wireframes, a review of the plan against the brief
that names what you changed and why, then build, then critique with screenshots. If that file is missing, stop
and write BLOCKED.

The brief for the skill:
- **Subject:** StampedeUSA, a small eBay shop selling U.S. stamps: mint sheets and panes, plate blocks, singles,
  covers and postal history, revenues and back-of-book.
- **Audience:** stamp collectors, plus casual visitors who arrive from Pinterest or Google search with no collecting
  vocabulary.
- **Primary job:** get the visitor to the eBay listing (or the store) for something that catches their eye.
- **Fixed:** royal purple `#4B006E` is the signature color, used where the brand must be recognized. Everything else
  (supporting colors, type, layout, hero) is your choice under the skill. Brand voice is positive, upbeat, light and
  a little humorous. Every page keeps the sign-off line "- StampedeUSA" and a link to https://www.ebay.com/str/stampedeusa.
- **Quality floor:** mobile-first, light and dark themes, visible keyboard focus, reduced motion respected,
  WCAG AA contrast.

## Hard rules
1. **No prices. Ever.** Dollar amounts inside titles are face values. Keep them as part of the title. Never call them
   a price, a value or a deal. The existing tests enforce this, so keep them passing.
2. **No invented facts about the stamp itself.** Only the title, category, condition and format fields may be
   asserted about an item. Never assert a year, designer, printing, perforation, variety, rarity, value or condition
   the title does not state. (STEP 4 allows sourced history about a story's *subject* for 50 items, and nothing else.)
3. **No external fonts, trackers, analytics or CDNs.** Self-host any font as `woff2` files committed under
   `assets/fonts/` together with its license (SIL OFL or similar), or use system fonts. Plain JavaScript only.
4. **No Claude, API key or paid service in the workflow.** Standard-library Python for the build. GitHub Pages + Actions only.
5. Commit only public listing data, code, static assets and generated reports. No buyer data, costs or secrets.
6. Do not edit `data/listings.csv`, `.claude/`, or anything the 3:30 AM refresh writes. In
   `.github/workflows/pages.yml` you may only add paths (e.g. `assets/**`) to the push trigger.
7. Blurbs stay generated fresh on every build by `tools/make_blurbs.py` (see README) for every item without a story.

## STEP 0: probe (stop if it fails)
- `data/listings.csv` has a header `item,title,category,condition,format,ebay_url` and 380-460 rows.
- `python3 -m unittest discover -s tests` passes on `main` as you received it. Record the count.
- Create branch `site-design-2026-10`, commit `results/START_A2_<yyyy-mm-dd>.md` (time, commit you started from,
  test count) and **push it now**. If the push is refused (403 / no GitHub access), note it. Keep working, and use the
  bundle route in STEP 6.
- Check whether a headless browser is available (Playwright/Chromium). If not, try to install one. Record which.
- Take **before** screenshots of the current build (home and one item page; 390 px and 1280 px wide; light and dark)
  into `results/screens_A2/before/`.

## STEP 1: design plan (the skill's first pass)
Write `results/DESIGN_PLAN_A2.md`: subject/audience/job as you understand them, palette (4-6 named hex values with
purple as the signature), type and roles, layout concept with ASCII wireframes for the home page and an item page,
principles, and the photo plan (see STEP 2). Then review it against the brief as the skill directs. Name every part
that read as a generic default and what you changed it to.

## STEP 2: look, layout and browsing (in `build.py` and static assets)
- **Home page:** a hero that opens with the most characteristic thing in this shop's world (your call under the skill),
  then browsing. Sections by category. Within big sections, optional sub-grouping by decade **only** where the title
  itself contains a 4-digit year. Listings with **identical titles** appear once, with a link to each listing
  ("Listing 1", "Listing 2", ...). Do not claim they are the same item. A short "featured" row at the top, chosen
  deterministically (for example, the items with a story from STEP 4). Search stays plain JavaScript: it filters all
  items, shows a live result count, keeps working after Back, and offers clear empty-state direction.
- **Item page:** the title as the headline, category / condition / format, the blurb or story, one dominant
  "See it on eBay" button, a store link, and links to 3-6 related items from the same category.
- **Photos:** none exist now. Design a text-only card and item page that look intentional, **plus** the photo layout
  that turns on automatically when `data/images.csv` (`item,image_url`) appears. The build already supports that
  file: keep it working and add a test with a 2-row fixture.
- Keep the 404 page, RSS feed (`feed.xml`), `sitemap.xml` and `robots.txt` working.

## STEP 3: share previews and SEO
- Every page: unique `<title>` and meta description, canonical URL, Open Graph (`og:title`, `og:description`, `og:url`,
  `og:type`, `og:site_name`, `og:image`) and Twitter card tags.
- `og:image`: the listing photo when `images.csv` has one. Otherwise **one branded static PNG** (1200x630) you design
  and commit under `assets/`, generated during this session, not at build time.
- JSON-LD: `WebSite` + `Organization` on the home page; `BreadcrumbList` and a `Product` (name, url, category, image if
  any, brand StampedeUSA) on item pages, **with no `offers` and no price**.
- `sitemap.xml` with `lastmod`. The feed stays valid RSS 2.0 so Pinterest can auto-pin from it.
- Add tests: every page has og:title/og:description/canonical, JSON-LD parses as JSON, no `offers`/`price` key anywhere.

## STEP 4: stories for the first 50 listings (evaluation only)
Take the **first 50 data rows of `data/listings.csv`** at the commit you started from.
- Write `data/stories.csv` with columns `item,title_at_writing,story,source_url`. `build.py` uses a story only while
  that item is still listed **and** its current title equals `title_at_writing` exactly. Otherwise it falls back to the
  generated blurb. Test both paths.
- A story is 2-4 sentences in the brand voice. It may tell the history of the **subject the title names** (the event,
  person, place, animal or artwork on the stamp) **only with a source URL** from a reputable reference (Smithsonian
  National Postal Museum, USPS, Library of Congress, National Park Service, a museum, or an encyclopedia). If you can't
  reach a source, write a warm, claim-free story and leave `source_url` as `NO SOURCE`.
- Hard rule 2 still binds the stamp itself. No price, and no "$" unless it is copied verbatim from the title.
- Write `results/STORIES_REVIEW_A2.md`, a table of item, title, old blurb, new story, source, and **every factual
  claim in the story listed on its own line**, so Douglas can check them. These go live only if Douglas merges.

## STEP 5: verify and critique
- All tests pass (existing + new). Build into a temp dir with the current listings: count item pages = rows, no broken
  internal links, `feed.xml` and `sitemap.xml` parse as XML, every JSON-LD block parses, and nothing matches the price
  pattern outside titles.
- **After** screenshots, same pages and sizes as STEP 0, into `results/screens_A2/after/`. Look at them and critique as
  the skill says ("remove one accessory"). Fix what you find, then re-shoot.
- Measure and record: home page HTML size, largest item page size, total font bytes, and the text contrast ratios you chose.

## STEP 6: report and PR
`results/REPORT_A2_<yyyy-mm-dd>.md`: the plan and what the review changed, a before/after screenshot table, test
output, sizes, story count with how many are sourced vs NO SOURCE, anything skipped and why, and a short plain-language
"What happened, in order" list. Push branch `site-design-2026-10` and open a PR to `main`. **Never merge it. Never
change repo or Pages settings.**
**If the push is refused:** run `git bundle create results/site-design-2026-10.bundle main..site-design-2026-10` and end
by telling Douglas the exact file name to download from this session. OMEN will fetch it, test it and open the PR.
