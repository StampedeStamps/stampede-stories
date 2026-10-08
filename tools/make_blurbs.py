"""One-time blurb writer: data/listings.csv -> data/blurbs.csv.

Only states what the title / category / format fields say. No prices, no catalog facts.
"""
import csv, re, sys, zlib

OPEN = [
    "A little something for the album:", "Fresh on the shelf:", "Come say hello to this one:",
    "Pull up a chair for this one:", "Magnifier at the ready:", "Today's stamp story:",
    "Tweezers out, friends:", "Look what turned up:", "Part of the StampedeUSA herd:",
    "Here's one with a story to tell:",
]
CLOSE = [
    "Take a peek on eBay.", "Come see it on eBay.", "Have a look on eBay.", "It's waiting for you on eBay.",
    "Give it a look on eBay and see if it speaks to you.", "Swing by eBay and say hi.",
    "The full details are on eBay.", "Hop over to eBay to see more.",
]
NOTES = [  # (regex on title, phrase) -- phrase restates the title only
    (r"\bMNH\b", "MNH"), (r"\bMNG\b", "MNG"), (r"\bMint\b", "mint"),
    (r"\bUnused\b", "unused"), (r"\bUsed\b", "used"),
    (r"\bPerfin(s)?\b", "perfins"), (r"\bManuscript\b", "manuscript marking"),
    (r"\bPlate\b", "plate"), (r"\bTear Noted\b", "tear noted"),
    (r"\bNo Gum\b", "no gum"), (r"\bSouvenir Sheet\b", "souvenir sheet"),
    (r"\bSe-Tenant\b", "se-tenant"), (r"\bFDC\b", "first day cover"),
]

def blurb(row):
    cat, fmt = row["category"], row["format"]
    h = zlib.crc32(row["item"].encode())
    op, cl = OPEN[h % len(OPEN)], CLOSE[(h >> 8) % len(CLOSE)]
    tags = [p for rx, p in NOTES if re.search(rx, row["title"], re.I)][:3]
    how = "up for auction" if fmt == "AUCTION" else "ready to buy now"
    s = f"{op} filed under {cat}, {how}."
    if tags:
        s += " Noted in the title: " + ", ".join(tags) + "."
    m = re.search(r"Scott\s+#([A-Za-z0-9][A-Za-z0-9\-]*)", row["title"])
    if m:
        s += f" Listed under Scott #{m.group(1)}."
    cond = row["condition"].strip()
    if cond:
        s += f" Condition: {cond}."
    return s + " " + cl

def main():
    rows = list(csv.DictReader(open("data/listings.csv", encoding="utf-8", newline="")))
    with open("data/blurbs.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f); w.writerow(["item", "blurb"])
        for r in rows:
            b = blurb(r)
            for m in re.findall(r"\$\d[\d,]*(?:\.\d+)?", b):
                if m not in r["title"]:
                    sys.exit(f"price-like text in blurb for {r['item']}")
            if "$" in b.replace(r["title"], ""):
                sys.exit(f"stray $ in blurb for {r['item']}")
            w.writerow([r["item"], b])
    print(len(rows), "blurbs")

if __name__ == "__main__":
    main()
