# stampede-stories

The public "Stamp Stories" site for the StampedeUSA eBay store. Part of NO-COST ADVERTISING (Douglas, 2026-10-06).

- PUBLIC repo, by ruling: public listing data and generated pages only. No prices, buyer data, costs or secrets.
- Built once by a claude.ai/code cloud session (`CLOUD_TASK_A_STAMP_STORIES_SITE.md`). After that, GitHub Actions
  rebuilds the site with no model whenever `data/listings.csv` changes.
- `data/listings.csv` is generated on OMEN by `make_public_listings.py` (in the R: project folder, not in this repo)
  from the eBay all-active-listings export.

## How the site is built
- Site: https://stampedestamps.github.io/stampede-stories/ (GitHub Pages, Settings > Pages > Source: GitHub Actions).
- Every push to `main` that touches `data/**`, `build.py`, `tools/**`, `tests/**` or the workflow runs the tests, then
  `build.py`, then deploys. If the tests fail, nothing is deployed and the live site stays as it was.
  To rebuild by hand: Actions > Build and deploy Stamp Stories > Run workflow.
- Blurbs are written fresh from each listing's current title, category and format on every build
  (`tools/make_blurbs.py`), so an ended, new, retitled or recategorized listing never shows a stale claim.
  `data/blurbs.csv` is a snapshot of that text for review (`python tools/make_blurbs.py`); the site does not read it.
- Photos: add `data/images.csv` (columns `item,image_url`, eBay image URLs only) and the next build shows them.
- Google: a `robots.txt` under `/stampede-stories/` is not read by crawlers, so submit
  `https://stampedestamps.github.io/stampede-stories/sitemap.xml` in Google Search Console
  (URL-prefix property `https://stampedestamps.github.io/stampede-stories/`).
