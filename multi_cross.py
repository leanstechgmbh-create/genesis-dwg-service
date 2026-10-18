"""Multi Cross Anlagen — Analyse und Fehlerprüfung in DXF/DWG.

Multi Cross = Mehrzonen-Klimaanlage: 1 Außengerät (AG) → mehrere Innengeräte (IG).
Typische Systemgrenzen:
  - max. 8 IG pro AG (herstellerabhängig)
  - Kältemittelleitungslänge max. 150 m (gesamt), max. 50 m IG-seitig
  - Höhenunterschied AG↔IG max. 30 m (AG oben) / 15 m (AG unten)
  - IG-Gesamtleistung 50–130 % der AG-Nennleistung

Der Scanner sucht in DXF/DWG nach:
  - Blöcken und Texten mit AG/IG-Kennzeichnung (deutsch und englisch)
  - Klima-/Kälteschichten (KLIMA, KAELTE, VRF, VRV, SPLIT …)
  - Y-Abzweigen und Verteilerblöcken (VERTEILER, Y-STUECK, BRANCH)
  - Alarmhinweisen aus Steuerungs-Exports (MB Alm, Dringend, 01.01.2003)
"""
import re
import ezdxf
from typing import Tuple

# Schichtnamen, die auf Klima-/Kälteanlagen hinweisen
_KLIMA_LAYER = re.compile(r"(klima|kaelt|k[aä]lte|vrf|vrv|split|multi|refrig|kond|verdampf)", re.I)

# Texte/Blocknamen für Außen- und Innengeräte
_AG_TEXT = re.compile(r"\b(AG|A\.?G\.?|AU[ÃS]EN|AUSSEN|OUTDOOR|KOND[EN]?|SPLIT\s*OUT)", re.I)
_IG_TEXT = re.compile(r"\b(IG|I\.?G\.?|INNEN|INDOOR|VERDAMPF|TRUHE|CASSETT|SPLIT\s*IN|UNIT\s*\d+)", re.I)
_BRANCH = re.compile(r"(VERTEILER|Y.?STÜCK|Y.?STUECK|BRANCH|ABZWEIG|HEADER)", re.I)

# Alarmhinweise, die aus BMS-Exports/Plänen übernommen werden können
_ALARM_HINWEIS = re.compile(r"(MB\s*Alm|01\.01\.2003|Dringend|Alarm\s*A|Batterie|Uhrzeit\s*fehlt)", re.I)

GRENZWERTE = {
    "max_ig_pro_ag": 8,
    "warn_ig_pro_ag": 6,       # Warnung ab hier, Fehler erst ab max
    "max_leitungslaenge_m": 150,
    "max_hoehenunterschied_m": 30,
    "min_kapazitaet_pct": 50,
    "max_kapazitaet_pct": 130,
}


def _textinhalt(e) -> str:
    t = e.dxftype()
    try:
        if t == "TEXT":
            return e.dxf.text or ""
        if t == "MTEXT":
            return e.plain_mtext() if hasattr(e, "plain_mtext") else (e.text or "")
        if t == "INSERT":
            return e.dxf.name or ""
    except Exception:
        return ""
    return ""


def _position(e) -> Tuple[float, float]:
    try:
        if hasattr(e.dxf, "insert"):
            p = e.dxf.insert
        elif hasattr(e.dxf, "center"):
            p = e.dxf.center
        elif hasattr(e.dxf, "start"):
            p = e.dxf.start
        else:
            return (0.0, 0.0)
        return (round(float(p[0]), 1), round(float(p[1]), 1))
    except Exception:
        return (0.0, 0.0)


def analysiere(dxf_pfad: str) -> dict:
    """Liest die DXF-Datei und erstellt einen Multi-Cross-Anlagen-Bericht.

    Rückgabe-Dict:
      schema_typ        str   "Multi Cross" / "Einzel-Split" / "unbekannt"
      klima_layer       list  gefundene Schichtnamen
      aussengeraete     list  [{text, layer, pos}]
      innengeraete      list  [{text, layer, pos}]
      abzweige          list  [{text, layer, pos}]
      alarm_hinweise    list  Texte, die auf BMS-Alarme hindeuten
      anzahl_ag         int
      anzahl_ig         int
      warnungen         list  Hinweise (kein Fehler, aber prüfenswert)
      fehler            list  Regelwidrigkeiten
      ok                bool  True wenn keine Fehler
    """
    doc = ezdxf.readfile(dxf_pfad)
    msp = doc.modelspace()

    ags, igs, abzweige, alarm_hinweise = [], [], [], []
    klima_layer: list = []
    warnungen: list = []
    fehler: list = []

    for e in msp:
        try:
            layer = str(e.dxf.layer) if hasattr(e.dxf, "layer") else ""
        except Exception:
            layer = ""
        text = _textinhalt(e)
        pos = _position(e)

        if _KLIMA_LAYER.search(layer) and layer not in klima_layer:
            klima_layer.append(layer)

        if _ALARM_HINWEIS.search(text):
            alarm_hinweise.append({"text": text.strip()[:80], "layer": layer, "pos": list(pos)})

        if _AG_TEXT.search(text):
            ags.append({"text": text.strip()[:60], "layer": layer, "pos": list(pos)})
        elif _IG_TEXT.search(text):
            igs.append({"text": text.strip()[:60], "layer": layer, "pos": list(pos)})
        elif _BRANCH.search(text):
            abzweige.append({"text": text.strip()[:60], "layer": layer, "pos": list(pos)})

    n_ag = len(ags)
    n_ig = len(igs)

    # --- Alarme aus BMS-Export ---
    if alarm_hinweise:
        warnungen.append(
            f"{len(alarm_hinweise)} BMS-Alarmhinweis(e) im Plan gefunden "
            "(z. B. 'MB Alm', '01.01.2003'). Ursache meist: Pufferbatterie leer → "
            "Uhr auf Werksreset (01.01.2003). Lösung: Uhrzeit neu setzen, "
            "Batterie tauschen, Alarm quittieren."
        )

    # --- Komponenten-Erkennung ---
    if n_ag == 0 and n_ig == 0:
        warnungen.append(
            "Keine Klima-Komponenten (AG/IG) erkannt. "
            "Evtl. andere Beschriftungskonvention oder kein Multi-Cross-Schema."
        )
        schema_typ = "unbekannt"
    else:
        # Schema-Typ bestimmen
        if n_ig <= 1:
            schema_typ = "Einzel-Split"
        else:
            schema_typ = "Multi Cross"

        if n_ag == 0:
            fehler.append("Außengerät (AG) nicht gefunden — Schema unvollständig.")
        elif n_ag > 1:
            warnungen.append(
                f"{n_ag} Außengeräte erkannt. Bitte prüfen: mehrere unabhängige "
                "Anlagen oder Kaskaden-System?"
            )

        if n_ig == 0:
            warnungen.append("Kein Innengerät (IG) erkannt — Schema unvollständig?")
        elif n_ig == 1:
            warnungen.append(
                "Nur 1 Innengerät gefunden. Für Multi Cross mind. 2 IG erforderlich."
            )
        else:
            ig_pro_ag = n_ig / n_ag if n_ag else n_ig
            if ig_pro_ag > GRENZWERTE["max_ig_pro_ag"]:
                fehler.append(
                    f"Zu viele Innengeräte: {n_ig} IG bei {n_ag} AG "
                    f"= {ig_pro_ag:.1f} IG/AG. "
                    f"Grenzwert: {GRENZWERTE['max_ig_pro_ag']} IG/AG. "
                    "Prüfen: Systemauslegung, Hersteller-Spezifikation, Kaskade."
                )
            elif ig_pro_ag > GRENZWERTE["warn_ig_pro_ag"]:
                warnungen.append(
                    f"{ig_pro_ag:.1f} IG/AG — nahe am Grenzwert "
                    f"({GRENZWERTE['max_ig_pro_ag']}). Kapazität prüfen."
                )

        if n_ag and n_ig and not abzweige:
            warnungen.append(
                "Kein Y-Abzweig / Verteiler erkannt. "
                "Bei Multi Cross wird ein Kältemittel-Verteiler erwartet."
            )

    return {
        "schema_typ": schema_typ if (n_ag or n_ig) else "unbekannt",
        "klima_layer": klima_layer,
        "aussengeraete": ags,
        "innengeraete": igs,
        "abzweige": abzweige,
        "alarm_hinweise": alarm_hinweise,
        "anzahl_ag": n_ag,
        "anzahl_ig": n_ig,
        "warnungen": warnungen,
        "fehler": fehler,
        "ok": len(fehler) == 0,
    }
