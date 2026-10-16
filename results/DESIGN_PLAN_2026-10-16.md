# Stamp Stories redesign, Fri 2026-10-16 (local Claude Code session on OMEN)

Douglas, Fri 2026-10-16 4:48 PM ET: put on the Marketing/Advertising hats and make Stamp Stories as visually
attractive as www.stampedestamps.store, or more so; then test-run Facebook stories for the five stamps under
"Stories worth a read". Hats: CMO + CEO, lens SARA (no-cost project).

## What the hats found on the live site (measured 2026-10-16)
1. **No pictures.** The store shows every listing's photo (420 of 420). Stamp Stories shows none. Biggest single gap.
2. **The stories were not stories.** All 50 rows of `data/stories.csv` were `NO SOURCE`: cheerful lines that restate
   the title ("The title names Sarah Vaughan..."). The headline promises "Every stamp has a story."
3. **The featured row hid a card.** "Stories worth a read" held six cards in a row that clipped the sixth off the right
   edge at desktop width, with no sign it was there (Douglas counted five).
4. **The home page opened as a directory** (category tiles), not as a story.

## The plan (frontend-design skill: subject first, one bold device)
- **Subject and job.** Most visitors will now come from a Facebook story post, on a phone. The job: read one stamp's
  story, then tap "See it on eBay".
- **The one bold device: the cover.** Today's story arrives as airmail: an envelope on the album page with a purple and
  lilac chevron border, a return address ("Stamp Stories / StampedeUSA"), the stamp in the corner, and a purple
  circular postmark (site name round the ring, the build date inside, wavy killer bars across the stamp). The postmark
  strikes once as the page opens; reduced motion shows it already struck. Nothing else on the page moves.
- **Palette.** Royal purple #4B006E (signature: selvage, buttons, postmark ink, chevrons); lilac #D7B8F0 / #B48BD6
  (chevron and dark-theme accent); album page #F6F4FA with grid #E7E2EF (unchanged); envelope paper #FFFDF8 (the
  cover only); ink #1F1D2B; cancel red #B3261E (focus ring and "Has a story", unchanged). Dark theme = stockbook.
- **Type.** League Gothic (self-hosted) for headlines, the postmark and printed stamps; Charter / system serif for
  reading at 1.15rem, line height 1.7, measure under 62 characters. The story page opens with a League Gothic drop cap.
- **Stamps.** With a photo: the photo on perforated paper. Without one: a printed stamp built only from the title (its
  cents figure, "Forever", or the first year it states) on a lilac field, with the category in a purple value band.
- **Honest labels.** Only a story with at least one https source is a story: it is featured, marked "Has a story" and
  gets the story layout. A `NO SOURCE` line still shows on its own page but is no longer called a story.
- **Story page.** The stamp (cancelled) beside the story: headline, the eBay title as a subtitle, the hook as a
  standfirst, the story with a drop cap, a "Did you know?" box, the sources, then "See it on eBay", the store's photo
  page and "Share this story" (Facebook, Pinterest, Email, Copy the link: plain links, no scripts from other sites).
- **Home.** The promise and today's story side by side (the sourced stories take turns, one a day), then "Stories worth
  a read" as a grid that never hides a card, then search, the category pane and the shelf.
- **Photos are a switch.** `STORE_PHOTOS` in build.py reads the store's public photo list
  (www.stampedestamps.store/data/catalog_images.csv, 420 of 420 listings) and every photo slot fills, with no other
  change. It was OFF under Douglas's 10-11 "Submit, stay text-only meanwhile"; **Douglas turned it ON on Fri 2026-10-16
  ~7:15 PM ET** ("Turn photos on (Recommended)"), after seeing both versions.

## Review against the brief (what read as a default, and what changed)
- A first idea, a "Story of the week" label in tracked capitals over the hero, read as template chrome. Changed to the
  envelope's own vocabulary: the return address, and an italic "Today's story" where an address line would sit.
- A plain list of story cards read as the generic card kit. Changed to stamps mounted on the album page, each with its
  write-up underneath, no card box.
- The printed stamps first had a big empty middle. Changed to a stamp-like lilac field with a purple value band.
- Middle-dot meta strings and arrow links were avoided throughout.

## Kept from the A2 design (10-11)
Album page / stockbook themes, perforation mask, purple selvage, the category pane with "Mail early in the day", search,
decade groups, feed, sitemap, robots, 404, share tags and JSON-LD, and the store link and canonical from 0cd3929.
