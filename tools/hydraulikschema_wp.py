"""Hydraulikschema (Prinzip) als DXF erzeugen:

Zwei getrennte Waermepumpen-Kaskaden Midea MHC-V10W/D2N8-BER90 (je 10 kW):
  - 6 Geraete fuer Heizen UND Kuehlen (Change-Over, ein 2-Leiter-Netz)
  - 3 Geraete separat fuer Warmwasser (eigenes 2-Leiter-Netz)

Systemtrennung ueber Plattenwaermetauscher:
  - Primaer (Waermepumpen + Aussenleitungen): Wasser/Glykol ca. 30 %
  - Sekundaer (Gebaeude): reines Heizungswasser nach VDI 2035, kein Glykol

Aufruf:  python3 tools/hydraulikschema_wp.py [ausgabe.dxf]
"""
import sys, math, os
import ezdxf
from ezdxf.enums import TextEntityAlignment

# ---------------------------------------------------------------- Grundlagen
def new_doc():
    doc = ezdxf.new("R2018", setup=True)
    for name, color, ltype in [
        ("WP", 7, "CONTINUOUS"), ("SPEICHER", 7, "CONTINUOUS"),
        ("ARMATUR", 7, "CONTINUOUS"), ("TEXT", 7, "CONTINUOUS"),
        ("RAHMEN", 8, "CONTINUOUS"), ("VL", 1, "CONTINUOUS"),
        ("RL", 5, "CONTINUOUS"), ("KALTWASSER", 4, "CONTINUOUS"),
        ("WARMWASSER", 30, "CONTINUOUS"), ("TRENNUNG", 3, "DASHED"),
        ("MSR", 6, "DASHED"),
    ]:
        doc.layers.add(name, color=color, linetype=ltype)
    doc.header["$LTSCALE"] = 3.0
    return doc

def line(msp, p1, p2, layer):
    msp.add_line(p1, p2, dxfattribs={"layer": layer})

def poly(msp, pts, layer, closed=False):
    msp.add_lwpolyline(pts, dxfattribs={"layer": layer}, close=closed)

def text(msp, s, p, h=4.0, layer="TEXT", align=TextEntityAlignment.LEFT):
    t = msp.add_text(s, dxfattribs={"layer": layer, "height": h})
    t.set_placement(p, align=align)
    return t

def ctext(msp, s, p, h=4.0, layer="TEXT"):
    return text(msp, s, p, h, layer, TextEntityAlignment.MIDDLE_CENTER)

def rect(msp, x1, y1, x2, y2, layer):
    poly(msp, [(x1, y1), (x2, y1), (x2, y2), (x1, y2)], layer, closed=True)

# ---------------------------------------------------------------- Symbole
def tank(msp, x1, y1, x2, y2, layer="SPEICHER"):
    """Speicher: Rechteck mit gerundetem Deckel/Boden."""
    r = (x2 - x1) / 2.0
    cx = (x1 + x2) / 2.0
    line(msp, (x1, y1 + r), (x1, y2 - r), layer)
    line(msp, (x2, y1 + r), (x2, y2 - r), layer)
    msp.add_arc((cx, y2 - r), r, 0, 180, dxfattribs={"layer": layer})
    msp.add_arc((cx, y1 + r), r, 180, 360, dxfattribs={"layer": layer})

def waermetauscher(msp, x1, y1, x2, y2, layer="ARMATUR"):
    """Plattenwaermetauscher: Rechteck mit Zickzack (Gegenstrom)."""
    rect(msp, x1, y1, x2, y2, layer)
    n, pts = 8, []
    for i in range(n + 1):
        y = y1 + (y2 - y1) * (i / n)
        x = x1 + (x2 - x1) * (0.25 if i % 2 == 0 else 0.75)
        pts.append((x, y))
    poly(msp, pts, layer)

def pumpe(msp, cx, cy, r=5.0, ang=0.0, layer="ARMATUR"):
    """Umwaelzpumpe: Kreis mit Richtungsdreieck (ang = Fliessrichtung in Grad)."""
    msp.add_circle((cx, cy), r, dxfattribs={"layer": layer})
    a = math.radians(ang)
    tip = (cx + r * 0.9 * math.cos(a), cy + r * 0.9 * math.sin(a))
    b1 = (cx + r * 0.9 * math.cos(a + 2.5), cy + r * 0.9 * math.sin(a + 2.5))
    b2 = (cx + r * 0.9 * math.cos(a - 2.5), cy + r * 0.9 * math.sin(a - 2.5))
    poly(msp, [tip, b1, b2], layer, closed=True)

def ventil2(msp, cx, cy, s=4.0, motor=True, layer="ARMATUR"):
    """Absperr-/Regelventil: zwei Dreiecke Spitze an Spitze, opt. mit Antrieb."""
    poly(msp, [(cx - s, cy - s * 0.75), (cx - s, cy + s * 0.75), (cx, cy)], layer, closed=True)
    poly(msp, [(cx + s, cy - s * 0.75), (cx + s, cy + s * 0.75), (cx, cy)], layer, closed=True)
    if motor:
        line(msp, (cx, cy), (cx, cy + s * 1.6), layer)
        rect(msp, cx - s * 0.8, cy + s * 1.6, cx + s * 0.8, cy + s * 2.8, layer)
        ctext(msp, "M", (cx, cy + s * 2.2), s * 0.9, layer)

def mag(msp, cx, cy, r=6.0, layer="ARMATUR"):
    """Membran-Ausdehnungsgefaess: Kreis mit Trennlinie."""
    msp.add_circle((cx, cy), r, dxfattribs={"layer": layer})
    line(msp, (cx - r, cy), (cx + r, cy), layer)

def fuehler(msp, cx, cy, kuerzel, r=5.0, layer="MSR"):
    """MSR-Kreis mit Kuerzel (z. B. Taupunktwaechter)."""
    msp.add_circle((cx, cy), r, dxfattribs={"layer": layer})
    ctext(msp, kuerzel, (cx, cy), r * 0.8, layer)

def pfeil(msp, p1, p2, layer):
    """Linie mit Pfeilspitze am Ende p2."""
    line(msp, p1, p2, layer)
    a = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
    for da in (2.6, -2.6):
        q = (p2[0] + 4.0 * math.cos(a + da), p2[1] + 4.0 * math.sin(a + da))
        line(msp, p2, q, layer)

def punkt(msp, p, layer):
    """Verbindungspunkt (T-Stueck)."""
    msp.add_circle(p, 1.2, dxfattribs={"layer": layer})

# ---------------------------------------------------------------- Zeichnung
X_TRENN = 164          # Systemtrennung (Mitte der Waermetauscher)
X_ENDE = 560           # Ende der Sekundaer-Sammelleitungen

def waermepumpen_block(msp, x1, y1, x2, y2, titel, anzahl):
    rect(msp, x1, y1, x2, y2, "WP")
    cx = (x1 + x2) / 2.0
    ctext(msp, titel, (cx, y2 - 13), 4.0)
    ctext(msp, "Midea MHC-V10W/D2N8-BER90", (cx, y2 - 22), 2.9)
    ctext(msp, f"{anzahl} × 10,0 kW (A7/W35, COP 4,95)", (cx, y2 - 30), 2.9)
    ctext(msp, "R32 · 400 V 3N~ · IBH 9 kW", (cx, y2 - 38), 2.9)

def build(doc):
    msp = doc.modelspace()

    # ================= WARMWASSER (oben, eigene 3 Waermepumpen) ============
    Y_WW_VL, Y_WW_RL = 365, 335
    waermepumpen_block(msp, 10, 312, 95, 392, "WÄRMEPUMPEN 7–9", 3)
    ctext(msp, "nur Warmwasser", (52.5, 320), 3.2)
    text(msp, "Kaskade Warmwasser: 3 × 10 kW = 30 kW", (10, 302), 3.0)

    waermetauscher(msp, 150, 325, 178, 375)
    ctext(msp, "WT 2", (X_TRENN, 380), 3.2)
    text(msp, "WT 2: 30 kW · primär 58/48 → sekundär 45/55 °C", (150, 318), 2.5)
    text(msp, "Grädigkeit 2–3 K · ca. 2,5–4 m² · DN32–40", (150, 312), 2.5)
    text(msp, "V 2,8 m³/h primär · 2,6 m³/h sekundär", (150, 306), 2.5)

    line(msp, (95, Y_WW_VL), (150, Y_WW_VL), "VL")            # primaer hin
    line(msp, (150, Y_WW_RL), (95, Y_WW_RL), "RL")            # primaer zurueck
    line(msp, (178, Y_WW_VL), (X_ENDE, Y_WW_VL), "VL")        # sekundaer VL
    line(msp, (X_ENDE, Y_WW_RL), (178, Y_WW_RL), "RL")        # sekundaer RL
    pumpe(msp, 205, Y_WW_VL, 5, 0)
    text(msp, "WW-Ladepumpe", (192, Y_WW_VL + 9), 3.0)
    text(msp, "WW-Ladung VL", (X_ENDE + 6, Y_WW_VL - 1.5), 3.0, layer="VL")
    text(msp, "WW-Ladung RL", (X_ENDE + 6, Y_WW_RL - 1.5), 3.0, layer="RL")

    for i, xs in enumerate((300, 400)):
        tank(msp, xs, 380, xs + 50, 455)
        ctext(msp, f"TWW-SPEICHER {i + 1}", (xs + 25, 424), 3.4)
        ctext(msp, "Trinkwarmwasser", (xs + 25, 415), 2.8)
        ctext(msp, "zus. 1600 Liter", (xs + 25, 407), 2.8)
        line(msp, (xs + 12, Y_WW_VL), (xs + 12, 380), "VL")
        punkt(msp, (xs + 12, Y_WW_VL), "VL")
        line(msp, (xs + 38, Y_WW_RL), (xs + 38, 380), "RL")   # kreuzt VL ohne Punkt
        punkt(msp, (xs + 38, Y_WW_RL), "RL")
        pfeil(msp, (xs + 25, 455), (xs + 25, 478), "WARMWASSER")
        pfeil(msp, (xs - 28, 392), (xs, 392), "KALTWASSER")
    text(msp, "Warmwasser zu den Zapfstellen", (300, 483), 3.2, layer="WARMWASSER")
    text(msp, "Kaltwasser", (232, 396), 3.0, layer="KALTWASSER")

    # ================= HEIZEN / KÜHLEN (unten, 6 Waermepumpen) ============
    Y_HK_VL, Y_HK_RL = 203, 161
    waermepumpen_block(msp, 10, 175, 95, 255, "WÄRMEPUMPEN 1–3", 3)
    waermepumpen_block(msp, 10, 60, 95, 140, "WÄRMEPUMPEN 4–6", 3)
    for y in (168, 53):
        ctext(msp, "Heizen / Kühlen (reversibel)", (52.5, y + 15), 3.2)
    text(msp, "Kaskade Heizen/Kühlen: 6 × 10 kW = 60 kW (A7/W35)", (10, 43), 3.0)
    text(msp, "Kühlen: 6 × 9,9 kW = 59 kW (A35/W18, EER 4,55)", (10, 35), 3.0)

    X_VL, X_RL = 112, 130
    for yv in (228, 113):
        line(msp, (95, yv), (X_VL, yv), "VL")
    for yr in (190, 75):
        line(msp, (X_RL, yr), (95, yr), "RL")
    line(msp, (X_VL, 113), (X_VL, 228), "VL")                 # VL-Sammler DN54
    line(msp, (X_RL, 75), (X_RL, 190), "RL")                  # RL-Sammler DN54
    text(msp, "Sammelleitung DN54", (X_VL - 12, 264), 2.6)
    text(msp, "(Querschnitt prüfen)", (X_VL - 12, 258), 2.6)

    waermetauscher(msp, 150, 152, 178, 212)
    ctext(msp, "WT 1", (X_TRENN, 217), 3.2)
    text(msp, "WT 1: 60 kW · Auslegung nach KÜHLFALL", (150, 145), 2.5)
    text(msp, "Kühlen  primär 13/18 °C → sekundär 16/21 °C", (150, 139), 2.5)
    text(msp, "Heizen  primär 38/33 °C → sekundär 35/30 °C", (150, 133), 2.5)
    text(msp, "Grädigkeit 3 K · ca. 7 m² · DN50", (150, 127), 2.5)
    text(msp, "V 11,5 m³/h primär · 10,3 m³/h sekundär", (150, 121), 2.5)
    line(msp, (X_VL, Y_HK_VL), (150, Y_HK_VL), "VL")
    punkt(msp, (X_VL, Y_HK_VL), "VL")
    line(msp, (150, Y_HK_RL), (X_RL, Y_HK_RL), "RL")
    punkt(msp, (X_RL, Y_HK_RL), "RL")

    line(msp, (178, Y_HK_VL), (X_ENDE, Y_HK_VL), "VL")        # Change-Over VL
    line(msp, (X_ENDE, Y_HK_RL), (178, Y_HK_RL), "RL")        # Change-Over RL
    pumpe(msp, 205, Y_HK_VL, 5, 0)
    text(msp, "Pumpe Heiz-/Kühlkreis", (192, Y_HK_VL + 9), 3.0)

    # Pufferspeicher 1 (bleibt im Kuehlbetrieb in Betrieb)
    tank(msp, 255, 60, 305, 145)
    ctext(msp, "PUFFERSPEICHER 1", (280, 116), 3.2)
    ctext(msp, "PSM 800 · 800 l", (280, 107), 3.0)
    ctext(msp, "Austria Email · 95 °C · 0,4 MPa", (280, 99), 2.5)
    ctext(msp, "Mindestwasserinhalt,", (280, 90), 2.5)
    ctext(msp, "bleibt beim Kühlen in Betrieb", (280, 84), 2.5)
    line(msp, (267, Y_HK_VL), (267, 145), "VL")               # kreuzt RL ohne Punkt
    punkt(msp, (267, Y_HK_VL), "VL")
    line(msp, (293, Y_HK_RL), (293, 145), "RL")
    punkt(msp, (293, Y_HK_RL), "RL")

    # Trennung 2. Heizungsraum
    line(msp, (355, 42), (355, 265), "TRENNUNG")
    text(msp, "2. Heizungsraum", (360, 268), 3.0)
    text(msp, "Verbindung: DN54-Doppelleitung", (360, 260), 2.6)

    # Pufferspeicher 2 (im Kuehlbetrieb absperren = Bypass ueber Hauptleitung)
    tank(msp, 400, 60, 450, 145)
    ctext(msp, "PUFFERSPEICHER 2", (425, 116), 3.2)
    ctext(msp, "PSM 500 · 500 l", (425, 107), 3.0)
    ctext(msp, "im Kühlbetrieb absperren", (425, 96), 2.5)
    ctext(msp, "(Bypass über Hauptleitung)", (425, 90), 2.5)
    line(msp, (412, Y_HK_VL), (412, 145), "VL")
    punkt(msp, (412, Y_HK_VL), "VL")
    ventil2(msp, 412, 178, 4.0)
    line(msp, (438, Y_HK_RL), (438, 145), "RL")
    punkt(msp, (438, Y_HK_RL), "RL")
    ventil2(msp, 438, 152, 4.0)

    # Abgang zu den Verbrauchern
    pfeil(msp, (X_ENDE, Y_HK_VL), (X_ENDE + 60, Y_HK_VL), "VL")
    pfeil(msp, (X_ENDE + 60, Y_HK_RL), (X_ENDE, Y_HK_RL), "RL")
    punkt(msp, (X_ENDE, Y_HK_VL), "VL")
    punkt(msp, (X_ENDE, Y_HK_RL), "RL")
    fuehler(msp, 530, Y_HK_VL + 18, "TP", 6)
    line(msp, (530, Y_HK_VL + 12), (530, Y_HK_VL), "MSR")
    text(msp, "Taupunktwächter: hebt VL an,", (452, Y_HK_VL + 37), 2.6)
    text(msp, "wenn Taupunkt + 2 K erreicht", (452, Y_HK_VL + 31), 2.6)
    for i, s in enumerate([
        "zu / von den 20 Kanal-Gebläsekonvektoren",
        "KONVEKA DF2 51 (2-Leiter-Ausführung)",
        "Kühlen 17/22 °C, Raum 27 °C, Stufe max:",
        "1 516 W total / 1 061 W sensibel je Gerät",
        "→ 30,3 kW total / 21,2 kW sensibel",
        "Heizen 35/30 °C, Raum 20 °C: 1 593 W je Gerät → 31,9 kW",
        "Wasser 261 l/h je Gerät · Δp 11,9 kPa · G 3/4\"",
        "Kondensatanschluss DN20 je Gerät",
        "Auslegung Kaltwasser: 16/21 °C sekundär,",
        "gleitend nach Taupunkt (Minimum 12 °C)",
    ]):
        text(msp, s, (X_ENDE + 4, 258 - i * 8), 2.8 if i else 3.2)

    # MAG primaer (Glykol) und sekundaer (Wasser)
    line(msp, (X_RL, 75), (X_RL + 16, 75), "RL")
    line(msp, (X_RL + 16, 75), (X_RL + 16, 51), "RL")
    punkt(msp, (X_RL, 75), "RL")
    mag(msp, X_RL + 16, 45, 6)
    text(msp, "MAG primär", (X_RL + 25, 43), 2.8)
    line(msp, (330, Y_HK_RL), (330, 128), "RL")
    punkt(msp, (330, Y_HK_RL), "RL")
    mag(msp, 330, 122, 6)
    text(msp, "MAG sekundär", (339, 120), 2.8)

    # ================= Systemtrennung ======================================
    line(msp, (X_TRENN, 42), (X_TRENN, 470), "TRENNUNG")
    text(msp, "PRIMÄR — Wasser/Glykol ca. 30 %", (14, 466), 3.4, layer="TRENNUNG")
    text(msp, "(Wärmepumpen + Außenleitungen, frostsicher)", (14, 459), 2.8, layer="TRENNUNG")
    text(msp, "SEKUNDÄR — reines Heizungswasser nach VDI 2035, kein Glykol", (182, 466), 3.4,
         layer="TRENNUNG")
    text(msp, "(gesamtes Gebäude: Puffer, Verteilung, Verbraucher, TWW-Ladung)", (182, 459), 2.8,
         layer="TRENNUNG")

    # ================= Hinweise ============================================
    for i, s in enumerate([
        "SYSTEMTRENNUNG: Nur der Primärkreis (Wärmepumpen + Außenstrecke bis zu den Wärmetauschern) wird mit Frostschutz gefüllt —",
        "dadurch statt über 600 l nur rund 50–75 l Glykol. Preis dafür: Grädigkeit der Wärmetauscher 2–4 K (rund 7 % COP bzw. EER).",
        "WT 1 auf den KÜHLFALL auslegen (kleinere treibende Temperaturdifferenz als beim Heizen), nicht auf den Heizfall.",
        "CHANGE-OVER: Heizen und Kühlen laufen über dieselben Leitungen, Puffer und Verbraucher — Umschaltung an den Wärmepumpen,",
        "saisonal umschalten (nicht täglich): jedes Umladen der Puffer kostet rund 30 kWh. Warmwasser läuft davon unabhängig weiter.",
        "KÜHLBETRIEB: Leitungen, Armaturen und Speicher dampfdiffusionsdicht dämmen (geschlossenzelliger Kautschuk, Stöße verklebt).",
        "Die Eco-Skin-Vliesisolierung des PSM 800 ist NICHT diffusionsdicht. Kondensatanschlüsse der Konvektoren mit Gefälle führen.",
        "KALTWASSER: 16 °C Vorlauf sekundär (13 °C primär) hält die Anlage in fast allen Betriebspunkten über dem Taupunkt. Grenzen:",
        "primär nie unter 7 °C (ohne Glykol Vereisungsgefahr), sekundär nie unter 12 °C. Bedarf 30 kW gegen 59 kW Kälteleistung —",
        "die Reserve in eine HÖHERE Kaltwassertemperatur umsetzen (rund 2–3 % besserer EER je Kelvin), nicht in eine tiefere.",
        "WARMWASSER: Die Wärmepumpe liefert max. 60 °C. Mit 3 K Grädigkeit am WT 2 wird der Speicher nur auf 52–54 °C geladen — bei 1600 l",
        "fordert die TrinkwV aber 60 °C am Speicheraustritt. Empfehlung: WW-Kreis OHNE Systemtrennung (Glykol bis zum Speicher-WT,",
        "rund 35 l mehr) oder WT 2 mit 2 K plus E-Nachheizung im Speicher für die Legionellenschaltung.",
        "AUSLEGUNG: Für die Raumtemperatur zählt die SENSIBLE Leistung der Konvektoren — bei 17/22 °C sind das 21,2 kW, bei 14/19 °C",
        "27,4 kW, bei 10/15 °C 35,8 kW (Katalogwerte DF2 51, interpoliert). Volumenstrom steigt dabei von 261 auf 439 l/h je Gerät —",
        "vor einer tieferen Kaltwassertemperatur die Strangquerschnitte Ø22/Ø28/Ø35 auf max. 0,8 m/s nachrechnen.",
    ]):
        text(msp, s, (10, 24 - i * 7), 2.7)

    # ================= Legende =============================================
    lx, ly = 470, 30
    rect(msp, lx, ly, lx + 170, ly + 118, "RAHMEN")
    text(msp, "LEGENDE", (lx + 6, ly + 106), 4.0)
    line(msp, (lx + 8, ly + 96), (lx + 30, ly + 96), "VL")
    text(msp, "Vorlauf (VL)", (lx + 36, ly + 94), 3.0)
    line(msp, (lx + 8, ly + 85), (lx + 30, ly + 85), "RL")
    text(msp, "Rücklauf (RL)", (lx + 36, ly + 83), 3.0)
    line(msp, (lx + 8, ly + 74), (lx + 30, ly + 74), "TRENNUNG")
    text(msp, "Systemtrennung / Raumgrenze", (lx + 36, ly + 72), 3.0)
    waermetauscher(msp, lx + 12, ly + 52, lx + 26, ly + 66)
    text(msp, "Plattenwärmetauscher", (lx + 36, ly + 57), 3.0)
    pumpe(msp, lx + 19, ly + 42, 4, 0)
    text(msp, "Umwälzpumpe", (lx + 36, ly + 40), 3.0)
    ventil2(msp, lx + 19, ly + 27, 3.5)
    text(msp, "Absperr-/Regelventil (motorisch)", (lx + 36, ly + 25), 3.0)
    mag(msp, lx + 19, ly + 12, 5)
    text(msp, "Ausdehnungsgefäß (MAG)", (lx + 36, ly + 10), 3.0)
    fuehler(msp, lx + 118, ly + 12, "TP", 5)
    text(msp, "Taupunktwächter", (lx + 128, ly + 10), 3.0)

    # ================= Rahmen + Schriftfeld ================================
    rect(msp, 0, -95, 700, 500, "RAHMEN")
    line(msp, (0, -70), (700, -70), "RAHMEN")
    text(msp, "HYDRAULIKSCHEMA (PRINZIP) — WÄRMEPUMPEN: HEIZEN / KÜHLEN / WARMWASSER MIT SYSTEMTRENNUNG",
         (10, -80), 4.5)
    text(msp, "LEANS Tech GmbH · ohne Maßstab · Prinzipdarstellung, keine Ausführungsplanung",
         (10, -90), 3.0)
    return doc

def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "zeichnungen/hydraulikschema-waermepumpen.dxf"
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    doc = build(new_doc())
    doc.saveas(out)
    print(f"geschrieben: {out}")

if __name__ == "__main__":
    main()
