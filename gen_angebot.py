#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Erzeugt ein LEANS-Tech-Angebot als PDF im Muster-Layout (Angebot 282)."""
from fpdf import FPDF

FONT_DIR = "/usr/share/fonts/truetype/liberation"

# ---- Angebotsdaten ----
NR = "283"
DATUM = "19. Juni 2026"
GUELTIG = "19. August 2026"
EMPF = ["[Kunde / Empfänger]", "[Straße]", "[PLZ Ort]"]
PROJ = "[Projektkürzel]"
BAUVORHABEN = "[Bauvorhaben]"
INTRO = ("Montage von 2 Klima-Wandgeräten 3,5 kW (Geräte bauseits gestellt) "
         "inkl. Demontage der Bestandsanlage.")
POSITIONS = [
    ("1.1", "Demontage Bestandsanlage",
     "Fachgerechte Demontage der vorhandenen Klimaanlage inkl. Absaugen/Entsorgung des "
     "Kältemittels nach F-Gase-Verordnung, Abbau Innen- und Außengerät sowie fachgerechte "
     "Entsorgung der Altgeräte.",
     "1,00", "psch", "600,00 €", "600,00 €"),
    ("1.2", "Montage 2× Klima-Wandgerät 3,5 kW inkl. Inbetriebnahme",
     "Montage von je Innen-Wandgerät und Außengerät (Geräte bauseits gestellt), "
     "Kältemittelleitungen, Isolierung, Kondensatablauf, Wanddurchbruch, elektrischer Anschluss, "
     "Vakuumieren, Dichtheitsprüfung, Inbetriebnahme sowie Einweisung in die Bedienung.",
     "1,00", "psch", "2.000,00 €", "2.000,00 €"),
    ("1.3", "Fernbedienung (zusätzlich)",
     "Zusätzliche Fernbedienung je Gerät, separat zur serienmäßig im Gerät enthaltenen.",
     "2,00", "Stk", "65,00 €", "130,00 €"),
]
ZWISCHEN = NETTO = GESAMT = "2.730,00 €"

W = {"nr": 14, "besch": 86, "menge": 16, "einheit": 16, "ep": 23, "betrag": 23}
DARK = (17, 17, 17)
GREY = (90, 90, 90)
LINE = (60, 60, 60)
FAM = "Lib"


class PDF(FPDF):
    def footer(self):
        self.set_y(-26)
        self.set_draw_color(150, 150, 150)
        self.set_line_width(0.2)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(2)
        col_w = (self.w - self.l_margin - self.r_margin) / 3
        y0 = self.get_y()
        cols = [
            ("Adresse", ["Berlepschstr. 165", "14165 Berlin"]),
            ("Kontakt", ["info@leanstech-gmbh.de", "Tel. +49 170 8280836", "www.leanstech-gmbh.de"]),
            ("Register / Bank", ["HR-Nr HRB 249080 B", "USt-IdNr. DE357948720",
                                  "Berliner Volksbank · BIC BEVODEBB", "IBAN DE21 1009 0000 2911 7280 04"]),
        ]
        for i, (title, lines) in enumerate(cols):
            x = self.l_margin + i * col_w
            self.set_xy(x, y0)
            self.set_font(FAM, "B", 7.5)
            self.set_text_color(*DARK)
            self.cell(col_w, 3.6, title, ln=2)
            self.set_font(FAM, "", 7.5)
            self.set_text_color(*GREY)
            for ln in lines:
                self.cell(col_w, 3.6, ln, ln=2)


pdf = PDF(orientation="P", unit="mm", format="A4")
pdf.add_font(FAM, "", f"{FONT_DIR}/LiberationSans-Regular.ttf")
pdf.add_font(FAM, "B", f"{FONT_DIR}/LiberationSans-Bold.ttf")
pdf.set_margins(16, 18, 16)
pdf.set_auto_page_break(auto=True, margin=30)
pdf.add_page()

# Absender
pdf.set_font(FAM, "", 8)
pdf.set_text_color(*GREY)
pdf.cell(0, 4, "LEANS Tech GmbH · Semir Redzic · Berlepschstr. 165 · 14165 · Berlin", ln=1)
pdf.set_draw_color(150, 150, 150)
pdf.set_line_width(0.2)
pdf.line(pdf.l_margin, pdf.get_y() + 1, pdf.w - pdf.r_margin, pdf.get_y() + 1)
pdf.ln(7)

# Empfänger
pdf.set_text_color(*DARK)
pdf.set_font(FAM, "B", 11)
pdf.cell(0, 5.5, EMPF[0], ln=1)
pdf.set_font(FAM, "", 10)
for line in EMPF[1:]:
    pdf.cell(0, 5, line, ln=1)
pdf.ln(8)

# Titel
pdf.set_font(FAM, "B", 22)
pdf.cell(0, 10, "ANGEBOT", ln=1)
pdf.set_font(FAM, "", 10)
pdf.set_text_color(*GREY)
pdf.cell(0, 5, PROJ, ln=1)
pdf.ln(2)
pdf.set_text_color(*DARK)
pdf.set_font(FAM, "B", 10)
pdf.cell(0, 5, "RAUMLUFTTECHNIK · HEIZUNG", ln=1)
pdf.ln(5)

# Meta
def kv(label, value, end=False):
    pdf.set_font(FAM, "", 10)
    pdf.write(5.5, label)
    pdf.set_font(FAM, "B", 10)
    pdf.write(5.5, value + ("\n" if end else ""))

kv("Angebotsnummer: ", NR, end=True)
kv("Angebotsdatum: ", DATUM)
kv("    Gültig bis: ", GUELTIG)
kv("    Bauvorhaben: ", BAUVORHABEN, end=True)
pdf.ln(6)

# Intro
pdf.set_font(FAM, "", 10)
pdf.multi_cell(0, 5, INTRO)
pdf.ln(3)

# Tabellenkopf
pdf.set_font(FAM, "B", 9)
pdf.set_text_color(*DARK)
pdf.set_draw_color(*LINE)
pdf.set_line_width(0.4)
pdf.cell(W["nr"], 7, "Nr.")
pdf.cell(W["besch"], 7, "Beschreibung")
pdf.cell(W["menge"], 7, "Menge", align="R")
pdf.cell(W["einheit"], 7, "Einheit", align="R")
pdf.cell(W["ep"], 7, "Einzelpreis", align="R")
pdf.cell(W["betrag"], 7, "Betrag", align="R")
pdf.ln(7)
pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
pdf.ln(1.5)

# Positionen
for nr, titel, besch, menge, einheit, ep, betrag in POSITIONS:
    x0 = pdf.l_margin
    y0 = pdf.get_y()
    pdf.set_xy(x0 + W["nr"], y0)
    pdf.set_font(FAM, "B", 9.5)
    pdf.multi_cell(W["besch"], 4.8, titel, align="L")
    pdf.set_font(FAM, "", 9)
    pdf.set_x(x0 + W["nr"])
    pdf.multi_cell(W["besch"], 4.6, besch, align="L")
    y_end = pdf.get_y()
    pdf.set_xy(x0, y0)
    pdf.set_font(FAM, "B", 9)
    pdf.cell(W["nr"], 4.8, nr)
    pdf.set_font(FAM, "", 9)
    pdf.set_xy(x0 + W["nr"] + W["besch"], y0)
    pdf.cell(W["menge"], 4.8, menge, align="R")
    pdf.cell(W["einheit"], 4.8, einheit, align="R")
    pdf.cell(W["ep"], 4.8, ep, align="R")
    pdf.cell(W["betrag"], 4.8, betrag, align="R")
    pdf.set_y(y_end + 2)
    pdf.set_draw_color(200, 200, 200)
    pdf.set_line_width(0.2)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
    pdf.ln(2)

# Summen
pdf.ln(2)
sum_label_w = 30
sum_val_w = 30
sum_x = pdf.w - pdf.r_margin - sum_label_w - sum_val_w
def sum_row(label, val, bold=False, top=False):
    if top:
        pdf.set_draw_color(*LINE); pdf.set_line_width(0.4)
        pdf.line(sum_x, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
        pdf.ln(1.5)
    pdf.set_x(sum_x)
    pdf.set_font(FAM, "B" if bold else "", 11 if bold else 10)
    pdf.cell(sum_label_w, 6, label)
    pdf.cell(sum_val_w, 6, val, align="R", ln=1)

sum_row("Zwischensumme", ZWISCHEN)
sum_row("Nettobetrag", NETTO)
sum_row("Gesamt (netto)", GESAMT, bold=True, top=True)
pdf.ln(6)

# Rechtshinweis + Zahlung
pdf.set_font(FAM, "", 9)
pdf.set_text_color(*DARK)
pdf.multi_cell(0, 4.6,
    "Die Umsatzsteuer für diese Leistung schuldet nach § 13b UStG der Leistungsempfänger "
    "(Reverse-Charge-Verfahren für Bauleistungen).")
pdf.ln(2)
pdf.multi_cell(0, 4.6,
    "Zahlungsbedingungen: 14 Tage netto. Es gelten unsere allgemeinen Geschäftsbedingungen. "
    "Wir freuen uns auf Ihre Beauftragung.")

pdf.output("Angebot_283_2x_Wandgeraet_3.5kW.pdf")
print("OK geschrieben")
