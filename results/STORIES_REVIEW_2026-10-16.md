# Stories review, Fri 2026-10-16: the five sourced stories

Written in a local Claude Code session on OMEN for Douglas's request of 2026-10-16 (make Stamp Stories awesome; test-run
Facebook stories for the five stamps under "Stories worth a read"). Each story names the stamp only by what its listing
title says; every other claim is history of the subject, with its source. Catalog pages were read this session with the
scott-us-lookup / scott-us-bob-lookup skills, never from memory. Two research subagents gathered the sources; every
claim below was checked against the fetched page text.

Rows in `data/stories.csv` run in home-cover order: the sourced stories take turns on the cover by the build date
(ordinal % 5), so Sat 10-17 shows Sarah Vaughan, Sun Jackson, Mon Duane, Tue Prussia, Wed the Pearl Harbor cover,
matching the planned Facebook posts.

## AUDIT FLAG (open, Douglas's call): listing 168402099827's title names the wrong stamp
The title says "Scott #C21 ... 20c Clipper". The stamp on the cover (main listing photo) is the "Map of United States
and Two Mail Planes" design, AP5: catalog 007 Air Post PDF p.3 lists it as **C9, 20c yellow green, Jan. 25, 1927**.
C21 (p.4) is the 20c green China Clipper design. The story below never says Clipper or C21. When the eBay title is
corrected, update `title_at_writing` for 168402099827 the same day, or the page falls back to the plain blurb.

## A letter from a harbor at war - item 168402099827
| Claim | Source |
|---|---|
| After Dec 7, 1941 Hawaii was put under martial law | encyclopedia.densho.org/Martial_law_in_Hawaii/ |
| Hawaii was then a U.S. territory | home.nps.gov/hono/.../martial-law-in-hawai-i.htm ("Hawaiian territory") |
| The Army censored civilian mail | Densho |
| Censors at an Information Control office beside the Honolulu post office opened, stamped and resealed letters | rumseyauctions.com/auctions/lot/92/1215 (Ken Lawrence in Linn's, quoted); usstamps.org Prexie Era Issue 51 (opened, stamped on the reverse, resealed with tape) |
| 1942 airmail cover from Pearl Harbor, T.H.; censor marking I.C.B. Censor 4 | listing title |
| Fact: martial law until Oct 24, 1944, almost three years | home.nps.gov/hono martial-law page |
| Left out: what the B in I.C.B. stands for (Branch vs Board, sources split 2-2); the meaning of "4"; the Clipper story | unverified, or the title's stamp ID is wrong |

## Newark's Divine One - item 168402099832 (#5059: outside the bundled catalog, title facts only)
| Claim | Source |
|---|---|
| Grew up in Newark, New Jersey | arts.gov/honors/jazz/sarah-vaughan ("her native Newark") |
| In 1942, still a teenager (born March 27, 1924), won an amateur contest at the Apollo in Harlem | about.usps.com/news/national-releases/2016/pr16_013.htm; arts.gov (birth date) |
| Billy Eckstine heard her there and recommended her to Earl Hines; she joined his band in 1943 | USPS pr16_013 (spring 1943) |
| Dave Garroway called her the Divine One; she was also called Sassy | USPS pr16_013 |
| 2016 Music Icons pane of 16 Forever stamps, MNH | listing title (USPS Postal Bulletin 2016: pane of 16, issued March 29, 2016, Newark) |
| Fact: 1989 NEA Jazz Master; 1989 Grammy Lifetime Achievement Award | arts.gov; live.grammy.com/awards/lifetime-achievement-awards/ |
| Left out: "Gershwin Live!" Grammy year (1982 vs 1983), the Apollo song, "four Grammys" | conflicting or unverified |

## The first stamps Uncle Sam printed - item 168402099704 (#253: 004 PDF p.61 "3c purple, Sept. 1894"; p.59 "Jackson - A89")
| Claim | Source |
|---|---|
| Before 1894 private companies printed every U.S. postage stamp under contract | postalmuseum.si.edu first-bureau-issues-1894-1898 |
| In July 1894 the Bureau of Engraving and Printing took over from the American Bank Note Company | postalmuseum.si.edu bureau-period-1894-1939; bep.gov/currency/history |
| Known as the First Bureau Issue | listing title; postalmuseum.si.edu |
| Jackson, seventh president; "Old Hickory" from sharing his soldiers' hardships | millercenter.org/president/jackson; .../life-before-the-presidency |
| 3c, purple, unwatermarked, used | listing title (catalog p.61) |
| Fact: in 1833 Jackson dismissed Treasury secretary William J. Duane for refusing to move the deposits | millercenter.org/president/jackson/domestic-affairs; home.treasury.gov |

## The secretary who said no - item 168402099809 (RD125: 042 PDF p.5 "SERIES 1942 ... RD125 ST1 50c bright green"; 50c portrait William J. Duane per 039 PDF p.21 and 042 p.4 "Same Portraits as Nos. R288-R310")
| Claim | Source |
|---|---|
| Duane made Secretary of the Treasury in May 1833 | home.treasury.gov/about/history/prior-secretaries/william-j-duane-1833 |
| Told to move the government's money out of the Second Bank; refused without the consent of Congress | home.treasury.gov (Duane) |
| Dismissed that September, after only four months | home.treasury.gov ("dismissed him after only four months of service"); senate.gov censure page ("On September 23 Jackson dismissed Duane") |
| Roger B. Taney took over and moved the deposits to state banks | senate.gov/about/parties-leadership/censure-president-jackson.htm |
| 1942 series 50c stock transfer stamp, green, full perfin, Duane | listing title; catalog as above |
| A perfin is small holes punched in a pattern, usually a firm's initials | perfinsoc.org.uk/introduction-to-perfins |
| Fact: Senate censure March 1834; Clay's first draft named the firing of Duane; expunged 1837 | senate.gov censure page |
| Left out: Duane's last day (Sept 22 vs 23), "fired" vs "resigned" (one Miller Center bio says resigned) | conflicting; the copy says "September" and "dismissed" |

## Stamps that counted the mail - item 168402099857 (Germany: no bundled catalog volume; title facts only)
| Claim | Source |
|---|---|
| Frei durch Ablösung means, roughly, free by settlement; Prussia's offices paid postage by a lump-sum contract with the Reichspost | de.wikipedia.org/wiki/Dienstmarken_(Deutsches_Reich) (Portoablösungsverträge); germanstamps.net/imp-dienst-1903/ |
| In 1903 officials put these stamps on their mail for one year so the real amount could be counted and the payment reset | de.wikipedia.org/wiki/Dienstmarke; de.wikipedia.org/wiki/Briefmarken-Jahrgang_1903_der_Deutschen_Reichspost |
| Nr. 21 is Prussia's contract number, in force since April 1, 1894 | de.wikipedia Dienstmarken (Deutsches Reich); germanstamps.net |
| 1903 official set, MH | listing title |
| Fact: the count found far less official mail than assumed, so payments were cut; Baden ran the same count in 1905, Nr. 16 | de.wikipedia Dienstmarke; de.wikipedia Dienstmarken (Deutsches Reich) |
| Note | No museum or philatelic-society page was found; German Wikipedia plus a collector site carry this story |
