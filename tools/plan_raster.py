"""Gitternetz mit Feldbezeichnungen (A1, B2, C3 ...) ueber Planblaetter legen.

Damit lassen sich Stellen im Plan eindeutig benennen ("der Speicher in C3").
Quelle: PDF (alle Seiten) oder einzelne Bilddateien.

Aufruf:
    python3 tools/plan_raster.py plan.pdf [ausgabeordner] [--zelle 100] [--dpi 130]
    python3 tools/plan_raster.py blatt.png [ausgabeordner]

--zelle ist die Kantenlaenge eines Rasterfeldes in Millimetern auf dem
Originalplan (Standard 100 mm). Spalten werden mit Buchstaben, Zeilen mit
Zahlen bezeichnet; die Beschriftung liegt in einem weissen Randstreifen und
wird oben/unten sowie links/rechts wiederholt.
"""
import os
import sys
import math

from PIL import Image, ImageDraw, ImageFont

RASTER = (230, 0, 120)      # Magenta: auf Bauplaenen gut sichtbar, kein Schwarz
DECKKRAFT = 105
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def spaltenname(i):
    """0 -> A, 25 -> Z, 26 -> AA"""
    name = ""
    while True:
        name = chr(ord("A") + i % 26) + name
        i = i // 26 - 1
        if i < 0:
            return name


def raster_ueberlagern(img, zelle_px, rand=None):
    """Gibt ein neues Bild mit Randstreifen, Rasterlinien und Feldnamen zurueck."""
    if img.mode != "RGB":
        img = img.convert("RGB")
    w, h = img.size
    rand = rand or max(46, int(zelle_px * 0.13))
    spalten = math.ceil(w / zelle_px)
    zeilen = math.ceil(h / zelle_px)

    blatt = Image.new("RGB", (w + 2 * rand, h + 2 * rand), "white")
    blatt.paste(img, (rand, rand))

    linien = Image.new("RGBA", blatt.size, (0, 0, 0, 0))
    zeichner = ImageDraw.Draw(linien)
    for c in range(spalten + 1):
        x = rand + min(c * zelle_px, w)
        zeichner.line([(x, rand), (x, rand + h)], fill=RASTER + (DECKKRAFT,), width=2)
    for r in range(zeilen + 1):
        y = rand + min(r * zelle_px, h)
        zeichner.line([(rand, y), (rand + w, y)], fill=RASTER + (DECKKRAFT,), width=2)
    blatt = Image.alpha_composite(blatt.convert("RGBA"), linien).convert("RGB")

    schrift = ImageFont.truetype(FONT_BOLD, int(rand * 0.62))
    beschriftung = ImageDraw.Draw(blatt)
    for c in range(spalten):
        x = rand + min(c * zelle_px + zelle_px / 2, w - (w % zelle_px or zelle_px) / 2)
        for y in (rand / 2, rand + h + rand / 2):
            beschriftung.text((x, y), spaltenname(c), font=schrift,
                              fill=RASTER, anchor="mm")
    for r in range(zeilen):
        y = rand + min(r * zelle_px + zelle_px / 2, h - (h % zelle_px or zelle_px) / 2)
        for x in (rand / 2, rand + w + rand / 2):
            beschriftung.text((x, y), str(r + 1), font=schrift,
                              fill=RASTER, anchor="mm")
    return blatt


def aus_pdf(pfad, ordner, zelle_mm, dpi):
    import pymupdf
    doc = pymupdf.open(pfad)
    zelle_px = int(zelle_mm / 25.4 * dpi)
    basis = os.path.splitext(os.path.basename(pfad))[0]
    erzeugt = []
    for nr, seite in enumerate(doc, 1):
        pix = seite.get_pixmap(dpi=dpi)
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        out = os.path.join(ordner, f"{basis}_S{nr}_raster.png")
        raster_ueberlagern(img, zelle_px).save(out)
        erzeugt.append(out)
    return erzeugt


def aus_bild(pfad, ordner, zelle_mm, dpi):
    img = Image.open(pfad)
    zelle_px = int(zelle_mm / 25.4 * dpi)
    basis = os.path.splitext(os.path.basename(pfad))[0]
    out = os.path.join(ordner, f"{basis}_raster.png")
    raster_ueberlagern(img, zelle_px).save(out)
    return [out]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    opt = {a.split("=")[0]: a.split("=")[1] for a in sys.argv[1:] if "=" in a and a.startswith("--")}
    if not args:
        print(__doc__)
        return
    quelle = args[0]
    ordner = args[1] if len(args) > 1 else "."
    zelle_mm = float(opt.get("--zelle", 100))
    dpi = int(opt.get("--dpi", 130))
    os.makedirs(ordner, exist_ok=True)

    fn = aus_pdf if quelle.lower().endswith(".pdf") else aus_bild
    for pfad in fn(quelle, ordner, zelle_mm, dpi):
        print(f"geschrieben: {pfad}")


if __name__ == "__main__":
    main()
