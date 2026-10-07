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
        with open(ROOT / "data/listings.csv", encoding="utf-8", newline="") as f:
            cls.rows = list(csv.DictReader(f))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_page_count(self):
        self.assertEqual(len(self.rows), 427)
        self.assertEqual(len(list((self.out / "item").glob("*.html"))), 427)

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
        with open(ROOT / "data/blurbs.csv", encoding="utf-8", newline="") as f:
            bl = list(csv.DictReader(f))
        self.assertEqual(len(bl), 427)
        for b in bl:
            self.assertTrue(b["blurb"].strip())
            self.assertNotIn("$", b["blurb"].replace(titles[b["item"]], ""))

    def test_extras(self):
        for n in ("index.html", "feed.xml", "sitemap.xml", "robots.txt"):
            self.assertTrue((self.out / n).exists(), n)
        self.assertEqual((self.out / "sitemap.xml").read_text().count("<url>"), 428)
        self.assertEqual((self.out / "feed.xml").read_text().count("<item>"), 427)


if __name__ == "__main__":
    unittest.main()
