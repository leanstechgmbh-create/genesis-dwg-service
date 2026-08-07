#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Schlanker Angebots-PDF-Generator (LEANS Tech GmbH).

Erzeugt Angebote im verbindlichen Design von vorlagen/angebot-muster.html
(blauer Kopf #1a5276, Meta-Raster, Positionstabelle, blauer Summenkasten,
kursiver Hinweisblock, zentrierte Fußzeile) — aber mit PDF-Kernschriften
statt eingebetteter Fonts. Ergebnis: ~20 KB statt ~250 KB pro PDF, damit
die Dateien als E-Mail-Anhang in Entwürfe passen (Gmail-Connector).

Aufruf:  python3 tools/angebot_pdf.py daten.json ausgabe.pdf
JSON-Schema: siehe BEISPIEL am Dateiende.
"""
import json
import sys

from fpdf import FPDF

BLAU = (26, 82, 118)        # #1a5276
DUNKEL = (52, 73, 94)       # #34495e
GRAU = (85, 85, 85)
HELLGRAU = (136, 136, 136)
ZEILE = (221, 221, 238)     # #dde
SEC_BG = (240, 244, 249)

# Spaltenbreiten der Positionstabelle (Summe = 180 mm Satzspiegel)
COLS = [8, 11, 89, 12, 12, 19, 20, 9]
ALIGN = ["C", "L", "L", "R", "L", "R", "R", "C"]


def eur(v):
    return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " €"


# Kernschriften können nur cp1252 — Zeichen außerhalb (z. B. ć in „Redžić")
# werden auf das nächstliegende Zeichen abgebildet.
_ERSATZ = str.maketrans({"ć": "c", "Ć": "C", "č": "c", "Č": "C",
                         "đ": "d", "Đ": "D", "ş": "s", "Ş": "S"})


def _text(v):
    if isinstance(v, str):
        s = v.translate(_ERSATZ)
        return s.encode("cp1252", errors="replace").decode("cp1252")
    if isinstance(v, list):
        return [_text(x) for x in v]
    if isinstance(v, dict):
        return {k: _text(x) for k, x in v.items()}
    return v


class AngebotPDF(FPDF):
    def __init__(self, daten):
        super().__init__("P", "mm", "A4")
        self.core_fonts_encoding = "cp1252"
        self.daten = _text(daten)
        self.set_margins(15, 12, 15)
        self.set_auto_page_break(True, margin=22)

    def footer(self):
        self.set_y(-16)
        self.set_draw_color(204, 204, 204)
        self.line(15, self.get_y(), 195, self.get_y())
        self.set_y(-14)
        self.set_font("helvetica", "", 6.5)
        self.set_text_color(153, 153, 153)
        self.cell(0, 4, self.daten["fusszeile"], align="C")

    def kopf(self):
        d = self.daten
        y0 = self.get_y()
        if d.get("logo"):
            self.image(d["logo"], x=15, y=y0, h=17)
        self.set_xy(15, y0 + 18.5)
        self.set_font("helvetica", "", 7)
        self.set_text_color(102, 102, 102)
        self.cell(120, 3.5, d["absenderzeile"])
        self.set_xy(115, y0)
        self.set_font("helvetica", "B", 7.5)
        self.set_text_color(26, 26, 26)
        self.cell(80, 3.8, "An:", align="R", new_x="LMARGIN", new_y="NEXT")
        self.set_font("helvetica", "", 7.5)
        for zeile in d["kunde"]:
            self.set_x(115)
            self.cell(80, 3.8, zeile, align="R", new_x="LMARGIN", new_y="NEXT")
        self.set_y(max(self.get_y(), y0 + 23))
        self.set_draw_color(*BLAU)
        self.set_line_width(0.9)
        self.line(15, self.get_y(), 195, self.get_y())
        self.set_line_width(0.2)
        self.ln(4)
        self.set_font("helvetica", "B", 17)
        self.set_text_color(*BLAU)
        self.set_char_spacing(1.2)
        self.cell(0, 8, "ANGEBOT", new_x="LMARGIN", new_y="NEXT")
        self.set_char_spacing(0)
        self.ln(2)

    def meta(self):
        for label, wert in self.daten["meta"]:
            self.set_font("helvetica", "B", 8)
            self.set_text_color(*DUNKEL)
            self.cell(45, 4.4, label)
            self.set_font("helvetica", "", 8)
            self.set_text_color(26, 26, 26)
            self.multi_cell(135, 4.4, wert, new_x="LMARGIN", new_y="NEXT")
        self.ln(2.5)

    def tabellenkopf(self):
        self.set_font("helvetica", "B", 7.3)
        self.set_fill_color(*BLAU)
        self.set_text_color(255, 255, 255)
        titel = ["Nr.", "OZ", "Beschreibung", "Menge", "Einh.",
                 "EP netto", "Betrag netto", "MwSt"]
        for w, t, a in zip(COLS, titel, ALIGN):
            self.cell(w, 5.5, t, fill=True, align="R" if a == "R" else "L")
        self.ln()

    def position(self, p):
        besch = p["titel"] + "\n" + p.get("beschreibung", "")
        tech = p.get("technik", "")
        # Höhe vorab bestimmen
        self.set_font("helvetica", "", 7.3)
        h_besch = len(self.multi_cell(COLS[2] - 2, 3.4, besch, dry_run=True,
                                      output="LINES")) * 3.4
        h_tech = 0
        if tech:
            self.set_font("helvetica", "", 6.4)
            h_tech = len(self.multi_cell(COLS[2] - 2, 3.0, tech, dry_run=True,
                                         output="LINES")) * 3.0
        h = max(h_besch + h_tech + 2.4, 8)
        if self.get_y() + h > self.page_break_trigger:
            self.add_page()
            self.tabellenkopf()
        x0, y0 = self.get_x(), self.get_y()
        self.set_draw_color(*ZEILE)
        self.set_text_color(26, 26, 26)
        werte = [str(p["nr"]), p["oz"], "", p["menge"], p["einheit"],
                 eur(p["ep"]), eur(p["betrag"]), p.get("mwst", "19%")]
        x = x0
        for i, (w, v, a) in enumerate(zip(COLS, werte, ALIGN)):
            self.set_xy(x, y0)
            fett = "B" if i == 6 else ""
            self.set_font("helvetica", fett, 7.3)
            self.cell(w, h, "", border=1)
            self.set_xy(x + 1, y0 + 1.2)
            self.cell(w - 2, 3.4, v, align=a)
            x += w
        # Beschreibung mehrzeilig in Spalte 3
        bx = x0 + COLS[0] + COLS[1]
        self.set_xy(bx + 1, y0 + 1.2)
        self.set_font("helvetica", "B", 7.3)
        self.multi_cell(COLS[2] - 2, 3.4, p["titel"])
        self.set_xy(bx + 1, self.get_y())
        self.set_font("helvetica", "", 7.3)
        if p.get("beschreibung"):
            self.multi_cell(COLS[2] - 2, 3.4, p["beschreibung"])
        if tech:
            self.set_xy(bx + 1, self.get_y() + 0.4)
            self.set_font("helvetica", "", 6.4)
            self.set_text_color(*GRAU)
            self.multi_cell(COLS[2] - 2, 3.0, tech)
            self.set_text_color(26, 26, 26)
        self.set_xy(x0, y0 + h)

    def summen(self):
        s = self.daten["summen"]
        breite, x = 90, 105
        if self.get_y() + 30 > self.page_break_trigger:
            self.add_page()
        self.ln(4)
        y0 = self.get_y()
        self.set_x(x)
        zeilen = [("Nettobetrag:", eur(s["netto"]), False),
                  (s.get("ust_label", "zzgl. USt 19 %:"), eur(s["ust"]), False),
                  ("Gesamtbetrag:", eur(s["gesamt"]), True)]
        for label, wert, final in zeilen:
            self.set_x(x)
            if final:
                self.set_fill_color(*BLAU)
                self.set_text_color(255, 255, 255)
                self.set_font("helvetica", "B", 10)
                self.cell(breite / 2, 8, " " + label, fill=True)
                self.cell(breite / 2, 8, wert + " ", align="R", fill=True,
                          new_x="LMARGIN", new_y="NEXT")
            else:
                self.set_text_color(26, 26, 26)
                self.set_font("helvetica", "", 8.5)
                self.cell(breite / 2, 7, " " + label)
                self.cell(breite / 2, 7, wert + " ", align="R",
                          new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(*BLAU)
        self.set_line_width(0.5)
        self.rect(x, y0, breite, 22)
        self.set_line_width(0.2)

    def hinweise(self):
        self.ln(5)
        self.set_draw_color(238, 238, 238)
        self.line(15, self.get_y(), 195, self.get_y())
        self.ln(2)
        self.set_font("helvetica", "I", 7)
        self.set_text_color(*HELLGRAU)
        for zeile in self.daten["hinweise"]:
            self.multi_cell(180, 3.4, zeile, new_x="LMARGIN", new_y="NEXT")

    def erzeuge(self, ziel):
        self.add_page()
        self.kopf()
        self.meta()
        self.tabellenkopf()
        for p in self.daten["positionen"]:
            self.position(p)
        self.summen()
        self.hinweise()
        self.output(ziel)


def main():
    if len(sys.argv) != 3:
        sys.exit("Aufruf: angebot_pdf.py daten.json ausgabe.pdf")
    with open(sys.argv[1], encoding="utf-8") as f:
        daten = json.load(f)
    AngebotPDF(daten).erzeuge(sys.argv[2])
    print("geschrieben:", sys.argv[2])


BEISPIEL = {
    "logo": "vorlagen/leans-logo.png",
    "absenderzeile": "Semir Redžić • Berlepschstr. 165 • 14165 Berlin • "
                     "Tel: +49 170 828 0836 • info@leanstech-gmbh.de",
    "kunde": ["Firma GmbH", "Straße 1", "12345 Berlin"],
    "meta": [["Angebotsnummer:", "999"], ["Angebotsdatum:", "1. Januar 2026"]],
    "positionen": [{"nr": 1, "oz": "1.1.", "titel": "Position",
                    "beschreibung": "Text", "technik": "Details",
                    "menge": "1", "einheit": "Stk", "ep": 100.0,
                    "betrag": 100.0, "mwst": "19%"}],
    "summen": {"netto": 100.0, "ust_label": "zzgl. USt 19 %:",
               "ust": 19.0, "gesamt": 119.0},
    "hinweise": ["Dieses Angebot ist freibleibend."],
    "fusszeile": "LEANS Tech GmbH • Berlepschstr. 165, 14165 Berlin • ...",
}

if __name__ == "__main__":
    main()
