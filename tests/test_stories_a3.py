"""2026-10-16 redesign: the story layout, today's story on the cover, honest story labels, and store photos."""
import csv, datetime, html, io, re, sys, tempfile, unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import build  # noqa: E402

HEAD = ["item", "title", "category", "condition", "format", "ebay_url"]
STORY_HEAD = ["item", "title_at_writing", "story", "source_url", "headline", "hook", "fact"]
DAY = datetime.date(2026, 10, 16)

LISTINGS = [
    ["701", "Scott #253 US 1894 3c Jackson Purple First Bureau Issue Unwatermarked Used", "19th Century: Used", "",
     "FIXED_PRICE", "https://www.ebay.com/itm/701"],
    ["702", "Scott #C21 1942 Pearl Harbor T.H. Airmail Cover 20c Clipper I.C.B. Censor 4", "Postal History", "",
     "FIXED_PRICE", "https://www.ebay.com/itm/702"],
    ["703", "Scott #5059 2016 Sarah Vaughan Music Icons Forever Pane of 16 MNH Jazz Singer", "Sheets", "",
     "FIXED_PRICE", "https://www.ebay.com/itm/703"],
    ["704", "Scott #1192 Arizona Statehood 1962 4c Full Sheet of 50 MNH Saguaro Cactus", "Sheets", "",
     "AUCTION", "https://www.ebay.com/itm/704"],
]
STORIES = [
    ["701", LISTINGS[0][1], "Andrew Jackson was the seventh president. This 3c stamp came from the Bureau's first year.",
     "https://www.britannica.com/biography/Andrew-Jackson https://www.bep.gov/about", "Old Hickory, in purple",
     "The first stamps the Bureau printed itself.", "Jackson is on more than one U.S. stamp."],
    ["702", LISTINGS[1][1], "Clipper flying boats carried mail across the Pacific.",
     "https://airandspace.si.edu/x", "Clipper mail from a harbor at war", "Mailed from Pearl Harbor in 1942.", ""],
    ["703", LISTINGS[2][1], "A warm, claim-free line about a great singer.", "NO SOURCE", "", "", ""],
]


def write_csv(path, rows):
    with open(path, "w", encoding="utf-8", newline="") as f:
        csv.writer(f).writerows(rows)


class StoryLayoutTest(unittest.TestCase):
    def build(self, stories=STORIES, photos=None, store=None, today=DAY):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        data = Path(tmp.name) / "data"
        data.mkdir()
        write_csv(data / "listings.csv", [HEAD] + LISTINGS)
        write_csv(data / "stories.csv", [STORY_HEAD] + stories)
        out = Path(tmp.name) / "site"
        build.main(out, data, store=store, photos=photos, today=today)
        return out

    def read(self, out, name):
        return (out / name).read_text(encoding="utf-8")

    def test_story_page_parts(self):
        p = self.read(self.build(), "item/701.html")
        self.assertIn('<main id="main" class="story-page">', p)
        self.assertIn('<h1 class="headline">Old Hickory, in purple</h1>', p)
        self.assertIn(f'<p class="listing-title">{html.escape(LISTINGS[0][1])}</p>', p)
        self.assertIn('<p class="standfirst">The first stamps the Bureau printed itself.</p>', p)
        self.assertIn('<h2 id="fact-h">Did you know?</h2><p>Jackson is on more than one U.S. stamp.</p>', p)
        self.assertIn('href="https://www.britannica.com/biography/Andrew-Jackson"', p)    # every source is linked
        self.assertIn('href="https://www.bep.gov/about"', p)
        self.assertEqual(p.count("See it on eBay"), 1)
        self.assertIn('class="postmark"', p)
        self.assertIn(">OCT 16</text>", p)
        own = f"{build.SITE_URL}/item/701.html"
        self.assertIn("https://www.facebook.com/sharer/sharer.php?u=" + build.quote(own, safe=""), p)
        self.assertIn("https://www.pinterest.com/pin/create/button/?url=", p)
        self.assertIn('href="mailto:?subject=', p)
        self.assertIn(f'data-url="{own}"', p)
        self.assertIn('<span class="face">3c</span>', p)           # no photo: the printed stamp, from the title only
        self.assertIn("<title>Old Hickory, in purple: Scott #253", p)

    def test_story_without_a_fact_has_no_fact_box(self):
        p = self.read(self.build(), "item/702.html")
        self.assertIn('<h1 class="headline">Clipper mail from a harbor at war</h1>', p)
        self.assertNotIn("Did you know?", p)
        self.assertNotIn("<p></p>", p)

    def test_no_source_line_is_not_a_story(self):
        out = self.build()
        p = self.read(out, "item/703.html")
        self.assertIn("A warm, claim-free line about a great singer.", p)    # still shown on its own page
        self.assertNotIn('class="headline"', p)
        self.assertNotIn('class="source"', p)
        home = self.read(out, "index.html")
        self.assertNotIn('href="item/703.html"><span class="stamp', home)   # never featured
        row = re.search(r'<li class="row"[^>]*>.*?item/703\.html.*?</li>', home).group(0)
        self.assertNotIn("Has a story", row)
        self.assertIn("Has a story", re.search(r'<li class="row"[^>]*>.*?item/701\.html.*?</li>', home).group(0))

    def test_cover_takes_turns_and_the_rest_are_featured(self):
        seen = set()
        for d in range(2):
            day = DAY + datetime.timedelta(days=d)
            home = self.read(self.build(today=day), "index.html")
            cover = re.search(r'<article class="cover".*?</article>', home, re.S).group(0)
            it = re.search(r'href="item/(\d+)\.html">Read the story', cover).group(1)
            seen.add(it)
            told = ["701", "702"]
            self.assertEqual(it, told[day.toordinal() % 2])
            feat = re.search(r'<section class="featured".*?</section>', home, re.S).group(0)
            self.assertIn("Stories worth a read", feat)
            self.assertIn(f'href="item/{told[1 - told.index(it)]}.html"', feat)
            self.assertNotIn(f'href="item/{it}.html"', feat)          # the cover story is not repeated below it
            self.assertIn(day.strftime("%b").upper(), cover)
        self.assertEqual(seen, {"701", "702"})

    def test_no_sourced_story_falls_back_to_fresh_from_the_shelf(self):
        home = self.read(self.build(stories=[STORIES[2]]), "index.html")
        self.assertNotIn('class="cover"', home)
        self.assertIn("Fresh from the shelf", home)
        self.assertIn('class="featured"', home)

    def test_store_photos_turn_on_the_photo_layout(self):
        pic = "https://www.stampedestamps.store/images/catalog/701.jpg"
        out = self.build(photos={"701": pic, "702": "http://not-https.example/x.jpg"})
        p = self.read(out, "item/701.html")
        self.assertIn(f'<span class="stamp perf edged photo big"><img src="{pic}" alt="">', p)
        self.assertIn(f'property="og:image" content="{pic}"', p)
        self.assertIn("&amp;media=" + build.quote(pic, safe=""), p)    # Pinterest gets the photo
        self.assertNotIn("not-https", self.read(out, "item/702.html"))  # only https photos are used
        self.assertIn('<span class="face">20c</span>', self.read(out, "item/702.html"))

    def test_story_page_keeps_the_store_link_and_canonical(self):
        out = self.build(store={"701": True})
        p = self.read(out, "item/701.html")
        shop = f"{build.STORE_SITE}/catalog/item/701.html"
        self.assertIn(f'<link rel="canonical" href="{shop}">', p)
        self.assertIn(f'<a href="{shop}">See it with its photo at stampedestamps.store</a>', p)
        self.assertIn(f'data-url="{build.SITE_URL}/item/701.html"', p)  # sharing points at the story itself

    def test_money_in_a_headline_hook_or_fact_stops_the_build(self):
        for col in (4, 5, 6):
            bad = list(STORIES[0])
            bad[col] = "Yours for $5 today."
            with self.assertRaises(SystemExit):
                self.build(stories=[bad])

    def test_face_comes_only_from_the_title(self):
        self.assertEqual(build.face("Scott #253 US 1894 3c Jackson Purple"), "3c")
        self.assertEqual(build.face("Scott #RD125 US Series 1942 50c Stock Transfer Duane"), "50c")
        self.assertEqual(build.face("Scott #5059 2016 Sarah Vaughan Music Icons Forever Pane of 16 MNH"), "Forever")
        self.assertEqual(build.face("Scott #RV42 $5 Motor Vehicle Use Revenue 1945 Mint No Gum"), "1945")
        self.assertEqual(build.face("Scott #3412 $11.75 Round Hologram Earth Space Sheet"), "")
        self.assertEqual(build.face("Scott #OL3-OL5 Germany Prussia 1903 Frei Durch Ablosung"), "1903")


class StorePhotosTest(unittest.TestCase):
    def test_reads_the_store_photo_list_and_fails_safe(self):
        body = "item,image\n101,images/catalog/101.jpg\n102,images/catalog/102-e.jpg\nbad,images/x.jpg\n103,/etc/x\n"
        with mock.patch.object(build.urllib.request, "urlopen", return_value=io.BytesIO(body.encode("utf-8"))):
            self.assertEqual(build.store_photos(), {
                "101": "https://www.stampedestamps.store/images/catalog/101.jpg",
                "102": "https://www.stampedestamps.store/images/catalog/102-e.jpg"})
        with mock.patch.object(build.urllib.request, "urlopen", side_effect=OSError("offline")):
            self.assertEqual(build.store_photos(), {})

    def test_photos_stay_off_until_douglas_says_so(self):
        self.assertFalse(build.STORE_PHOTOS)


if __name__ == "__main__":
    unittest.main()
