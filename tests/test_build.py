import csv, html, re, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import build  # noqa: E402


class BuildTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = Path(cls.tmp.name) / "site"
        build.main(cls.out)
        cls.rows = build.read(ROOT / "data", "listings.csv")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_page_count(self):
        self.assertGreater(len(self.rows), 0)
        self.assertEqual(len(list((self.out / "item").glob("*.html"))), len(self.rows))

    def test_each_page_links_to_ebay(self):
        for r in self.rows:
            txt = (self.out / "item" / f"{r['item']}.html").read_text(encoding="utf-8")
            self.assertIn(f'href="{html.escape(r["ebay_url"])}"', txt, r["item"])
            self.assertIn("See it on eBay", txt)
            self.assertIn("- StampedeUSA", txt)

    def test_no_price_outside_titles(self):
        titles = sorted({html.escape(r["title"]) for r in self.rows} | {r["title"] for r in self.rows}, key=len, reverse=True)
        for p in list(self.out.rglob("*.html")) + [self.out / "feed.xml"]:
            txt = p.read_text(encoding="utf-8")
            for t in titles:
                txt = txt.replace(t, "")
            self.assertNotRegex(txt, r"\$\s*\d", p.name)

    def test_blurbs_have_no_price(self):
        titles = {r["item"]: r["title"] for r in self.rows}
        # data/blurbs.csv is a review snapshot the site does not read; check it only if it is there.
        if not (ROOT / "data/blurbs.csv").exists():
            self.skipTest("no data/blurbs.csv")
        bl = build.read(ROOT / "data", "blurbs.csv")
        for b in bl:
            self.assertTrue(b["blurb"].strip())
            # A blurb can outlive its listing (the daily refresh drops ended items from listings.csv);
            # such a leftover is never rendered, so it may not contain "$" at all.
            self.assertNotIn("$", b["blurb"].replace(titles.get(b["item"], ""), ""))

    def test_no_empty_blurb_paragraph(self):
        for r in self.rows:
            txt = (self.out / "item" / f"{r['item']}.html").read_text(encoding="utf-8")
            self.assertNotIn("<p></p>", txt, r["item"])

    def test_extras(self):
        for n in ("index.html", "feed.xml", "sitemap.xml", "robots.txt"):
            self.assertTrue((self.out / n).exists(), n)
        self.assertEqual((self.out / "sitemap.xml").read_text(encoding="utf-8").count("<url>"), len(self.rows) + 1)
        self.assertEqual((self.out / "feed.xml").read_text(encoding="utf-8").count("<item>"), len(self.rows))

    def test_google_verification_on_home_page(self):
        # Search Console checks this tag on the home page; if it disappears the property is un-verified.
        txt = (self.out / "index.html").read_text(encoding="utf-8")
        self.assertIn('<meta name="google-site-verification" content="LLXJ-AdRojWsQOPVel5D4eVxu6o9vwAzJJ_nle-0bQ8">', txt)

    def test_sitemap_hosts_are_lowercase(self):
        # Search Console's property is https://stampedestamps.github.io/stampede-stories/ (lowercase host).
        locs = re.findall(r"<loc>([^<]+)</loc>", (self.out / "sitemap.xml").read_text(encoding="utf-8"))
        self.assertTrue(locs)
        for loc in locs:
            self.assertTrue(loc.startswith("https://stampedestamps.github.io/stampede-stories/"), loc)

    def test_404_page(self):
        txt = (self.out / "404.html").read_text(encoding="utf-8")
        self.assertIn("https://www.ebay.com/str/stampedeusa", txt)
        self.assertIn("- StampedeUSA", txt)
        self.assertIn(f'href="{build.SITE_URL}/index.html"', txt)

    def test_blurbs_make_no_catalog_claims(self):
        # The Scott number is already in the page heading verbatim; a blurb must never pick or repeat one.
        for r in self.rows:
            txt = (self.out / "item" / f"{r['item']}.html").read_text(encoding="utf-8")
            body = txt.split("</h1>", 1)[1]
            self.assertNotIn("Listed under Scott", body, r["item"])


def write_csv(path, rows):
    with open(path, "w", encoding="utf-8", newline="") as f:
        csv.writer(f).writerows(rows)


class RefreshTest(unittest.TestCase):
    """A listings refresh from OMEN must never break the build or leave a stale claim on a page."""

    HEAD = ["item", "title", "category", "condition", "format", "ebay_url"]

    def build(self, listings, blurbs=None, bom=False):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        data = Path(tmp.name) / "data"
        data.mkdir()
        write_csv(data / "listings.csv", [self.HEAD] + listings)
        if bom:
            raw = (data / "listings.csv").read_bytes()
            (data / "listings.csv").write_bytes(b"\xef\xbb\xbf" + raw)
        if blurbs is not None:
            write_csv(data / "blurbs.csv", [["item", "blurb"]] + blurbs)
        out = Path(tmp.name) / "site"
        build.main(out, data)
        return out

    def page(self, out, item):
        return (out / "item" / f"{item}.html").read_text(encoding="utf-8")

    def test_ended_new_retitled_and_recategorized(self):
        out = self.build(
            [["111", "Scott #1 Test Stamp Used", "Revenues", "", "FIXED_PRICE", "https://www.ebay.com/itm/111"],
             ["222", "Brand New Listing $5 Face MNH", "Sheets", "", "AUCTION", "https://www.ebay.com/itm/222"]],
            # Stale rows: 111 was retitled (old blurb says MNH) and moved from Sheets; 999 has ended.
            [["111", "Old blurb filed under Sheets. Noted in the title: MNH."], ["999", "Ended listing blurb."]])
        self.assertEqual(sorted(p.name for p in (out / "item").glob("*.html")), ["111.html", "222.html"])
        p111 = self.page(out, "111")
        self.assertNotIn("Old blurb", p111)
        self.assertNotIn("MNH", p111)
        self.assertIn("Revenues", p111)
        self.assertIn("Noted in the title: used.", p111)
        p222 = self.page(out, "222")
        self.assertIn("Noted in the title: MNH.", p222)
        self.assertNotIn("<p></p>", p222)

    def test_no_blurbs_csv_and_bom(self):
        out = self.build([["333", "Single Perfin Used", "Revenues", "", "AUCTION", "https://www.ebay.com/itm/333"]], bom=True)
        p = self.page(out, "333")
        self.assertIn("Noted in the title: used, perfin.", p)
        self.assertNotIn("perfins", p)

    def test_blank_category_and_odd_format(self):
        out = self.build([["555", "Cover Used", "", "", "Auction", "https://www.ebay.com/itm/555"],
                          ["666", "Card MNH", " ", "", "", "https://www.ebay.com/itm/666"]])
        for item in ("555", "666"):
            p = self.page(out, item)
            self.assertIn("Category: Other", p)
            self.assertNotIn("our our", p)
            self.assertNotIn("the our ", p)
        self.assertRegex(self.page(out, "555"), r"up for auction|open for bids")
        p666 = self.page(out, "666")
        self.assertNotIn("buy now", p666)
        self.assertNotIn("auction", p666)
        self.assertNotIn("bids", p666)
        index = (out / "index.html").read_text(encoding="utf-8")
        self.assertIn("<h2>Other (2)</h2>", index)

    def test_flat_plate_is_not_a_plate_tag(self):
        out = self.build([["444", "Flat Plate Printing 2c MNH", "Sheets", "", "FIXED_PRICE", "https://www.ebay.com/itm/444"]])
        self.assertIn("Noted in the title: MNH.", self.page(out, "444"))


if __name__ == "__main__":
    unittest.main()
