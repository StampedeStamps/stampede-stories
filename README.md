# stampede-stories

The public "Stamp Stories" site for the StampedeUSA eBay store. Part of NO-COST ADVERTISING (Douglas, 2026-10-06).

- PUBLIC repo, by ruling: public listing data and generated pages only. No prices, buyer data, costs or secrets.
- Built once by a claude.ai/code cloud session (`CLOUD_TASK_A_STAMP_STORIES_SITE.md`). After that, GitHub Actions
  rebuilds the site with no model whenever `data/listings.csv` changes.
- `data/listings.csv` is generated on OMEN by `make_public_listings.py` (in the R: project folder, not in this repo)
  from the eBay all-active-listings export.
