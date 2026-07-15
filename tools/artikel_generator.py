#!/usr/bin/env python3
"""Artikel-Generator für Profihaustechnik.de.

Erzeugt aus den Basis-Produktgruppen (tools/basis_artikel.json) das komplette
Sortiment mit allen realen Varianten (Dimensionen, Nennweiten, Leistungs- und
Speicherklassen) — so wie die großen SHK-Großhändler ihre Artikellisten führen.

Ausgabe:
  website/artikel.json       — [{g, k, n, d, e, v: [[Ausführung, Artikelnummer], ...]}, ...]
  website/amazon-export.csv  — eine Zeile je SKU (Amazon-Flatfile-Basis)
"""
import csv, json, re, zlib
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
BASIS = WURZEL / "tools" / "basis_artikel.json"
ZIEL_JSON = WURZEL / "website" / "artikel.json"
ZIEL_CSV = WURZEL / "website" / "amazon-export.csv"

# ---------------------------------------------------------------- Maßreihen
DN_LUEFTUNG = [80, 100, 112, 125, 140, 150, 160, 180, 200, 224, 250, 280,
               300, 315, 355, 400, 450, 500, 560, 630, 710, 800, 900, 1000, 1120, 1250]
DN_LUEFTUNG_KLEIN = [80, 100, 125, 150, 160, 200, 250, 315]
CU = [12, 15, 18, 22, 28, 35, 42, 54]
MSVR = [16, 20, 26, 32, 40, 50, 63]
HT = [32, 40, 50, 75, 90, 110, 125, 160]
KG = [110, 125, 160, 200, 250, 315, 400, 500]
ZOLL = ['3/8"', '1/2"', '3/4"', '1"', '1 1/4"', '1 1/2"', '2"']
FITTING_FORMEN = ["Bogen 90° I/I", "Bogen 90° I/A", "Bogen 45° I/I", "Bogen 45° I/A",
                  "Muffe", "Reduziermuffe", "T-Stück", "T-Stück reduziert",
                  "Übergangsmuffe IG", "Übergangsnippel AG", "Wandscheibe", "Kappe"]
HK_TYPEN = ["Typ 10", "Typ 11", "Typ 20", "Typ 21", "Typ 22", "Typ 30", "Typ 33"]
HK_HOEHEN = [300, 350, 400, 500, 550, 600, 750, 900, 950]
HK_LAENGEN = list(range(400, 3300, 100))
LITER_PUFFER = [200, 300, 400, 500, 600, 800, 1000, 1500, 2000]
LITER_WW = [120, 150, 200, 300, 400, 500]
KW_WP = [4, 6, 8, 10, 12, 14, 16]
KW_KESSEL = [15, 20, 25, 30, 35, 50]
KW_KLIMA = [2.0, 2.5, 3.5, 5.0, 6.1, 7.1]
MAG = [18, 25, 35, 50, 80, 100, 140, 200, 300, 500]
DAEMM_STAERKEN = [13, 19, 25, 32]


def dn(reihe, einheit="mm"):
    return [f"DN {d}" for d in reihe] if einheit == "mm" else [f"{d} {einheit}" for d in reihe]


def kombi(a, b, fmt="{} · {}"):
    return [fmt.format(x, y) for x in a for y in b]


# ---------------------------------------------------------- Variantenregeln
# (Muster auf Name | Kategorie) -> (Variantenliste, Einheit). Erste Regel gewinnt.
REGELN = [
    # ---- Lüftung: Rohre, Formteile
    (r"Wickelfalzrohr", lambda: kombi(dn(DN_LUEFTUNG), ["1,5 m", "3 m", "5 m"], "{} × {}"), "St"),
    (r"Flexrohr|Iso-Flexrohr|Kombi-Flexrohr|PE-Flexkanal",
     lambda: kombi(dn(DN_LUEFTUNG_KLEIN), ["3 m", "6 m", "10 m"], "{} × {}"), "St"),
    (r"Flachkanal Kunststoff|PVC-Flachkanal",
     lambda: kombi(["220×54 mm", "220×90 mm", "308×29 mm"],
                   ["Kanal 1 m", "Kanal 1,5 m", "Bogen horizontal", "Bogen vertikal",
                    "Verbinder", "Übergang rund"], "{} · {}"), "St"),
    (r"Bogen 15|Flexbogen", lambda: kombi(kombi(dn(DN_LUEFTUNG), ["15°", "30°", "45°", "90°"]),
                                          ["mit Lippendichtung (SAFE)", "ohne Dichtung"]), "St"),
    (r"T-Stück / Hosenstück|Sattelstutzen|Enddeckel|Rückschlagklappe|"
     r"Absperrklappe|Jalousieklappe|Übergangsstück rund",
     lambda: kombi(dn(DN_LUEFTUNG), ["mit Lippendichtung (SAFE)", "ohne Dichtung"]), "St"),
    (r"Muffe / Nippel", lambda: kombi(kombi(["Muffe", "Nippel"], dn(DN_LUEFTUNG), "{} {}"),
                                      ["mit Lippendichtung (SAFE)", "ohne Dichtung"]), "St"),
    (r"Reduzierung konzentrisch",
     lambda: kombi([f"DN {a}/{b}" for a, b in zip(DN_LUEFTUNG[1:], DN_LUEFTUNG[:-1])] +
                   [f"DN {a}/{b}" for a, b in zip(DN_LUEFTUNG[2:], DN_LUEFTUNG[:-2])],
                   ["mit Lippendichtung (SAFE)", "ohne Dichtung"]), "St"),
    (r"Rundrohr Kunststoff|Tunnelbogen|Flachovalrohr",
     lambda: ["DN 75", "DN 90", "DN 75 · 50-m-Ring", "DN 90 · 50-m-Ring",
              "Bogen 90°", "Verbinder", "Endkappe"], "St"),
    (r"Rechteckkanal", lambda: kombi(["200×100", "300×150", "400×200", "500×250", "600×300",
                                      "800×300", "1000×400"], ["mm, 1,5 m"], "{} {}"), "St"),
    (r"Tellerventil", lambda: kombi(dn([80, 100, 125, 150, 160, 200]),
                                    ["Stahl weiß", "Edelstahl"]), "St"),
    (r"Lüftungsgitter|Wetterschutzgitter|Designgitter|Kombigitter",
     lambda: kombi(["150×150", "200×200", "250×250", "300×300", "400×400", "500×500"],
                   ["mm"], "{} {}") + dn(DN_LUEFTUNG_KLEIN), "St"),
    (r"Brandschutzklappe|Absperrvorrichtung K90",
     lambda: kombi(dn(DN_LUEFTUNG), ["Schmelzlot", "Stellmotor 230 V", "Stellmotor 24 V"]), "St"),
    (r"Rohrschalldämpfer", lambda: kombi(dn(DN_LUEFTUNG_KLEIN),
                                         ["L 500 mm", "L 600 mm", "L 900 mm", "L 1200 mm"]), "St"),
    (r"Volumenstromregler", lambda: kombi(dn(DN_LUEFTUNG_KLEIN), ["mechanisch", "motorisch"]), "St"),
    (r"Schalldämpfer-Verteilerbox|Luftverteiler",
     lambda: [f"{n} Anschlüsse DN 75/90" for n in range(6, 16)], "St"),
    (r"Dachhaube|Dachventilator", lambda: dn(DN_LUEFTUNG_KLEIN), "St"),
    (r"Rohrventilator|Kanalventilator|EC-Ventilator|Radialventilator|Axialventilator",
     lambda: dn(DN_LUEFTUNG_KLEIN), "St"),
    (r"Kleinraumventilator", lambda: kombi(["DN 100", "DN 125", "DN 150"],
                                           ["Standard", "Nachlauf", "Feuchtesensor", "Bewegungsmelder"]), "St"),
    (r"KWL-Gerät", lambda: [f"{m} m³/h" for m in [180, 250, 300, 350, 400, 500, 600, 800]], "St"),
    (r"Pendellüfter", lambda: ["Einzelgerät", "2er-Set", "4er-Set", "6er-Set"], "St"),
    (r"Filtermatte|Taschenfilter|Aktivkohlefilter|HEPA-Filter|Fettfilter|Pollenfilter",
     lambda: kombi(["G4", "M5", "F7 (ePM1 55 %)", "F9"],
                   ["287×287", "490×490", "592×592", "Zuschnitt 1×2 m"], "{} · {} mm"), "St"),
    (r"Dämmmatte|Kautschuk-Dämmung",
     lambda: [f"{s} mm · Rolle {l} m²" for s in [20, 30, 50, 100] for l in [5, 10]], "Rolle"),
    (r"Rohrschelle|Kanalschelle", lambda: kombi(dn(DN_LUEFTUNG_KLEIN) + [f"{z}" for z in ZOLL] +
                                                [f"{d} mm" for d in [12, 15, 18, 22, 28, 35, 42, 54]],
                                                ["M8", "M8/M10"]), "St"),
    (r"KG-Formteile|KG-2000-Formteile",
     lambda: [f"DN {d} · {f}" for d in KG for f in ["Bogen 15°", "Bogen 30°", "Bogen 45°", "Bogen 87°",
                                                    "Abzweig 45°", "Überschiebmuffe", "Reduzierung", "Kappe"]], "St"),

    # ---- Sanitär: Rohre & Fittings
    (r"Kupferrohr", lambda: [f"{d} × 1 mm · Stange 5 m" for d in CU] +
                            [f"{d} × 1 mm · Ring 25 m" for d in CU if d <= 22], "St"),
    (r"C-Stahlrohr|Edelstahlrohr|Heizungsrohr C-Stahl",
     lambda: [f"{d} mm · Stange 6 m" for d in [15, 18, 22, 28, 35, 42, 54, 76, 88, 108]], "St"),
    (r"Mehrschichtverbundrohr", lambda: [f"{d} mm · Ring {l} m" for d in MSVR
                                         for l in ([200, 500] if d <= 20 else [50])] +
                                        [f"{d} mm · Stange 5 m" for d in MSVR if d >= 32], "Ring"),
    (r"PE-X-Rohr|PE-RT|FBH-Rohr", lambda: [f"{d} · Ring {l} m" for d in
                                           ["14×2", "16×2", "17×2", "20×2"]
                                           for l in [120, 200, 240, 300, 500, 600]], "Ring"),
    (r"PP-R-Rohr", lambda: [f"{d} mm · Stange 4 m" for d in [20, 25, 32, 40, 50, 63]], "St"),
    (r"PE-HD-Rohr", lambda: [f"{d} · Ring {l} m" for d in ["25×2,3", "32×2,9", "40×3,7", "50×4,6", "63×5,8"]
                             for l in [50, 100]], "Ring"),
    (r"HT-Rohr", lambda: [f"DN {d} × {l} mm" for d in HT for l in [150, 250, 500, 750, 1000, 1500, 2000]], "St"),
    (r"HT-/KG-Formteile", lambda: [f"HT DN {d} · {f}" for d in HT for f in
                                   ["Bogen 15°", "Bogen 30°", "Bogen 45°", "Bogen 67°", "Bogen 87°",
                                    "Abzweig 45°", "Abzweig 87°", "Überschiebmuffe", "Kappe"]], "St"),
    (r"KG-Rohr", lambda: [f"DN {d} × {l} mm" for d in KG for l in [500, 1000, 2000, 5000]], "St"),
    (r"KG-2000", lambda: [f"DN {d} × {l} mm" for d in KG[:5] for l in [1000, 2000, 5000]], "St"),
    (r"SML-Gussrohr|Schallschutz-Abwasserrohr",
     lambda: [f"DN {d} · {t}" for d in [50, 70, 100, 125, 150] for t in
              ["Rohr 3 m", "Bogen 45°", "Bogen 87°", "Abzweig 45°", "Muffe/Verbinder"]], "St"),
    (r"Pressfitting Kupfer|Pressfitting Edelstahl|Lötfitting",
     lambda: kombi(FITTING_FORMEN, [f"{d} mm" for d in CU]), "St"),
    (r"Pressfitting Verbundrohr", lambda: kombi(FITTING_FORMEN, [f"{d} mm" for d in MSVR]), "St"),
    (r"Gewindefitting", lambda: kombi(["Winkel 90° IG", "Winkel 90° IG/AG", "Muffe", "Nippel",
                                       "T-Stück", "T-Stück reduziert", "Reduziernippel", "Kappe",
                                       "Langnippel 100 mm", "Doppelnippel", "Übergangsstück", "Stopfen"], ZOLL), "St"),
    (r"Klemmringverschraubung|Steckfitting",
     lambda: kombi(["gerade", "Winkel", "T-Stück"], [f"{d} mm" for d in [15, 16, 18, 20, 22, 26, 28, 32]]), "St"),
    (r"Übergangsstück AG/IG", lambda: kombi(["AG", "IG"], [f"{d} mm × {z}" for d in [16, 20, 26, 32]
                                                           for z in ['1/2"', '3/4"', '1"']]), "St"),
    # ---- Sanitär: Armaturen & Objekte
    (r"Eckventil", lambda: ['3/8" mit Rosette', '3/8" ohne Rosette',
                            '1/2" mit Rosette', '1/2" ohne Rosette', '1/2" mit Filter'], "St"),
    (r"Kugelhahn|Freistromventil|Schrägsitz|Schmutzfänger",
     lambda: kombi(ZOLL, ["IG/IG", "IG/AG"]), "St"),
    (r"Druckminderer|Rückflussverhinderer|Systemtrenner|Wasserzähler",
     lambda: ZOLL[:5], "St"),
    (r"Sicherheitsventil \(6/8/10", lambda: kombi(['1/2"', '3/4"', '1"'], ["6 bar", "8 bar", "10 bar"]), "St"),
    (r"Einhebelmischer", lambda: kombi(["Serie Basic", "Serie Komfort", "Serie Design"],
                                       ["Chrom", "Chrom Niederdruck", "Schwarz matt", "Edelstahl-Optik"]), "St"),
    (r"WC-Sitz", lambda: ["weiß Absenkautomatik", "weiß Absenkautomatik + Take-off",
                          "weiß matt", "schwarz matt", "anthrazit", "D-Form", "O-Form", "Familiensitz"], "St"),
    (r"Sanitärsilikon", lambda: [f"310 ml · {f}" for f in
                                 ["transparent", "weiß", "brillantweiß", "manhattan", "grau",
                                  "anthrazit", "schwarz", "bahamabeige", "jasmin", "caramel"]], "Kart."),
    (r"Flexschlauch / Panzerschlauch", lambda: [f'{z} · {l} mm · {a}' for z in ['3/8"', '1/2"']
                                                for l in [300, 500, 800, 1000, 1500, 2000]
                                                for a in ["IG/IG", "IG/AG"]], "St"),
    (r"Thermostatarmatur", lambda: ["Dusche AP", "Wanne AP", "Dusche UP-Fertigset", "Wanne UP-Fertigset"], "St"),
    (r"Wand-WC / Stand-WC", lambda: ["Wand-WC spülrandlos weiß", "Wand-WC spülrandlos weiß matt",
                                     "Stand-WC Abgang waagerecht", "Stand-WC Abgang senkrecht",
                                     "Wand-WC erhöht (Komfort)", "Kompakt-WC 48 cm"], "St"),
    (r"Waschtisch / Aufsatz", lambda: [f"{b} cm" for b in [50, 55, 60, 65, 80, 100, 120]] +
                                      ["Aufsatzbecken rund", "Aufsatzbecken eckig"], "St"),
    (r"Duschwanne", lambda: [f"{m} cm · {a}" for m in ["80×80", "90×90", "100×80", "100×100",
                                                       "120×80", "120×90", "140×90", "160×90", "170×90"]
                             for a in ["Acryl flach", "Acryl superflach", "Mineralguss bodeneben"]], "St"),
    (r"Badewanne", lambda: [f"{m} cm" for m in ["160×70", "170×75", "180×80", "190×90"]] +
                           ["Raumspar links", "Raumspar rechts", "freistehend oval"], "St"),
    (r"Duschabtrennung", lambda: [f"{t} {b} cm · H {h} cm · {g}" for t in
                                  ["Walk-In", "Falttür", "Drehtür", "Schiebetür"]
                                  for b in [75, 80, 90, 100, 110, 120, 140, 160]
                                  for h in [195, 200] for g in ["Klarglas", "satiniert"]], "St"),
    (r"Waschtischunterschrank", lambda: [f"{b} cm · {f}" for b in [50, 60, 65, 80, 100, 120, 140]
                                         for f in ["weiß glänzend", "eiche hell", "anthrazit matt", "grau Beton-Optik"]], "St"),
    (r"Küchenspüle", lambda: ["Edelstahl 1 Becken", "Edelstahl 1,5 Becken", "Edelstahl 2 Becken",
                              "Granit schwarz", "Granit grau", "Granit beige", "Unterbau Edelstahl"], "St"),
    (r"Vorwandelement WC", lambda: ["BH 82 cm", "BH 98 cm", "BH 112 cm",
                                    "BH 112 cm Eck", "BH 112 cm barrierefrei"], "St"),
    (r"Betätigungsplatte", lambda: ["Weiß", "Chrom glänzend", "Chrom matt", "Schwarz matt",
                                    "Edelstahl", "Glas weiß", "Glas schwarz", "berührungslos IR"], "St"),
    (r"Duschrinne", lambda: [f"{l} mm" for l in [600, 700, 800, 900, 1000, 1200]] +
                            ["Punktablauf 100×100", "Punktablauf 150×150"], "St"),
    (r"Warmwasserspeicher elektrisch", lambda: [f"{l} l" for l in [30, 50, 80, 100, 120, 150, 200, 300]], "St"),
    (r"Durchlauferhitzer elektronisch", lambda: ["18 kW", "21 kW", "24 kW", "27 kW"], "St"),
    (r"Rohrdämmung|Rohrisolierung|UV-beständige Leitungsdämmung",
     lambda: [f"{z} × {s} mm" for z in ["15 mm", "18 mm", "22 mm", "28 mm", "35 mm", "42 mm",
                                        "54 mm", '3/8"', '1/2"', '3/4"', '1"']
              for s in DAEMM_STAERKEN], "m"),

    # ---- Heizung
    (r"Flachheizkörper",
     lambda: [f"{t} · {h}×{l} mm" for t in HK_TYPEN for h in HK_HOEHEN for l in HK_LAENGEN], "St"),
    (r"Ventilheizkörper",
     lambda: [f"{t} · {h}×{l} mm · {a}" for t in HK_TYPEN for h in HK_HOEHEN for l in HK_LAENGEN
              for a in ["Anschluss rechts", "Mittenanschluss"]], "St"),
    (r"Röhrenradiator", lambda: [f"{s}-säulig · H {h} mm · {g} Glieder" for s in [2, 3, 4, 5, 6]
                                 for h in [300, 400, 500, 600, 750, 900, 1000, 1200, 1500, 1800, 2000, 2200, 2500, 3000]
                                 for g in range(4, 32, 2)], "St"),
    (r"Badheizkörper", lambda: [f"{h}×{b} mm · {f}" for h in [770, 1170, 1500, 1775, 1820]
                                for b in [450, 500, 600, 750]
                                for f in ["weiß gerade", "weiß gebogen", "anthrazit gerade",
                                          "anthrazit gebogen", "chrom gerade", "Mittelanschluss weiß"]], "St"),
    (r"Designheizkörper", lambda: [f"vertikal {h}×{b} mm · {f}" for h in [1600, 1800, 2000, 2200]
                                   for b in [300, 450, 600] for f in ["weiß", "anthrazit", "schwarz matt"]], "St"),
    (r"Konvektor / Unterflur", lambda: [f"{b}×{t} mm · L {l} m" for b in [200, 260, 320]
                                        for t in [90, 110] for l in [1.0, 1.5, 2.0, 2.5, 3.0]], "St"),
    (r"Heizkreisverteiler", lambda: [f"{n} Heizkreise" for n in range(2, 13)], "St"),
    (r"Tackersystem|Noppensystem", lambda: [f"Rolle 10 m² · {s} mm" for s in [20, 25, 30, 35]] +
                                           ["Tackernadeln 300 St", "Kleberband", "Systemzubehör-Set"], "St"),
    (r"Thermostatventil", lambda: kombi(["Durchgang", "Eck", "Axial"], ['3/8"', '1/2"', '3/4"']), "St"),
    (r"Thermostatkopf", lambda: ["Standard M30×1,5", "Behördenmodell", "Fernfühler 2 m",
                                 "Fernversteller 5 m", "Design weiß", "Design chrom"], "St"),
    (r"Rücklaufverschraubung|Hahnblock", lambda: kombi(["Durchgang", "Eck"], ['1/2"', '3/4"']), "St"),
    (r"Strangregulierventil|Zonenventil|Überströmventil",
     lambda: ZOLL[1:6], "St"),
    (r"3-Wege-Mischer", lambda: kombi(["3-Wege", "4-Wege"], ['3/4"', '1"', '1 1/4"']) +
                                ["Stellmotor 230 V", "Stellmotor 24 V"], "St"),
    (r"Hocheffizienz-Umwälzpumpe", lambda: [f"{t} · BL {bl} mm" for t in
                                            ["25-40", "25-60", "25-80", "32-60", "32-80"]
                                            for bl in [130, 180]], "St"),
    (r"Membran-Ausdehnungsgefäß", lambda: [f"{l} l" for l in MAG], "St"),
    (r"Pufferspeicher", lambda: [f"{l} l · {a}" for l in LITER_PUFFER
                                 for a in ["ohne Register", "1 Register", "2 Register"]], "St"),
    (r"Warmwasserspeicher \(mono", lambda: [f"{l} l · {a}" for l in LITER_WW
                                            for a in ["monovalent", "bivalent"]], "St"),
    (r"Hygienespeicher|Schichtenspeicher|Kombispeicher",
     lambda: [f"{l} l" for l in [600, 800, 1000, 1500]], "St"),
    (r"Luft/Wasser-Wärmepumpe|Sole/Wasser-Wärmepumpe|Wasser/Wasser-Wärmepumpe",
     lambda: [f"{kw} kW" for kw in KW_WP] + [f"{kw} kW · 3-phasig" for kw in KW_WP[2:]], "St"),
    (r"Gas-Brennwerttherme|Gas-Kombitherme", lambda: [f"{kw} kW" for kw in KW_KESSEL], "St"),
    (r"Gas-Brennwertkessel bodenstehend|Öl-Brennwertkessel|Pelletkessel|Scheitholz",
     lambda: [f"{kw} kW" for kw in [15, 20, 25, 32, 40, 50, 60]], "St"),
    (r"Abgassystem Kunststoff|LAS-System",
     lambda: [f"DN {d} · {t}" for d in ["60/100", "80/125", "110/160"]
              for t in ["Rohr 0,5 m", "Rohr 1 m", "Rohr 2 m", "Bogen 45°", "Bogen 87°",
                        "Revisionsstück", "Dachdurchführung", "Mündungsset"]], "St"),
    (r"Edelstahl-Abgasrohr|Schornsteinsanierung",
     lambda: [f"DN {d} · {t}" for d in [80, 113, 130, 150, 180, 200]
              for t in ["Rohr 1 m", "Bogen", "Wandhalter", "Mündungsabschluss"]], "St"),
    (r"Flachkollektor|Röhrenkollektor", lambda: ["2,0 m²", "2,3 m²", "2,55 m²", "3,0 m²"], "St"),
    (r"Stellantrieb", lambda: ["230 V NC", "230 V NO", "24 V NC", "24 V NO"], "St"),
    (r"Raumthermostat", lambda: ["analog 230 V", "digital 230 V", "digital 24 V",
                                 "Funk + Empfänger", "Smart (App/WLAN)"], "St"),

    # ---- Klima
    (r"Split-Klimagerät", lambda: [f"{kw} kW Wandgerät" for kw in KW_KLIMA], "St"),
    (r"Multisplit-Anlage", lambda: [f"Außengerät {kw} kW · {n} Inneneinheiten"
                                    for kw, n in [(4.1, 2), (5.3, 2), (5.3, 3), (6.8, 3),
                                                  (7.9, 4), (10.0, 4), (10.0, 5)]], "St"),
    (r"Kassettengerät|Kanalklimagerät|Truhengerät|Deckengerät|Standtruhe|Reversibles",
     lambda: [f"{kw} kW" for kw in [2.5, 3.5, 5.0, 6.0, 7.1, 9.5, 12.1]], "St"),
    (r"Kältemittelleitung", lambda: [f'{p} · {l} m' for p in
                                     ['1/4"–3/8"', '1/4"–1/2"', '1/4"–5/8"', '3/8"–5/8"']
                                     for l in [3, 5, 10, 15, 20, 25, 50]], "St"),
    (r"Kältemittel R32", lambda: ["R32 · 9 kg", "R410A · 11,3 kg", "R290 · 5 kg (Sachkunde)"], "St"),
    (r"Kondensatpumpe", lambda: ["Mini 8 l/h", "Mini 12 l/h", "Tank 300 l/h", "Peristaltik"], "St"),
    (r"Wandkonsole / Bodenkonsole", lambda: ["Wandkonsole 450 mm", "Wandkonsole 550 mm",
                                             "Bodenkonsole Kunststoff", "Bodenkonsole Beton 600 mm",
                                             "Flachdachständer"], "St"),
    (r"Kanalsystem / Kabelkanal", lambda: [f"{m} mm · {t}" for m in ["60×45", "80×60", "110×75"]
                                           for t in ["Kanal 2 m", "Bogen flach", "Bogen vertikal",
                                                     "Wanddurchführung", "Endstück"]], "St"),

    # ---- Werkzeug
    (r"Pressbacke V-Kontur", lambda: [f"{d} mm" for d in [12, 15, 18, 22, 28, 35, 42, 54]], "St"),
    (r"Pressbacke TH-Kontur", lambda: [f"{d} mm" for d in [16, 20, 26, 32, 40, 50, 63]], "St"),
    (r"Pressschlinge", lambda: [f"{d} mm inkl. Zwischenbacke" for d in [64, 66.7, 76.1, 88.9, 108]], "St"),
    (r"Akku-Pressmaschine", lambda: ["Kompakt bis 40 mm", "Standard bis 108 mm",
                                     "Set + 3 Backen V", "Set + 3 Backen TH"], "St"),
    (r"Rohrabschneider Kupfer", lambda: ["3–16 mm Mini", "3–35 mm", "6–67 mm", "Ersatzrädchen 2er"], "St"),
    (r"Gewindeschneidkluppe", lambda: ['Satz 1/2"–1 1/4" manuell', 'Satz 1/2"–2" manuell',
                                       'elektrisch bis 2"'], "St"),
    (r"Bohrer- & Bit-Sortimente", lambda: ["HSS-Kassette 1–10 mm", "HSS-Kassette 1–13 mm",
                                           "Betonbohrer-Set 4–12 mm", "SDS-plus-Set 5–12 mm",
                                           "Bit-Box 32-tlg.", "Bit-Box 61-tlg."], "St"),
    (r"Lochsäge", lambda: [f"Ø {d} mm Bi-Metall" for d in [35, 44, 51, 60, 68, 76, 83, 102, 111, 127, 152]], "St"),
    (r"Trennscheiben", lambda: [f"Ø {d} mm · {t} · 10er-Pack" for d in [115, 125, 230]
                                for t in ["Metall", "Inox dünn", "Stein"]], "Pack"),
    (r"Kernbohrgerät", lambda: ["Gerät 1500 W", "Bohrkrone Ø 68 mm", "Bohrkrone Ø 82 mm",
                                "Bohrkrone Ø 112 mm", "Bohrkrone Ø 132 mm", "Bohrkrone Ø 162 mm",
                                "Zentrierbohrer + Adapter"], "St"),
    (r"Wasserwaage", lambda: [f"{l} cm" for l in [40, 60, 80, 100, 120, 150, 180, 200]], "St"),
    (r"Stufenleiter", lambda: [f"{n} Stufen" for n in [3, 4, 5, 6, 7, 8]] +
                              ["Mehrzweck 3×3", "Mehrzweck 4×4", "Teleskop 3,8 m"], "St"),
    (r"Verlängerungskabel", lambda: ["10 m IP44", "25 m IP44", "Kabeltrommel 25 m", "Kabeltrommel 40 m",
                                     "Kabeltrommel 50 m"], "St"),
    (r"Arbeitshandschuhe", lambda: [f"Gr. {g} · {t}" for g in [8, 9, 10, 11]
                                    for t in ["Montage", "schnittfest C", "Nitril 12er-Pack"]], "Paar"),
    (r"Sicherheitsschuhe", lambda: [f"Gr. {g} · {t}" for g in range(39, 49)
                                    for t in ["Halbschuh S3", "Stiefel S3"]], "Paar"),
    (r"Arbeitshose", lambda: [f"Gr. {g} · {t}" for g in [44, 46, 48, 50, 52, 54, 56, 58, 60]
                              for t in ["Hose", "Bundjacke"]], "St"),
    (r"Atemschutzmaske", lambda: ["FFP2 · 10er", "FFP2 Ventil · 10er", "FFP3 Ventil · 5er"], "Pack"),
    (r"Rohreinfriergerät", lambda: ["elektrisch bis 2\"", "CO₂-Set bis 1\""], "St"),
    (r"Prüfpumpe", lambda: ["manuell 60 bar", "elektrisch 40 bar", "Luft-Prüfset mit Manometer"], "St"),
    (r"Akku-Bohrschrauber|Bohrhammer|Winkelschleifer|Säbelsäge|Baustaubsauger",
     lambda: ["Solo (ohne Akku)", "Set 2× 4,0 Ah + Lader"], "St"),
    (r"PP-R-Muffenschweißgerät", lambda: ["Set Heizdorne 20–40 mm", "Set Heizdorne 20–63 mm"], "St"),

    # ---- generische Auffangregeln
    (r"Gaskugelhahn|Gasströmungswächter", lambda: ['1/2"', '3/4"', '1"'], "St"),
    (r"", lambda: ["Standard"], "St"),  # Fallback: ein Artikel
]

KOMPILIERT = [(re.compile(m, re.I), v, e) for m, v, e in REGELN]


def artikelnummer(schluessel: str) -> str:
    n = zlib.crc32(schluessel.encode("utf-8"))
    z = "0123456789ABCDEFGHJKLMNPQRSTUVWXYZ"
    s = ""
    for _ in range(6):
        s = z[n % 34] + s
        n //= 34
    return "PHT-" + s


def main():
    basis = json.load(open(BASIS, encoding="utf-8"))
    produkte, sku_gesamt = [], 0
    for gewerk, kategorie, name, detail in basis:
        for muster, varianten_fn, einheit in KOMPILIERT:
            if muster.search(name) or (muster.pattern and muster.search(kategorie)):
                varianten = varianten_fn()
                break
        eintraege = [[v, artikelnummer(f"{name}|{v}")] for v in varianten]
        sku_gesamt += len(eintraege)
        produkte.append({"g": gewerk, "k": kategorie, "n": name, "d": detail,
                         "e": einheit, "v": eintraege})

    ZIEL_JSON.write_text(json.dumps(produkte, ensure_ascii=False, separators=(",", ":")),
                         encoding="utf-8")

    with open(ZIEL_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["sku", "item_name", "brand_name", "product_category",
                    "trade", "unit", "ean", "quantity"])
        for p in produkte:
            for ausf, nr in p["v"]:
                bezeichnung = p["n"] if ausf == "Standard" else f'{p["n"]} — {ausf}'
                w.writerow([nr, bezeichnung, "Profihaustechnik", p["k"], p["g"], p["e"], "", ""])

    je_gewerk = {}
    for p in produkte:
        je_gewerk[p["g"]] = je_gewerk.get(p["g"], 0) + len(p["v"])
    print(f"Produktgruppen: {len(produkte)}  |  Artikel (SKUs): {sku_gesamt}")
    for g, n in je_gewerk.items():
        print(f"  {g}: {n}")
    print(f"JSON: {ZIEL_JSON} ({ZIEL_JSON.stat().st_size // 1024} KB)")
    print(f"CSV:  {ZIEL_CSV} ({ZIEL_CSV.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
