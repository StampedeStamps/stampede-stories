"""A2 redesign: share previews, SEO, JSON-LD, stories, photos, identical titles, browsing and links."""
import csv, html, json, re, struct, sys, tempfile, unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import build  # noqa: E402

HEAD = ["item", "title", "category", "condition", "format", "ebay_url"]
LD = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)


def write_csv(path, rows):
    with open(path, "w", encoding="utf-8", newline="") as f:
        csv.writer(f).writerows(rows)


def keys(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield k
            yield from keys(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from keys(v)


def lds(txt):
    return [json.loads(m.replace("<\\/", "</")) for m in LD.findall(txt)]


class LiveSiteTest(unittest.TestCase):
    """The real data/ folder, built once."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = Path(cls.tmp.name) / "site"
        build.main(cls.out)
        cls.rows = build.read(ROOT / "data", "listings.csv")
        cls.pages = sorted(cls.out.rglob("*.html"))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_every_page_has_share_tags(self):
        need = ['property="og:title"', 'property="og:description"', 'property="og:url"', 'property="og:type"',
                'property="og:site_name"', 'property="og:image"', 'name="twitter:card"', 'rel="canonical"',
                'name="description"']
        for p in self.pages:
            txt = p.read_text(encoding="utf-8")
            for n in need:
                self.assertIn(n, txt, f"{p.name}: {n}")

    def test_titles_and_descriptions_unique(self):
        titles, descs = {}, {}
        for p in self.pages:
            if p.parent.name == "assets":
                continue
            txt = p.read_text(encoding="utf-8")
            t = re.search(r"<title>(.*?)</title>", txt).group(1)
            d = re.search(r'<meta name="description" content="(.*?)">', txt).group(1)
            self.assertNotIn(t, titles, f"{p.name} repeats the title of {titles.get(t)}")
            self.assertNotIn(d, descs, f"{p.name} repeats the description of {descs.get(d)}")
            titles[t], descs[d] = p.name, p.name

    def test_jsonld_parses_and_has_no_price(self):
        for p in self.pages:
            for obj in lds(p.read_text(encoding="utf-8")):
                ks = {k.lower() for k in keys(obj)}
                self.assertFalse({"offers", "price", "pricecurrency", "lowprice", "highprice"} & ks, p.name)
        home = {o["@type"] for o in lds((self.out / "index.html").read_text(encoding="utf-8"))}
        self.assertEqual(home, {"WebSite", "Organization"})
        for r in self.rows[:25]:
            types = {o["@type"]: o for o in lds((self.out / "item" / f"{r['item']}.html").read_text(encoding="utf-8"))}
            self.assertEqual(set(types), {"BreadcrumbList", "Product"})
            self.assertEqual(types["Product"]["name"], r["title"])
            self.assertEqual(types["Product"]["brand"]["name"], "StampedeUSA")

    def test_no_price_anywhere_outside_titles(self):
        titles = sorted({v for r in self.rows for v in (r["title"], html.escape(r["title"]),
                                                        json.dumps(r["title"], ensure_ascii=False)[1:-1])},
                        key=len, reverse=True)
        for p in self.pages + [self.out / "feed.xml", self.out / "assets" / "site.css"]:
            txt = p.read_text(encoding="utf-8")
            for t in titles:
                txt = txt.replace(t, "")
            self.assertNotRegex(txt, r"\$\s*\d", p.name)
            self.assertNotRegex(txt.lower(), r"\bprice\b|\bdeal\b", p.name)

    def test_feed_and_sitemap_parse(self):
        rss = ET.parse(self.out / "feed.xml").getroot()
        self.assertEqual(rss.tag, "rss")
        self.assertEqual(rss.get("version"), "2.0")
        self.assertEqual(len(rss.findall("./channel/item")), len(self.rows))
        sm = ET.parse(self.out / "sitemap.xml").getroot()
        ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        urls = sm.findall("s:url", ns)
        self.assertEqual(len(urls), len(self.rows) + 1)
        for u in urls:
            self.assertRegex(u.find("s:lastmod", ns).text, r"^\d{4}-\d{2}-\d{2}$")

    def test_internal_links_resolve(self):
        for p in self.pages:
            if p.name == "404.html":
                continue  # absolute links by design
            txt = p.read_text(encoding="utf-8")
            for href in re.findall(r'(?:href|src)="([^"#?]+)', txt):
                if href.startswith(("http://", "https://", "mailto:")):
                    continue
                self.assertTrue((p.parent / html.unescape(href)).resolve().exists(), f"{p.name}: {href}")
            for frag in re.findall(r'href="(?:\.\./)?index\.html#([^"]+)"', txt):
                self.assertIn(f'id="{frag}"', (self.out / "index.html").read_text(encoding="utf-8"), frag)

    def test_item_page_parts(self):
        for r in self.rows:
            txt = (self.out / "item" / f"{r['item']}.html").read_text(encoding="utf-8")
            self.assertEqual(txt.count("See it on eBay"), 1, r["item"])
            self.assertIn(f"Category: {html.escape(build.category(r))}", txt)
            self.assertIn("https://www.ebay.com/str/stampedeusa", txt)
            self.assertIn("- StampedeUSA", txt)
            rel = re.search(r'<section class="related">(.*?)</section>', txt, re.S)
            same = [x for x in self.rows if build.category(x) == build.category(r) and x["title"] != r["title"]]
            if len({x["title"] for x in same}) >= 3:
                n = rel.group(1).count("<li>")
                self.assertTrue(3 <= n <= 6, f"{r['item']}: {n} related")
                for it in re.findall(r'href="(\d+)\.html"', rel.group(1)):
                    other = next(x for x in self.rows if x["item"] == it)
                    self.assertEqual(build.category(other), build.category(r))

    def test_assets_self_hosted(self):
        self.assertTrue((self.out / "assets" / "fonts" / "OFL.txt").exists())
        css = (self.out / "assets" / "site.css").read_text(encoding="utf-8")
        self.assertNotRegex(css, r"url\((?:'|\")?https?:")
        for p in self.pages:
            txt = p.read_text(encoding="utf-8")
            self.assertNotRegex(txt, r"<script[^>]+src=", p.name)
            self.assertNotRegex(txt, r'<link[^>]+href="https?://(?!stampedestamps)[^"]+"[^>]*stylesheet', p.name)
        png = (ROOT / build.OG_DEFAULT).read_bytes()
        self.assertEqual(png[:8], b"\x89PNG\r\n\x1a\n")
        self.assertEqual(struct.unpack(">II", png[16:24]), (1200, 630))

    def test_home_search_and_featured(self):
        txt = (self.out / "index.html").read_text(encoding="utf-8")
        self.assertIn('id="q"', txt)
        self.assertIn('aria-live="polite"', txt)
        self.assertIn("pageshow", txt)
        self.assertIn('id="empty"', txt)
        self.assertEqual(sum(int(n) for n in re.findall(r'class="row" data-n="(\d+)"', txt)), len(self.rows))
        self.assertIn('class="featured"', txt)


class FixtureTest(unittest.TestCase):
    def build(self, listings, stories=None, images=None):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        data = Path(tmp.name) / "data"
        data.mkdir()
        write_csv(data / "listings.csv", [HEAD] + listings)
        if stories is not None:
            write_csv(data / "stories.csv", [["item", "title_at_writing", "story", "source_url"]] + stories)
        if images is not None:
            write_csv(data / "images.csv", [["item", "image_url"]] + images)
        out = Path(tmp.name) / "site"
        build.main(out, data)
        return out

    def read(self, out, name):
        return (out / name).read_text(encoding="utf-8")

    def test_images_fixture_turns_on_photo_layout(self):
        out = self.build(
            [["101", "Eagle Sheet of 50 MNH", "Sheets", "", "FIXED_PRICE", "https://www.ebay.com/itm/101"],
             ["102", "Owl Pane of 20 MNH", "Sheets", "", "AUCTION", "https://www.ebay.com/itm/102"],
             ["103", "Bison Pane of 20 MNH", "Sheets", "", "AUCTION", "https://www.ebay.com/itm/103"]],
            images=[["101", "https://i.ebayimg.com/images/g/AAA/s-l1600.jpg"],
                    ["102", "https://i.ebayimg.com/images/g/BBB/s-l1600.jpg"]])
        p101 = self.read(out, "item/101.html")
        self.assertIn('<img src="https://i.ebayimg.com/images/g/AAA/s-l1600.jpg" alt="Eagle Sheet of 50 MNH">', p101)
        self.assertIn('property="og:image" content="https://i.ebayimg.com/images/g/AAA/s-l1600.jpg"', p101)
        self.assertIn('class="photo-title"', p101)
        prod = [o for o in lds(p101) if o["@type"] == "Product"][0]
        self.assertEqual(prod["image"], "https://i.ebayimg.com/images/g/AAA/s-l1600.jpg")
        p103 = self.read(out, "item/103.html")
        self.assertIn(f'content="{build.SITE_URL}/{build.OG_DEFAULT}"', p103)
        self.assertNotIn("<img", p103)
        self.assertNotIn("image", [o for o in lds(p103) if o["@type"] == "Product"][0])
        home = self.read(out, "index.html")
        self.assertEqual(home.count('width="64" height="64"'), 2)
        self.assertEqual(self.read(out, "feed.xml").count("<enclosure "), 2)

    def test_story_used_only_while_title_unchanged(self):
        story = "Owls hunt at night and fly almost silently. This one is happy to stay in the album."
        out = self.build(
            [["201", "Owl Pane of 20 MNH", "Sheets", "", "FIXED_PRICE", "https://www.ebay.com/itm/201"],
             ["202", "Eagle Sheet of 50 MNH Plate 12345", "Sheets", "", "FIXED_PRICE", "https://www.ebay.com/itm/202"]],
            stories=[["201", "Owl Pane of 20 MNH", story, "https://www.britannica.com/animal/owl"],
                     ["202", "Eagle Sheet of 50 MNH", "Eagles are big. Old story.", "NO SOURCE"],
                     ["999", "Ended Listing", "Should never show.", "NO SOURCE"]])
        p201 = self.read(out, "item/201.html")
        self.assertIn(story, p201)
        self.assertIn('href="https://www.britannica.com/animal/owl"', p201)
        self.assertIn("Has a story", self.read(out, "index.html"))
        p202 = self.read(out, "item/202.html")  # retitled since the story was written: blurb instead
        self.assertNotIn("Old story", p202)
        self.assertIn("Noted in the title: MNH, plate.", p202)
        self.assertFalse((out / "item" / "999.html").exists())
        self.assertNotIn("Should never show", self.read(out, "index.html"))

    def test_story_no_source_has_no_source_line(self):
        out = self.build([["301", "Flag Pane of 20 MNH", "Sheets", "", "FIXED_PRICE", "https://www.ebay.com/itm/301"]],
                         stories=[["301", "Flag Pane of 20 MNH", "A cheerful wave of red, white and blue.", "NO SOURCE"]])
        p = self.read(out, "item/301.html")
        self.assertIn("A cheerful wave of red, white and blue.", p)
        self.assertNotIn('class="source"', p)

    def test_story_with_stray_price_stops_the_build(self):
        with self.assertRaises(SystemExit):
            self.build([["401", "Owl Pane of 20 MNH", "Sheets", "", "FIXED_PRICE", "https://www.ebay.com/itm/401"]],
                       stories=[["401", "Owl Pane of 20 MNH", "Yours for $5 today.", "NO SOURCE"]])

    def test_identical_titles_listed_once_with_each_listing_linked(self):
        same = "Scott #1480-1483 1973 8c Boston Tea Party Sheet of 50 MNH"
        out = self.build([["501", same, "Sheets", "", "AUCTION", "https://www.ebay.com/itm/501"],
                          ["502", same, "Sheets", "", "AUCTION", "https://www.ebay.com/itm/502"],
                          ["503", "Other Sheet 1975 MNH", "Sheets", "", "AUCTION", "https://www.ebay.com/itm/503"]])
        home = self.read(out, "index.html")
        self.assertEqual(home.count(f'class="tt" href="item/502.html">{html.escape(same)}</a>'), 1)
        self.assertNotIn(f'class="tt" href="item/501.html"', home)
        self.assertIn('<a href="item/502.html">Listing 1</a>, <a href="item/501.html">Listing 2</a>', home)
        self.assertNotIn("same item", home.lower())
        t501 = re.search(r"<title>(.*?)</title>", self.read(out, "item/501.html")).group(1)
        t502 = re.search(r"<title>(.*?)</title>", self.read(out, "item/502.html")).group(1)
        self.assertNotEqual(t501, t502)

    def test_decades_only_from_a_year_in_the_title(self):
        rows = [[str(600 + i), f"Scott #{1100 + i} 196{i % 10} 4c Sheet of 50 MNH", "Sheets", "", "AUCTION",
                 f"https://www.ebay.com/itm/{600 + i}"] for i in range(build.DECADE_MIN)]
        rows.append(["699", "Mystery Pane MNH", "Sheets", "", "AUCTION", "https://www.ebay.com/itm/699"])
        home = self.read(self.build(rows), "index.html")
        self.assertIn("<h3>1960s</h3>", home)
        self.assertIn("<h3>Year not in the title</h3>", home)
        small = self.read(self.build(rows[:3]), "index.html")
        self.assertNotIn("<h3>", small)

    def test_title_year(self):
        cases = {"Scott #1928 1929 1930 1931 (MNH) 1981 18c American Architecture": 1981,
                 "Scott #4523a 2011 Forever Civil War 1861 Fort Sumter": 2011,
                 "Scott #1199 1200 1201 1202 1962 4c Sheets of 50": 1962,
                 "Scott #1931 Used": None, "Sheet of 50 Plate 1984 MNH": None,
                 "Scott #1480-1483 1973 8c Boston Tea Party": 1973, "Scott #R88c 1862-71 $5 Charter Party": 1862}
        for t, want in cases.items():
            self.assertEqual(build.title_year(t), want, t)


if __name__ == "__main__":
    unittest.main()
