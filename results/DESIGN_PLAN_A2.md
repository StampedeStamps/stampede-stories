# DESIGN PLAN A2: Stamp Stories

Written Sun 2026-10-11, STEP 1, under `.claude/skills/frontend-design/SKILL.md`. Part 1 is the first-pass plan, as
written. Part 2 reviews it against the brief and names what changed. Part 3 is the revised plan that STEP 2 builds.

## Subject, audience, job (as I understand them)
- **Subject:** StampedeUSA, a small eBay shop. Of the 421 live listings at `d855e01`, 178 are mint U.S. sheets and panes
  (the 1950s to now: Nature of America, Legends of Hollywood, Marvel and DC heroes, Sesame Street, plate-number
  sheets), 70 are revenues, 39 are 1901-40 unused singles, 34 are postal history. The rest are small foreign and
  back-of-book groups. 359 of 421 titles carry a 4-digit year. There are no photos.
- **Audience:** (1) collectors who read "Scott #3099a ... Pane of 20 MNH Plate B1111" fluently and want to scan fast;
  (2) casual visitors from Pinterest or Google who know Batman, Betty White, Babe Ruth or dinosaurs but not "MNH".
- **Primary job:** a visitor sees something that catches their eye and clicks through to the eBay listing (or the
  store). Success = more click-throughs to listings that already exist, which shortens days-to-sale.
- **Fixed:** royal purple `#4B006E` is the signature; "- StampedeUSA" sign-off and the store link on every page; voice
  positive, upbeat, light, a little humorous; mobile-first, light and dark themes, visible focus, reduced motion, WCAG AA.

## Part 1: first-pass plan (as first written)
- Color: royal purple header bar; white background; a light lavender `#F4ECF8` for cards; purple links; a gold
  `#E0B000` accent for "featured".
- Type: Inter (the system has it) for everything, bold headings.
- Layout: purple header bar with the name; hero = big headline "Every stamp has a story", a sub-line and a purple
  "Visit the eBay store" button on a soft purple-to-white gradient; a row of rounded category cards (name + count) with a
  soft shadow; search box; then every category as a grid of rounded cards with title and a small "MNH · Sheets" meta
  line; item page = headline, meta line, blurb, purple button, "← Back".
- Principles: clean, modern, friendly.

## Part 2: review against the brief
I worked a similar prompt ("design a site for a small online shop with ~400 products and a brand color") and arrived
at almost exactly Part 1, so nearly all of it was a generic default. What I changed, and why:

| Part of plan 1 | Why it reads as a default | Changed to |
|---|---|---|
| Inter everywhere, bold headings | The default sans on any page; says nothing about stamps | **League Gothic** (OFL, 10.4 KB woff2, self-hosted) for headlines: the condensed American gothic of early-1900s printing and of stamp inscriptions. Its narrow width also lets 80-character titles like "Scott #3023a 1995 32c Antique Autos Pane of 25 MNH ..." sit as a 2-3 line headline. Body in the system **Charter** serif stack (0 bytes): sturdy book type for reading a story, clearly distinct from the gothic |
| Gradient hero with headline + button | Skill: "gradient accent ... is the default treatment" | **The hero is a pane of stamps.** A royal-purple sheet margin (selvage) holds perforated stamp-paper tiles, one per category, each with the category name and how many are listed. It is the most characteristic object in this shop's world (178 of 421 listings are panes) and it is also the browsing menu, so it does a job. The selvage carries the site name; its side margin carries "Mail early in the day", the real 1960s-70s USPS selvage inscription, as the one quiet joke for collectors |
| Rounded cards with soft shadow for every listing | SaaS-card kit (trait 4) | No shadows anywhere. Listings are **album rows**: a title line with small facts under it, on a quadrille album page. Only the featured row and the item-page headline use the perforated stamp shape, so perforation means "look here" |
| White background + lavender | Neutral default | Light theme = **album page**: a cool lilac-white sheet with a faint quadrille grid like a printed album page. Dark theme = **stockbook**: the black card page of a collector's stockbook with clear glassine strips (rows get a faint translucent band). Each theme names a real collecting material |
| Gold "featured" accent | Arbitrary | **Cancel red** `#B3261E`, the color of a red cancellation. Used only for keyboard focus rings and the small "Has a story" mark. A cancel is a mark on a stamp, which is what focus is |
| "MNH · Sheets" meta with middle dots, "← Back", "→" links | Template chrome (trait 5) | Facts as a short definition list ("Category", "Format"); breadcrumb "Stamp Stories / Sheets"; link text with no arrows |
| Category heading "Sheets (178)" in purple with a rule | Default | Gothic headline with the count in plain words ("178 listed"). Big sections get decade sub-headings only where the title states a year; "Year not in the title" collects the rest |
| "Visit the eBay store" button in the hero | Duplicates the main job of the item page | The store link sits in the selvage (top) and footer; the hero's job is to start browsing. The one dominant button lives on the item page |

## Part 3: the revised plan (what STEP 2 builds)

### Color (6 named core tokens, purple is the signature)
| Name | Hex | Role |
|---|---|---|
| Royal purple | `#4B006E` | Signature: selvage bands (header, hero sheet, footer), the "See it on eBay" button, light-theme links and headlines |
| Lilac | `#D7B8F0` | Purple for dark theme text and links; hero tile counts in dark theme |
| Album page | `#F6F4FA` | Light page background; quadrille grid lines are `#E7E2EF` |
| Stamp paper | `#FFFFFF` | Perforated tiles and the item stamp in light theme |
| Postmark ink | `#1F1D2B` | Body text in light theme (a blue-black, not a tinted #111) |
| Cancel red | `#B3261E` | Focus rings and the "Has a story" mark only. Dark theme uses `#FF8A80` for the same jobs |
Dark theme ("stockbook"): page `#1C1A22`, glassine strips `rgba(255,255,255,.045)`, stamp paper `#2A2732`, text `#ECE8F3`.
Contrast targets: all body text >= 7:1, small text >= 4.5:1, focus rings >= 3:1 against the page (measured in STEP 5).

### Type
- **League Gothic** 400 (self-hosted woff2, latin subset, OFL in `assets/fonts/`): site name, H1 titles, section and
  decade headings, hero tile names. Sentence case or the title's own case. Never all caps. Tracking +0.01em.
- **Charter stack** (`Charter, "Bitstream Charter", "Sitka Text", Cambria, Georgia, serif`): body, blurbs, stories,
  list titles. 17-18 px, line-height 1.6, measure <= 68ch.
- Scale (ratio 1.25 from 17 px): 17 / 21 / 27 / 33 / 42 / 52. Gothic headings run one step larger than a serif would,
  because the face is narrow.

### Layout and wireframes
Home, left-aligned throughout (lists read down the left edge; only the sign-off is centered).
```
390 px                                      1280 px (content max 72rem)
+--------------------------------+          +-------------------------------------------------------------+
| SELVAGE: Stamp Stories  [store]|          | SELVAGE: Stamp Stories           Visit the eBay store       |
+--------------------------------+          +-------------------------------------------------------------+
| Every stamp has a story.       |          | Every stamp has a story.            (gothic, 52px)          |
| 421 of them are on our shelf.  |          | 421 of them are on our shelf. Pick a category or search.    |
| +----------------------------+ |          | +---------------------------------------------------------+ |
| |purple sheet margin         | |          | | purple sheet margin "Stamp Stories by StampedeUSA"      | |
| | [Sheets   ][Revenues ]     | |  M       | | [Sheets  ][Revenues][1901-40 ][Postal  ][19th C. ]  M   | |
| | [178      ][70       ]     | |  a       | | [178     ][70      ][39      ][34      ][12     ]  a   | |
| | [1901-40  ][Postal   ]     | |  i       | | [19th C. ][Collect.][Event   ][First   ][Every-  ]  i   | |
| | [39       ][34       ]     | |  l       | | [12      ][11      ][8       ][6       ][thing.. ]  l   | |
| | ... 8 tiles + "All the rest"| |  early  | +---------------------------------------------------------+ |
| +----------------------------+ |          | [ Search 421 stamps and covers.........] 421 shown         |
| [ Search 421 ............... ] |          |                                                             |
| 421 shown                      |          | Stories worth a read                                        |
| Stories worth a read           |          | [stamp][stamp][stamp][stamp][stamp][stamp] (perforated)     |
| [stamp][stamp] (scrolls  ->)   |          |                                                             |
| Sheets  178 listed             |          | Sheets  178 listed                                          |
|  1950s                         |          |   1950s   title / facts                                     |
|   title                        |          |   1960s   title / facts   (decade in a left gutter column)  |
|   Sheets, Buy It Now           |          |                                                             |
| ...                            |          | ...                                                         |
| - StampedeUSA                  |          |              - StampedeUSA / Visit the store                |
+--------------------------------+          +-------------------------------------------------------------+
```
Item page, single column, max 44rem:
```
+-------------------------------------------+
| SELVAGE: Stamp Stories        [store]     |
| Stamp Stories / Sheets   (breadcrumb)     |
| +~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+ |  perforated stamp: photo when images.csv has one,
| (  Scott #3099a 1996 32c Big Band       ) |  otherwise the title itself printed in gothic as
| (  Leaders Sheet 20 MNH Basie ...       ) |  the stamp's design (text-only state = intentional)
| +~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+ |
| Category  Sheets      Format  Buy It Now  |  definition list; Condition only when the field has one
| Story or blurb (Charter, 2-4 sentences)   |
| Source: Smithsonian ... (stories only)    |
| [        See it on eBay        ] purple   |  the one dominant button, full width on mobile
| Browse everything in the StampedeUSA store|
| More from Sheets: 3-6 related titles      |
| - StampedeUSA                             |
+-------------------------------------------+
```
With a photo, the H1 moves below the stamp and the stamp holds the image (`object-fit: contain` on stamp paper).
Home rows gain a 64 px thumbnail at the left when the item has a photo; rows without one keep the text layout.

### Principles
1. **One bold thing: perforation.** It appears on the hero pane, the featured stamps and the item-page stamp, nowhere
   else. Everything around it is quiet: no shadows, no gradients, no hover animations on rows.
2. **Materials, not decoration.** Album page (light), stockbook (dark), selvage (purple bands), cancel (red focus).
3. **Titles are the content.** Never truncate a title on an item page; on lists allow full wrap. No claims beyond the
   fields; face values stay inside the title.
4. **Plain words for casual visitors.** "Buy It Now" / "Auction" instead of FIXED_PRICE; "Has a story" mark; search
   placeholder suggests words people know ("Batman", "eagle", "1962").
5. **Motion only on request.** One small press state on the button; none when `prefers-reduced-motion: reduce`.

### Photo plan
No photos exist (eBay has not issued API keys). Text-only is the designed default: the item-page stamp shows the title
as its design and the home rows are typographic. When `data/images.csv` (`item,image_url`) appears, the build turns on
automatically: item stamp shows the photo (with `alt` = title, width/height hints, `loading` eager on item pages),
home rows get a 64 px thumbnail, featured stamps show the photo, `og:image` and JSON-LD `image` use it, and `feed.xml`
gets an enclosure. A 2-row fixture test covers it.
