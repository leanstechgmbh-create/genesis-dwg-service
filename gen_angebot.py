#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LEANS-Tech-Angebot als PDF im Original-Template (Layout von Angebot 297).
US-Letter, Logo, dunkelblaue Tabellenkopfzeile, Spalten OZ..MwSt, Summenblock, AGB-Seite.
Positionsdaten unten anpassen und ausfuehren."""
from fpdf import FPDF

FD = "/usr/share/fonts/truetype/liberation"
LOGO = "leans_logo.png"

# ===================== ANGEBOTSDATEN =====================
NR = "283"
DATUM = "20. Juni 2026"
GUELTIG = "20. September 2026"
EMPF = ["Vape 4 me", "Güntzelstraße 10", "10717 Berlin"]
LEISTUNG = ("Montage Wandgerät (Außen- und Innengeräte) inkl. Inbetriebnahme, Kältemittel- "
            "und Kondensatleitung – Gerät bauseits gestellt")
GEWERK = "Klimatisierung / Kältetechnik (KG 430)"
FABRIKAT = "Gerät bauseits gestellt (kundenseitig)"
SECTION = "1. KLIMATISIERUNG – MONTAGE WANDGERÄT (GERÄT BAUSEITS)"
# OZ, Titel, Sub-Beschreibung, Menge, Einheit, EP, Betrag
POS = [
    ("1.1", "Montage Außengerät inkl. Inbetriebnahme",
     "Montage des Außengeräts (Gerät bauseits gestellt), elektrischer Anschluss, Vakuumieren, "
     "Dichtheitsprüfung, Inbetriebnahme der Gesamtanlage sowie Einweisung in die Bedienung.",
     "1,00", "pschl.", "1.200,00", "1.200,00 €"),
    ("1.2", "Montage Innengeräte (Wandgeräte)",
     "Montage der Innen-Wandgeräte (Gerät bauseits gestellt) inkl. Wanddurchbruch, Befestigung "
     "und Anschluss • Preis je Innengerät.",
     "2,00", "Stk", "825,00", "1.650,00 €"),
    ("1.3", "Kabel-Komfortfernbedienung",
     "Verdrahtete Komfort-Fernbedienung, Lieferung, Montage und Anschluss.",
     "1,00", "Stk", "97,00", "97,00 €"),
    ("1.4", "Cu-Kältemittelleitungssatz, vorisoliert, passend zum Gerät",
     "Kupferrohr weich nach DIN EN 12735-1, inkl. Armaflex-Dämmung, Schellen und Befestigung • "
     "Dimension passend zum Gerät • Lieferung und Montage.",
     "15,00", "m", "66,30", "994,50 €"),
    ("1.5", "Kondensatleitung DN16, flexibel",
     "Inkl. Gefällesicherung und Anschluss • Lieferung und Montage.",
     "15,00", "m", "22,00", "330,00 €"),
]
NETTO = "4.271,50 €"
MWST_LBL = "19%"
MWST = "811,59 €"
BRUTTO = "5.083,09 €"
LEISTUNGSUMFANG = ("Betriebsfertige Montage eines Klima-Wandgeräts (Außengerät und zwei "
    "Innengeräte) inkl. Inbetriebnahme und Dichtheitsprüfung, 15 m vorisolierte "
    "Kältemittelleitung und 15 m Kondensatleitung. Das Klimagerät wird bauseits gestellt. "
    "Gleichwertige Ausführungsvarianten vorbehalten.")
OUT = "Angebot_283_2x_Wandgeraet_3.5kW.pdf"
# Stabiler Drive-Titel je Angebot (KEINE Summe -> Iteration ueberschreibt dieselbe Datei)
DRIVE_TITLE = f"ANGEBOT {NR} - LEANS Tech GmbH - 2x Wandgeraet 3.5kW.pdf"
# =========================================================

BLUE = (26, 82, 118)
SECTION_BG = (234, 241, 248)
LINE_LT = (224, 231, 239)
DARK = (17, 17, 17)
GREY = (90, 90, 90)
WHITE = (255, 255, 255)

# Spaltengrenzen (pt)
L, R = 54, 558
C = {"oz": 54, "bes": 76, "menge": 365, "einh": 399, "ep": 430, "bet": 472, "mwst": 528}
BESW = C["menge"] - C["bes"] - 8  # Textbreite Beschreibung


class PDF(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="pt", format=(612, 792))
        self.add_font("Lib", "", f"{FD}/LiberationSans-Regular.ttf")
        self.add_font("Lib", "B", f"{FD}/LiberationSans-Bold.ttf")
        self.add_font("Lib", "I", f"{FD}/LiberationSans-Italic.ttf")
        self.set_auto_page_break(False)

    def t(self, x, y, s, size, style="", color=DARK, align="L", w=None):
        self.set_font("Lib", style, size)
        self.set_text_color(*color)
        if align == "L" and w is None:
            self.text(x, y, s)
        else:
            self.set_xy(x, y - size)
            self.cell(w if w else 0, size, s, align=align)


pdf = PDF()
pdf.add_page()

# ---- Logo (groesser, Schriftzug klar lesbar) ----
pdf.image(LOGO, x=54, y=50, w=116, h=78)

# ---- Empfaenger (rechtsbuendig auf R) ----
pdf.t(0, 63, "An:", 7.9, "B", DARK, align="R", w=R)
yy = 72
for line in EMPF:
    pdf.t(0, yy, line, 7.9, "", DARK, align="R", w=R)
    yy += 9

# ---- Absenderzeile + Akzentbalken ----
pdf.t(L, 142, "LEANS Tech GmbH • Berlepschstr. 165 • 14165 Berlin • Tel: +49 170 828 0836 • "
              "info@leanstech-gmbh.de", 7.5, "", GREY)
pdf.set_fill_color(*BLUE)
pdf.rect(L, 152, R - L, 2.2, style="F")

# ---- Titel ----
pdf.t(L, 178, "ANGEBOT", 18, "B", DARK)

# ---- Meta ----
pdf.t(L, 199, f"Angebotsnummer: {NR}", 8.6, "B", DARK)
pdf.t(L, 211, f"Angebotsdatum: {DATUM}", 8.6, "B", DARK)
pdf.t(L, 223, f"Gültig bis: {GUELTIG}", 8.6, "B", DARK)
# Leistung (kann umbrechen)
pdf.set_font("Lib", "B", 8.6)
pdf.set_text_color(*DARK)
pdf.set_xy(L, 228)
pdf.multi_cell(R - L, 11, f"Leistung: {LEISTUNG}", align="L")
y = pdf.get_y() + 1
pdf.t(L, y + 8.6, f"Gewerk: {GEWERK}", 8.6, "B", DARK)
pdf.t(L, y + 20.6, f"Fabrikat: {FABRIKAT}", 8.6, "B", DARK)
y = y + 26

# ---- Tabellenkopf (dunkelblau) ----
hy = y + 6
hh = 16
pdf.set_fill_color(*BLUE)
pdf.rect(L, hy, R - L, hh, style="F")
hb = hy + 11
pdf.t(C["oz"] + 5, hb, "OZ", 7.9, "B", WHITE)
pdf.t(C["bes"] + 5, hb, "Beschreibung", 7.9, "B", WHITE)
pdf.t(0, hb, "Menge", 7.9, "B", WHITE, align="R", w=C["einh"] - 6)
pdf.t(C["einh"] + 4, hb, "Einh.", 7.9, "B", WHITE)
pdf.t(0, hb, "EP netto", 7.9, "B", WHITE, align="R", w=C["bet"] - 4)
pdf.t(0, hb, "Betrag netto", 7.9, "B", WHITE, align="R", w=C["mwst"] - 4)
pdf.t(C["mwst"] + 5, hb, "MwSt", 7.9, "B", WHITE)
y = hy + hh

# ---- Abschnittszeile (hellblau) ----
sh = 17
pdf.set_fill_color(*SECTION_BG)
pdf.rect(L, y, R - L, sh, style="F")
pdf.t(C["oz"] + 6, y + 12, SECTION, 8.6, "B", BLUE)
y = y + sh + 4

# ---- Positionen ----
for oz, titel, sub, menge, einh, ep, betrag in POS:
    ytop = y
    # Hauptzeile
    pdf.t(C["oz"] + 6, ytop + 8, oz, 7.9, "", DARK)
    pdf.t(C["bes"] + 6, ytop + 8, titel, 7.9, "B", DARK)
    pdf.t(0, ytop + 8, menge, 7.9, "", DARK, align="R", w=C["einh"] - 6)
    pdf.t(C["einh"] + 4, ytop + 8, einh, 7.9, "", DARK)
    pdf.t(0, ytop + 8, ep, 7.9, "", DARK, align="R", w=C["bet"] - 4)
    pdf.t(0, ytop + 8, betrag, 7.9, "", DARK, align="R", w=C["mwst"] - 4)
    pdf.t(C["mwst"] + 5, ytop + 8, MWST_LBL, 7.9, "", GREY)
    # Sub-Beschreibung
    pdf.set_font("Lib", "", 7.1)
    pdf.set_text_color(*GREY)
    pdf.set_xy(C["bes"] + 6, ytop + 12)
    pdf.multi_cell(BESW, 9, sub, align="L")
    y = pdf.get_y() + 6
    pdf.set_draw_color(*LINE_LT)
    pdf.set_line_width(0.5)
    pdf.line(L, y - 3, R, y - 3)

# ---- Summen (rechter Block 237..556) ----
TB_L, TB_R = 237, 556
lab_x = 247
y += 8
pdf.t(lab_x, y + 10, "Nettobetrag", 9.0, "", DARK)
pdf.t(0, y + 10, NETTO, 9.0, "", DARK, align="R", w=TB_R - 6)
y += 24
pdf.set_draw_color(*LINE_LT); pdf.set_line_width(0.6); pdf.line(TB_L, y, TB_R, y)
pdf.t(lab_x, y + 13, "zzgl. 19 % MwSt", 9.0, "", DARK)
pdf.t(0, y + 13, MWST, 9.0, "", DARK, align="R", w=TB_R - 6)
y += 23
# Gesamt (dunkelblauer Balken)
gh = 26
pdf.set_fill_color(*BLUE)
pdf.rect(TB_L, y, TB_R - TB_L, gh, style="F")
pdf.t(lab_x, y + 17, "Gesamtbetrag (brutto)", 9.7, "B", WHITE)
pdf.t(0, y + 17, BRUTTO, 9.7, "B", WHITE, align="R", w=TB_R - 6)

# ===================== SEITE 2 — AGB / Hinweise =====================
pdf.add_page()
pdf.set_xy(L, 60)
pdf.set_font("Lib", "I", 7.5)
pdf.set_text_color(*DARK)
pdf.multi_cell(R - L, 11, f"Leistungsumfang: {LEISTUNGSUMFANG}", align="L")
pdf.ln(6)
pdf.set_x(L)
pdf.multi_cell(R - L, 11,
    "Alle Preise verstehen sich netto zzgl. der gesetzlichen Umsatzsteuer von 19 %. "
    "Der Gesamtbetrag (brutto) enthält die ausgewiesene Umsatzsteuer.", align="L")
pdf.ln(6)
pdf.set_x(L)
pdf.multi_cell(R - L, 11, f"Dieses Angebot ist freibleibend und gültig bis {GUELTIG}.", align="L")

# Fusszeile Seite 2 (unten)
pdf.set_xy(L, 760)
pdf.set_font("Lib", "I", 6.7)
pdf.set_text_color(*GREY)
pdf.multi_cell(R - L, 9,
    "LEANS Tech GmbH • Berlepschstr. 165, 14165 Berlin • HRB 249080 B • "
    "USt-IdNr: DE357948720 • IBAN: DE24 1001 9000 1000 0012 17 • Adyen Bank • BIC: ADYBDEB2XXX",
    align="L")

pdf.output(OUT)
print("OK ->", OUT)

# Immer zusaetzlich in Downloads ablegen
import os, shutil
dl = os.path.expanduser("~/Downloads")
os.makedirs(dl, exist_ok=True)
dst = os.path.join(dl, OUT)
shutil.copyfile(OUT, dst)
print("Downloads ->", dst)

# Branded PDF in Drive-Ordner "Cloud Angebote" hochladen (ueberschreibt bei gleicher Nr).
# Wird uebersprungen, wenn kein Service-Account-Key gesetzt ist.
try:
    from drive_upload import upsert_file, CLOUD_ANGEBOTE
    res = upsert_file(OUT, DRIVE_TITLE, CLOUD_ANGEBOTE)
    print(f"Drive {res['action']} -> {res['name']} ({res['id']})")
    if res.get("webViewLink"):
        print("Drive-Link ->", res["webViewLink"])
except Exception as e:
    print("Drive-Upload uebersprungen:", str(e)[:160])
