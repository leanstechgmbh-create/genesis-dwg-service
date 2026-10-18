#!/usr/bin/env python3
"""Baut ein AAM-Angebot direkt als schlankes PDF (fpdf2, Core-Fonts ohne
Schrifteinbettung) - rund 7 KB statt 96 KB beim Weg ueber HTML/Chromium.
Layout wie AAM-Rechnung RE260026, eine A4-Seite.

Die Positionsliste EINZELPOSITIONEN (Titel, Kurzbeschreibung, Menge,
Einheit, Einzelpreis) fuer ein neues Angebot einfach ersetzen.
"""
import html
import pathlib
from fpdf import FPDF

import aam_positionen as P
import build_angebote as A

BASE = pathlib.Path(__file__).parent
LOGO = pathlib.Path(__file__).resolve().parent.parent / "vorlagen" / "aam-logo-klein.jpg"
MWST = 0.19

L, R = 16, 194          # linker/rechter Satzspiegel (mm)
COL = {"nr": 16, "bez": 26, "menge": 118, "einheit": 137, "einzel": 152, "gesamt": 172}
BREITE = {"nr": 10, "bez": 92, "menge": 19, "einheit": 15, "einzel": 20, "gesamt": 22}


def t(s):
    """HTML-Entities aufloesen und auf cp1252 reduzieren."""
    s = html.unescape(s)
    ersatz = {"–": "-", "—": "-", "→": "->", "≤": "<=",
              "·": "-", "•": "-", " ": " "}
    for a, b in ersatz.items():
        s = s.replace(a, b)
    return s


def eur(v):
    return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " EUR"


def zahl(v):
    return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


pdf = FPDF(format="A4", unit="mm")
pdf.set_auto_page_break(auto=False)
pdf.add_page()
pdf.set_margins(L, 11, 210 - R)

# ---------------------------------------------------------------- Briefkopf
pdf.image(str(LOGO), x=L, y=11, w=19.6)

pdf.set_font("Helvetica", "B", 10)
pdf.set_xy(L, 11)
for zeile in ["AAM Handwerk&Montage", "Scharnweberstr. 33", "13405 Berlin", "Tel.: +491629825633"]:
    pdf.cell(R - L, 4.6, zeile, align="R", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", "B", 10.5)
pdf.cell(R - L, 5, "info@aam-handwerk-montage.de", align="R", new_x="LMARGIN", new_y="NEXT")

pdf.ln(3)
pdf.set_font("Helvetica", "I", 8)
pdf.cell(0, 4, "AAM Handwerk&Montage * Scharnweberstr. 33 * 13405 Berlin",
         new_x="LMARGIN", new_y="NEXT")

# Empfaenger links, Ort/Datum rechts
y_empf = pdf.get_y() + 1
pdf.set_xy(L, y_empf)
pdf.set_font("Helvetica", "B", 9.6)
for zeile in ["Herrn", "Filip Rimac", t("Kleiststra&szlig;e 1"), "10787 Berlin"]:
    pdf.cell(90, 4.8, zeile, new_x="LMARGIN", new_y="NEXT")
pdf.set_xy(120, y_empf)
pdf.set_font("Helvetica", "", 10)
pdf.cell(45, 4.8, "Berlin ", align="R")
pdf.set_font("Helvetica", "I", 9.6)
pdf.cell(29, 4.8, "05.08.26", align="R", new_x="LMARGIN", new_y="NEXT")

# ------------------------------------------------------------- Dokumentkopf
pdf.set_y(max(pdf.get_y(), y_empf + 19.2) + 5)
pdf.set_font("Helvetica", "B", 9.6)
pdf.cell(0, 5, "Angebot", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", "", 9.4)
for zeile in ["Angebotsnummer: AN260027",
              "Kst.Nr.: /",
              t("Bauvorhaben: Hotel, Kleiststra&szlig;e 1, 10787 Berlin"),
              "Fabrikat: Geberit Silent-db20",
              t("G&uuml;ltig bis: 30.09.2026")]:
    pdf.cell(0, 4.4, zeile, new_x="LMARGIN", new_y="NEXT")

# ----------------------------------------------------------------- Tabelle
pdf.ln(3)
kopf_y = pdf.get_y()
pdf.set_font("Helvetica", "B", 9.4)
pdf.set_xy(COL["nr"], kopf_y);      pdf.cell(BREITE["nr"], 5, "Pos.")
pdf.set_xy(COL["bez"], kopf_y);     pdf.cell(BREITE["bez"], 5, "Bezeichnung")
pdf.set_xy(COL["menge"], kopf_y);   pdf.cell(BREITE["menge"], 5, "Menge", align="R")
pdf.set_xy(COL["einheit"], kopf_y); pdf.cell(BREITE["einheit"], 5, "Einheit", align="R")
pdf.set_xy(COL["einzel"], kopf_y);  pdf.cell(BREITE["einzel"], 5, "Einzel EUR", align="R")
pdf.set_xy(COL["gesamt"], kopf_y);  pdf.cell(BREITE["gesamt"], 5, "Gesamt EUR", align="R")
pdf.set_line_width(0.3)
pdf.line(L, kopf_y + 5.4, R, kopf_y + 5.4)
pdf.set_y(kopf_y + 6.4)

# Abschnittszeile
pdf.set_font("Helvetica", "B", 9.4)
pdf.set_x(COL["bez"])
pdf.cell(0, 4.8, "Schmutzwasserleitung Geberit Silent-db20, DN 100", new_x="LMARGIN", new_y="NEXT")
pdf.set_x(L)
pdf.line(L, pdf.get_y(), R, pdf.get_y())
pdf.ln(1)

netto = 0.0
for i, (titel, besch, menge, einheit, ep) in enumerate(P.EINZELPOSITIONEN, start=1):
    betrag = round(menge * ep, 2)
    netto += betrag
    y0 = pdf.get_y()

    pdf.set_font("Helvetica", "B", 9.4)
    pdf.set_xy(COL["nr"], y0)
    pdf.cell(BREITE["nr"], 4.2, str(i), align="C")
    pdf.set_xy(COL["bez"], y0)
    pdf.multi_cell(BREITE["bez"], 4.2, t(titel))

    pdf.set_font("Helvetica", "", 7.2)
    pdf.set_x(COL["bez"])
    pdf.multi_cell(BREITE["bez"], 3.1, t(besch))
    y_ende = pdf.get_y()

    pdf.set_font("Helvetica", "", 9.4)
    pdf.set_xy(COL["menge"], y0);   pdf.cell(BREITE["menge"], 4.2, zahl(menge), align="R")
    pdf.set_xy(COL["einheit"], y0); pdf.cell(BREITE["einheit"], 4.2, einheit, align="R")
    pdf.set_xy(COL["einzel"], y0);  pdf.cell(BREITE["einzel"], 4.2, eur(ep), align="R")
    pdf.set_xy(COL["gesamt"], y0);  pdf.cell(BREITE["gesamt"], 4.2, eur(betrag), align="R")

    pdf.set_y(y_ende + 0.8)
    pdf.set_draw_color(200, 200, 200)
    pdf.set_line_width(0.15)
    pdf.line(L, pdf.get_y(), R, pdf.get_y())
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.3)
    pdf.set_y(pdf.get_y() + 1.2)

netto = round(netto, 2)
mwst = round(netto * MWST, 2)
brutto = round(netto + mwst, 2)

# ----------------------------------------------------------------- Summen
pdf.ln(2)
def summenzeile(label, wert, fett=False, linie_oben=False):
    if linie_oben:
        pdf.line(112, pdf.get_y(), R, pdf.get_y())
        pdf.ln(1.2)
    pdf.set_font("Helvetica", "B" if fett else "", 9.6)
    pdf.set_x(112)
    pdf.cell(58, 5, label)
    pdf.cell(24, 5, eur(wert), align="R", new_x="LMARGIN", new_y="NEXT")

summenzeile("Gesamtbetrag Netto", netto, fett=True)
summenzeile("zzgl. 19% MwSt", mwst)
summenzeile("Angebotsbetrag", brutto, fett=True, linie_oben=True)

# ---------------------------------------------------------------- Hinweise
pdf.ln(3)
hinweis = t(
    f"{P.TECHHINWEIS} Grundlage: Aufma&szlig; vom 05.08.2026 (DB 20); Befestigung 1 Systemrohrschelle "
    f"je 1,00 m Leitung ({zahl(A.GESAMT_M)} m inkl. Formst&uuml;ckbaul&auml;ngen), Spannverbinder "
    f"kalkulatorisch - Abrechnung nach Aufma&szlig;. Nicht enthalten: Brandschutz, Kernbohrungen, "
    f"Ger&uuml;st, Stemm- und Schlitzarbeiten. Angebot freibleibend, g&uuml;ltig bis 30.09.2026.")
pdf.set_font("Helvetica", "", 7.4)
pdf.set_text_color(60, 60, 60)
pdf.multi_cell(R - L, 3.3, hinweis, new_x="LMARGIN", new_y="NEXT")
pdf.set_text_color(0, 0, 0)

# ---------------------------------------------------------------- Fussblock
fuss_y = max(pdf.get_y() + 5, 262)
pdf.set_draw_color(150, 150, 150)
pdf.set_line_width(0.2)
pdf.line(L, fuss_y, R, fuss_y)
pdf.set_draw_color(0, 0, 0)
pdf.set_font("Helvetica", "", 8)
spalten = [
    (L, "L", ["AAM Handwerk&Montage", "Scharnweberstr. 33", "13405 Berlin", "Tel.: +491629825633"]),
    (L, "C", ["USt-IdNr.: DE460797759", "Steuernummer: 17/484/02061"]),
    (L, "R", ["Mahit Ramovic", "Commerzbank", "IBAN: DE80 1004 0000 0792 1190 00", "BIC: COBADEFFXXX"]),
]
for x, align, zeilen in spalten:
    y = fuss_y + 2
    for zeile in zeilen:
        pdf.set_xy(x, y)
        pdf.cell(R - L, 3.8, zeile, align=align)
        y += 3.8

ziel = BASE / "AAM Angebot AN260027 - Hotel Kleiststrasse - 11.112,87 EUR.pdf"
pdf.output(str(ziel))
print(f"PDF: {ziel.name} | {ziel.stat().st_size} Bytes")
print(f"netto {zahl(netto)} | MwSt {zahl(mwst)} | brutto {zahl(brutto)}")
