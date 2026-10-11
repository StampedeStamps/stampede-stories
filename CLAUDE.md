# stampede-stories: notes for every Claude session

The public "Stamp Stories" site for the StampedeUSA eBay store (NO-COST ADVERTISING). Site:
https://stampedestamps.github.io/stampede-stories/

## Where the repo lives
- **On OMEN the git clone is `R:\stampede-stories-work\stampede-stories-publish`** (Douglas, Sun 2026-10-11). Use it for
  every fetch, bundle, test and push. Never search for it and never clone the site somewhere else.
- `R:\stampede-stories-work\stampede-stories` (next to it) is NOT a git clone.
- A cloud session cannot reach R:. If it cannot push here, it hands over a git bundle and OMEN fetches it into the
  folder above, runs the tests and pushes.

## How the site is built
- `build.py` (standard-library Python) generates every page from `data/listings.csv`; `tools/make_blurbs.py` writes
  the blurbs fresh on every build. Change `build.py`, `tools/`, `assets/` or tests, never a generated HTML file.
- GitHub Actions (`.github/workflows/pages.yml`) runs the tests, builds and deploys on every push to `main` that touches
  the paths it lists. If the tests fail, nothing deploys.
- OMEN pushes a fresh `data/listings.csv` every morning at 3:30 AM ET. Do not edit that file or anything that refresh writes.
- Run the tests before every push: `python -m unittest discover -s tests`.

## Rules
- This repo is PUBLIC: commit only public listing data, code, static assets and generated reports. No prices, buyer
  data, costs or secrets.
- No prices, ever. Dollar amounts in titles are face values; never call them a price, value or deal.
- No invented facts about a stamp: only what its title, category, condition and format say.
- Never merge a pull request and never change repo or Pages settings; those are Douglas's calls.
- Times in Eastern Time with the weekday, for example "Sun 2026-10-11 3:14 PM ET".
