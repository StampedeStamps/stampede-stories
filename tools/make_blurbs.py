"""Blurb writer for Stamp Stories.

build.py calls blurb() for every listing on every build, so each page's blurb always matches the
listing's current title, category and format. Running this file writes data/blurbs.csv (item,blurb),
a snapshot of the same text for review; the site does not read it.

Only states what the title / category / format fields say. No prices, no catalog facts.
"""
import csv, re, sys, zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

OPEN = [
    "A little something for the album:", "Fresh on the shelf:", "Come say hello to this one:",
    "Pull up a chair for this one:", "Magnifier at the ready:", "Today's stamp story:",
    "Tweezers out, friends:", "Look what turned up:", "Part of the StampedeUSA herd:",
    "Here's one with a story to tell:",
]
WHERE = ["filed under {cat}", "found in our {cat} section", "part of our {cat} selection", "on the {cat} shelf"]
HOW = {"AUCTION": ["up for auction", "open for bids"], "FIXED_PRICE": ["ready to buy now", "available to buy now"]}
CLOSE = [
    "Take a peek on eBay.", "Come see it on eBay.", "Have a look on eBay.", "It's waiting for you on eBay.",
    "Give it a look on eBay and see if it speaks to you.", "Swing by eBay and say hi.",
    "The full details are on eBay.", "Hop over to eBay to see more.",
]
NOTES = [  # (regex on title, phrase) -- phrase restates a word the title itself uses
    (r"\bMNH\b", "MNH"), (r"\bMNG\b", "MNG"), (r"\bMint\b", "mint"),
    (r"\bUnused\b", "unused"), (r"\bUsed\b", "used"),
    (r"\bPerfins\b", "perfins"), (r"\bPerfin\b", "perfin"), (r"\bManuscript\b", "manuscript marking"),
    (r"(?<!Flat )\bPlate\b", "plate"), (r"\bTear Noted\b", "tear noted"),
    (r"\bNo Gum\b", "no gum"), (r"\bSouvenir Sheet\b", "souvenir sheet"),
    (r"\bSe-Tenant\b", "se-tenant"), (r"\bFDC\b", "first day cover"),
]


def category(row):
    """The category as shown everywhere on the site; a blank one is filed under "Other"."""
    return (row.get("category") or "").strip() or "Other"


def blurb(row):
    cat = category(row)
    fmt = (row.get("format") or "").strip().upper()
    h = zlib.crc32(row["item"].encode())
    op, cl = OPEN[h % len(OPEN)], CLOSE[(h >> 8) % len(CLOSE)]
    where = WHERE[(h >> 16) % len(WHERE)].format(cat=cat)
    hows = HOW.get(fmt)  # an unknown format gets no auction/buy-now claim at all
    tags = [p for rx, p in NOTES if re.search(rx, row["title"], re.I)][:3]
    s = f"{op} {where}, {hows[(h >> 20) % len(hows)]}." if hows else f"{op} {where}."
    if tags:
        s += " Noted in the title: " + ", ".join(tags) + "."
    cond = (row.get("condition") or "").strip()
    if cond:
        s += f" Condition: {cond}."
    return s + " " + cl


def check(row, b):
    """Stop if a blurb carries a dollar amount that is not copied from its own title."""
    for m in re.findall(r"\$\d[\d,]*(?:\.\d+)?", b):
        if m not in row["title"]:
            sys.exit(f"price-like text in blurb for {row['item']}")
    if "$" in b.replace(row["title"], ""):
        sys.exit(f"stray $ in blurb for {row['item']}")


def main():
    with open(ROOT / "data" / "listings.csv", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    with open(ROOT / "data" / "blurbs.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["item", "blurb"])
        for r in rows:
            b = blurb(r)
            check(r, b)
            w.writerow([r["item"], b])
    print(len(rows), "blurbs")


if __name__ == "__main__":
    main()
