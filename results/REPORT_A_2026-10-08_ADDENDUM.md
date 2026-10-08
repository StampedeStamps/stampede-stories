# REPORT A addendum, Thu 2026-10-08

- Push from the cloud session was refused (403, Claude GitHub App has no write access to this repo), so the branch was
  delivered as a git bundle and pushed from OMEN. The earlier BLOCKED note was removed (Douglas's ruling, 2026-10-08).
- Fix: the refresh no longer breaks when the listing count changes. Tests compare against the real row count; a
  listing with no row in data/blurbs.csv gets a generated blurb (tools/make_blurbs.py). Checked by adding a fake
  listing to a copy: 2 failures before, OK after.
- Blurbs now include the Scott number when the title has one: 422 distinct of 427 (was 385); the 5 repeats are
  titles with no Scott number. No new facts: the number is copied from the title.
- Tests: 6 tests, OK.
- Photos still OUT (eBay unreachable from the cloud). To add them, run on OMEN: write data/images.csv
  (item,image_url) from each listing's og:image; build.py picks it up.
