"""Hydraulikschema (Prinzip) als DXF erzeugen:

2 reversible Waermepumpen (Heizen/Kuehlen) mit Umschaltung auf zwei
getrennte 2-Leiter-Netze:
  - Warmwasser: eigenes VL/RL-Paar zu 2 Trinkwarmwasser-Speichern
  - Heizen/Kuehlen: ein VL/RL-Paar (Change-Over) ueber 2 Pufferspeicher,
    ueber die geheizt UND gekuehlt wird

Aufruf:  python3 tools/hydraulikschema_wp.py [ausgabe.dxf]
"""
import sys, math, os
import ezdxf
from ezdxf.enums import TextEntityAlignment

# ---------------------------------------------------------------- Grundlagen
def new_doc():
    doc = ezdxf.new("R2018", setup=True)
    for name, color in [
        ("WP", 7), ("SPEICHER", 7), ("ARMATUR", 7), ("TEXT", 7),
        ("RAHMEN", 8), ("VL", 1), ("RL", 5), ("KALTWASSER", 4),
        ("WARMWASSER", 30),
    ]:
        doc.layers.add(name, color=color)
    return doc

def line(msp, p1, p2, layer):
    msp.add_line(p1, p2, dxfattribs={"layer": layer})

def poly(msp, pts, layer, closed=False):
    msp.add_lwpolyline(pts, dxfattribs={"layer": layer}, close=closed)

def text(msp, s, p, h=4.0, layer="TEXT", align=TextEntityAlignment.LEFT):
    t = msp.add_text(s, dxfattribs={"layer": layer, "height": h})
    t.set_placement(p, align=align)
    return t

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

def pumpe(msp, cx, cy, r=5.0, ang=0.0, layer="ARMATUR"):
    """Umwaelzpumpe: Kreis mit Richtungsdreieck (ang = Fliessrichtung in Grad)."""
    msp.add_circle((cx, cy), r, dxfattribs={"layer": layer})
    a = math.radians(ang)
    tip = (cx + r * 0.9 * math.cos(a), cy + r * 0.9 * math.sin(a))
    b1 = (cx + r * 0.9 * math.cos(a + 2.5), cy + r * 0.9 * math.sin(a + 2.5))
    b2 = (cx + r * 0.9 * math.cos(a - 2.5), cy + r * 0.9 * math.sin(a - 2.5))
    poly(msp, [tip, b1, b2], layer, closed=True)

def ventil3(msp, cx, cy, s=5.0, layer="ARMATUR"):
    """3-Wege-Umschaltventil: zwei Dreiecke waagerecht + eines nach oben."""
    poly(msp, [(cx - s, cy - s * 0.7), (cx - s, cy + s * 0.7), (cx, cy)], layer, closed=True)
    poly(msp, [(cx + s, cy - s * 0.7), (cx + s, cy + s * 0.7), (cx, cy)], layer, closed=True)
    poly(msp, [(cx - s * 0.7, cy + s), (cx + s * 0.7, cy + s), (cx, cy)], layer, closed=True)

def mag(msp, cx, cy, r=6.0, layer="ARMATUR"):
    """Membran-Ausdehnungsgefaess: Kreis mit Trennlinie."""
    msp.add_circle((cx, cy), r, dxfattribs={"layer": layer})
    line(msp, (cx - r, cy), (cx + r, cy), layer)

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
def build(doc):
    msp = doc.modelspace()

    # --- Waermepumpen (Kaskade, Prinzip: 2 Gruppen dargestellt) -----------
    for i, y0 in enumerate((150, 55)):
        rect(msp, 10, y0, 85, y0 + 55, "WP")
        text(msp, ("WÄRMEPUMPEN 1–6", "WÄRMEPUMPEN 7–12")[i], (47.5, y0 + 38), 4.0,
             align=TextEntityAlignment.MIDDLE_CENTER)
        text(msp, "je 16 kW, reversibel", (47.5, y0 + 27), 3.2,
             align=TextEntityAlignment.MIDDLE_CENTER)
        text(msp, "Heizen / Kühlen / WW", (47.5, y0 + 19), 3.2,
             align=TextEntityAlignment.MIDDLE_CENTER)
    text(msp, "Kaskade gesamt: 12 × 16 kW = 192 kW", (10, 137), 3.2)

    # Anschlusshoehen
    wp_vl = [195, 100]   # Vorlauf je WP
    wp_rl = [160, 65]    # Ruecklauf je WP
    X_VL, X_RL = 110, 130          # senkrechte Sammelleitungen
    Y_VALVE = 235                  # 3-Wege-Umschaltventil
    Y_WW_VL, Y_WW_RL = 285, 265    # 2 Leitungen Warmwasser-Ladung
    Y_HK_VL, Y_HK_RL = 235, 215    # 2 Leitungen Heizen/Kuehlen (Change-Over)

    # WP-Anschluesse an Sammelleitungen (Kreuzungen ohne Punkt = keine Verbindung)
    for yv in wp_vl:
        line(msp, (85, yv), (X_VL, yv), "VL")
    for yr in wp_rl:
        line(msp, (85, yr), (X_RL, yr), "RL")
    line(msp, (X_VL, wp_vl[1]), (X_VL, Y_VALVE - 5), "VL")   # VL-Sammler hoch zum Ventil
    line(msp, (X_RL, wp_rl[1]), (X_RL, Y_WW_RL), "RL")       # RL-Sammler hoch
    punkt(msp, (X_VL, wp_vl[0]), "VL")
    punkt(msp, (X_RL, wp_rl[0]), "RL")

    # --- 3-Wege-Umschaltventil (WW-Vorrang) -------------------------------
    ventil3(msp, X_VL, Y_VALVE, 5.0)
    text(msp, "3-Wege-Umschaltventil (WW-Vorrang)", (60, Y_VALVE + 11), 3.2)

    # --- Warmwasser-Ladung: 2 Leitungen zu 2 TWW-Speichern ----------------
    line(msp, (X_VL, Y_VALVE + 5), (X_VL, Y_WW_VL), "VL")
    line(msp, (X_VL, Y_WW_VL), (330, Y_WW_VL), "VL")         # WW-VL
    line(msp, (X_RL, Y_WW_RL), (330, Y_WW_RL), "RL")         # WW-RL
    pumpe(msp, 160, Y_WW_VL, 5, 0)
    text(msp, "WW-Ladepumpe", (150, Y_WW_VL + 8), 3.2)
    text(msp, "WW-Ladung VL", (335, Y_WW_VL - 1.5), 3.2, layer="VL")
    text(msp, "WW-Ladung RL", (335, Y_WW_RL - 1.5), 3.2, layer="RL")

    # TWW-Speicher 1+2
    for i, xs in enumerate((200, 280)):
        tank(msp, xs, 300, xs + 50, 385)
        text(msp, f"TWW-SPEICHER {i + 1}", (xs + 25, 342), 3.6,
             align=TextEntityAlignment.MIDDLE_CENTER)
        text(msp, "Trinkwarmwasser", (xs + 25, 333), 2.8,
             align=TextEntityAlignment.MIDDLE_CENTER)
        # Ladekreis (VL unten rein, RL unten raus — Kreuzung mit VL ohne Punkt)
        line(msp, (xs + 12, Y_WW_VL), (xs + 12, 300), "VL")
        punkt(msp, (xs + 12, Y_WW_VL), "VL")
        line(msp, (xs + 38, Y_WW_RL), (xs + 38, 300), "RL")
        punkt(msp, (xs + 38, Y_WW_RL), "RL")
        # Kaltwasser rein / Warmwasser zu den Zapfstellen
        pfeil(msp, (xs + 25, 385), (xs + 25, 413), "WARMWASSER")
        pfeil(msp, (xs - 22, 305), (xs, 305), "KALTWASSER")
    text(msp, "Warmwasser zu den Zapfstellen", (200, 420), 3.2, layer="WARMWASSER")
    text(msp, "Kaltwasser", (148, 309), 3.2, layer="KALTWASSER")

    # --- Heizen/Kuehlen: 2 Leitungen (Change-Over) zu 2 Pufferspeichern ---
    line(msp, (X_VL + 5, Y_HK_VL), (330, Y_HK_VL), "VL")     # HK-VL ab Ventil
    line(msp, (X_RL, Y_HK_RL), (330, Y_HK_RL), "RL")         # HK-RL
    punkt(msp, (X_RL, Y_HK_RL), "RL")
    pumpe(msp, 170, Y_HK_VL, 5, 0)
    text(msp, "Pumpe Heiz-/Kühlkreis", (155, Y_HK_VL - 12), 3.2)
    text(msp, "Change-Over VL", (335, Y_HK_VL - 1.5), 3.2, layer="VL")
    text(msp, "Change-Over RL", (335, Y_HK_RL - 1.5), 3.2, layer="RL")

    # Pufferspeicher 1+2 (unterhalb der Leitungen)
    for i, xs in enumerate((200, 280)):
        tank(msp, xs, 110, xs + 50, 195)
        text(msp, f"PUFFERSPEICHER {i + 1}", (xs + 25, 156), 3.4,
             align=TextEntityAlignment.MIDDLE_CENTER)
        text(msp, ("800 Liter", "500 Liter")[i], (xs + 25, 147), 3.0,
             align=TextEntityAlignment.MIDDLE_CENTER)
        text(msp, "Heizen + Kühlen", (xs + 25, 139), 2.8,
             align=TextEntityAlignment.MIDDLE_CENTER)
        line(msp, (xs + 12, Y_HK_VL), (xs + 12, 195), "VL")  # kreuzt HK-RL ohne Punkt
        punkt(msp, (xs + 12, Y_HK_VL), "VL")
        line(msp, (xs + 38, Y_HK_RL), (xs + 38, 195), "RL")
        punkt(msp, (xs + 38, Y_HK_RL), "RL")

    # Abgang zu den Verbrauchern (Heiz-/Kuehlflaechen)
    pfeil(msp, (330, Y_HK_VL), (380, Y_HK_VL), "VL")
    pfeil(msp, (380, Y_HK_RL), (330, Y_HK_RL), "RL")
    punkt(msp, (330, Y_HK_VL), "VL")
    punkt(msp, (330, Y_HK_RL), "RL")
    text(msp, "zu / von den", (385, Y_HK_VL - 5), 3.2)
    text(msp, "21 Umluftkühlgeräten", (385, Y_HK_VL - 13), 3.2)
    text(msp, "à 1,5 kW (2-Leiter Change-Over,", (385, Y_HK_VL - 21), 2.8)
    text(msp, "Kondensatablauf je Gerät)", (385, Y_HK_VL - 29), 2.8)

    # MAG + Fuellen/Entleeren am Ruecklauf-Sammler
    line(msp, (X_RL, 90), (X_RL, 82), "RL")
    mag(msp, X_RL + 18, 45, 6)
    line(msp, (X_RL, wp_rl[1]), (X_RL + 18, wp_rl[1]), "RL")
    line(msp, (X_RL + 18, wp_rl[1]), (X_RL + 18, 51), "RL")
    punkt(msp, (X_RL, wp_rl[1]), "RL")
    text(msp, "MAG", (X_RL + 28, 43), 3.2)

    # --- Hinweise ----------------------------------------------------------
    text(msp, "HINWEIS: Heizen und Kühlen laufen über DIESELBEN 2 Leitungen", (10, 20), 3.4)
    text(msp, "und DIESELBEN 2 Pufferspeicher (Change-Over, Umschaltung an der WP).", (10, 12), 3.4)
    text(msp, "Warmwasser hat ein eigenes Leitungspaar und eigene Speicher.", (10, 4), 3.4)

    # --- Legende -----------------------------------------------------------
    lx, ly = 330, 60
    rect(msp, lx, ly, lx + 135, ly + 88, "RAHMEN")
    text(msp, "LEGENDE", (lx + 6, ly + 76), 4.0)
    line(msp, (lx + 6, ly + 66), (lx + 26, ly + 66), "VL")
    text(msp, "Vorlauf (VL)", (lx + 32, ly + 64), 3.2)
    line(msp, (lx + 6, ly + 54), (lx + 26, ly + 54), "RL")
    text(msp, "Rücklauf (RL)", (lx + 32, ly + 52), 3.2)
    pumpe(msp, lx + 16, ly + 42, 4, 0)
    text(msp, "Umwälzpumpe", (lx + 32, ly + 40), 3.2)
    ventil3(msp, lx + 16, ly + 28, 4)
    text(msp, "3-Wege-Umschaltventil", (lx + 32, ly + 26), 3.2)
    mag(msp, lx + 16, ly + 12, 5)
    text(msp, "Ausdehnungsgefäß (MAG)", (lx + 32, ly + 10), 3.2)

    # --- Rahmen + Schriftfeld ---------------------------------------------
    rect(msp, 0, -30, 480, 440, "RAHMEN")
    line(msp, (0, -5), (480, -5), "RAHMEN")
    text(msp, "HYDRAULIKSCHEMA (PRINZIP) — WÄRMEPUMPEN: HEIZEN / KÜHLEN / WARMWASSER",
         (10, -15), 4.5)
    text(msp, "LEANS Tech GmbH · ohne Maßstab · Prinzipdarstellung, keine Ausführungsplanung",
         (10, -25), 3.0)
    return doc

def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "zeichnungen/hydraulikschema-waermepumpen.dxf"
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    doc = build(new_doc())
    doc.saveas(out)
    print(f"geschrieben: {out}")

if __name__ == "__main__":
    main()
