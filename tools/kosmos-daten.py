#!/usr/bin/env python3
"""LEANS Kosmos — Daten fuer das Cockpit bauen.

Nimmt das Master-Register (CSV-Export aus dem Drive) und deine Zuordnung
(welche Rechnung gehoert zu welchem Projekt und Kunden) und schreibt daraus
die Datei, die das Cockpit liest.

    python3 tools/kosmos-daten.py

Liest
    kosmos/zuordnung.json                 Projekte, Kunden, Angebote, Status
    kosmos/quellen/*.csv                  Master <Jahr> Ausgang.csv (optional)

Schreibt
    kosmos/daten.privat.js                wird von index.html nach daten.js geladen
                                          und ueberschreibt die Beispieldaten

Beides — Zuordnung und Ergebnis — steht in .gitignore: die echten Zahlen
bleiben auf deinem Rechner.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
KOSMOS = WURZEL / "kosmos"

TYPEN = ("projekt", "kunde", "rechnung", "angebot", "wartung", "aufgabe")


# ---------------------------------------------------------------- Hilfsmittel

def kennung(text: str, praefix: str = "") -> str:
    """Aus 'Beispielstr. 12' wird 'bv-beispielstr-12'."""
    roh = unicodedata.normalize("NFKD", text.lower())
    roh = (roh.replace("ä", "ae").replace("ö", "oe")
              .replace("ü", "ue").replace("ß", "ss"))
    roh = "".join(c for c in roh if not unicodedata.combining(c))
    roh = re.sub(r"[^a-z0-9]+", "-", roh).strip("-")
    return (praefix + roh) if praefix else roh


def betrag(text: str) -> float | None:
    """'14.000,00' und '14000.00' werden beide zu 14000.0."""
    if not text:
        return None
    t = text.strip().replace(" ", "").replace(" ", "").replace("EUR", "")
    if "," in t:
        t = t.replace(".", "").replace(",", ".")
    try:
        return round(float(t), 2)
    except ValueError:
        return None


def rechnungsart(dateiname: str) -> str:
    """'2. AR 2026-2 - LEANS ... .pdf'  ->  '2. AR'."""
    d = dateiname.upper().replace("_", " ")
    m = re.match(r"\s*(\d+)\s*\.?\s*(?:AR|ABSCHLAGSRECHNUNG)\b", d)
    if m:
        return f"{m.group(1)}. AR"
    if "SCHLUSS" in d:
        return "Schlussrechnung"
    if "ABSCHLAG" in d or re.search(r"\bAR\b", d):
        return "AR"
    return "Rechnung"


# ---------------------------------------------------------------- Register

def register_lesen(pfade: list[Path], meldungen: list[str]) -> dict[str, dict]:
    """Alle Ausgangsrechnungen aus den CSV-Exporten, Schluessel = Rechnungsnummer."""
    gefunden: dict[str, dict] = {}

    for pfad in pfade:
        try:
            text = pfad.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            text = pfad.read_text(encoding="cp1252")

        trenner = ";" if text.count(";") >= text.count(",") else ","
        zeilen = csv.DictReader(text.splitlines(), delimiter=trenner)
        anzahl = 0

        for z in zeilen:
            felder = {(k or "").strip(): (v or "").strip() for k, v in z.items()}
            if felder.get("Typ", "").lower() not in ("", "ausgang"):
                continue
            if felder.get("Kategorie", "").lower() not in ("", "rechnung"):
                continue

            nr = felder.get("Rechnungsnr", "")
            # '2026-31_LEANS_Tech_GmbH_11231_09_EUR' -> '2026-31'
            m = re.match(r"(\d{4}-\d+)", nr)
            if not m:
                continue
            nr = m.group(1)

            eintrag = {
                "nr": nr,
                "netto": betrag(felder.get("Betrag_EUR", "")),
                "datum": felder.get("Datum", "") or None,
                "art": rechnungsart(felder.get("Datei", "")),
                "quelle": pfad.name,
            }
            if nr in gefunden and gefunden[nr]["netto"] != eintrag["netto"]:
                meldungen.append(
                    f"  ! {nr}: zwei verschiedene Betraege im Register "
                    f"({gefunden[nr]['netto']} / {eintrag['netto']}) — der erste gilt")
                continue
            gefunden[nr] = eintrag
            anzahl += 1

        meldungen.append(f"  Register {pfad.name}: {anzahl} Ausgangsrechnungen")

    return gefunden


# ---------------------------------------------------------------- Knoten bauen

def knoten_bauen(zuordnung: dict, register: dict[str, dict],
                 unzugeordnet: bool, meldungen: list[str]) -> list[dict]:
    knoten: list[dict] = []
    anhang: dict[str, list[str]] = {}      # projekt-id -> ids, die daran haengen

    def anhaengen(projekt_id: str | None, knoten_id: str) -> None:
        if projekt_id:
            anhang.setdefault(projekt_id, []).append(knoten_id)

    # --- Kunden ---------------------------------------------------------
    kunden_id: dict[str, str] = {}
    for k in zuordnung.get("kunden", []):
        kid = k.get("id") or kennung(k["titel"], "kd-")
        kunden_id[k.get("kurz", k["titel"])] = kid
        kunden_id[kid] = kid
        knoten.append({
            "id": kid, "typ": "kunde", "bereich": k.get("bereich", "business"),
            "titel": k["titel"], "info": k.get("info", ""), "verbunden": [],
        })

    def kunde_von(eintrag: dict) -> str | None:
        name = eintrag.get("kunde")
        if not name:
            return None
        if name in kunden_id:
            return kunden_id[name]
        meldungen.append(f"  ! Kunde '{name}' ist in zuordnung.json nicht angelegt")
        return None

    # --- Projekte -------------------------------------------------------
    projekt_id: dict[str, str] = {}
    projekte: list[dict] = []
    for p in zuordnung.get("projekte", []):
        pid = p.get("id") or kennung(p["titel"], "bv-")
        projekt_id[p.get("kurz", p["titel"])] = pid
        projekt_id[pid] = pid
        eintrag = {
            "id": pid, "typ": "projekt", "bereich": p.get("bereich", "business"),
            "titel": p["titel"], "info": p.get("info", ""), "verbunden": [],
        }
        projekte.append(eintrag)
        knoten.append(eintrag)
        kid = kunde_von(p)
        if kid:
            eintrag["verbunden"].append(kid)

    def projekt_von(eintrag: dict) -> str | None:
        name = eintrag.get("projekt")
        if not name:
            return None
        if name in projekt_id:
            return projekt_id[name]
        meldungen.append(f"  ! Projekt '{name}' ist in zuordnung.json nicht angelegt")
        return None

    # --- Rechnungen aus der Zuordnung -----------------------------------
    benutzt: set[str] = set()
    for r in zuordnung.get("rechnungen", []):
        nr = str(r["nr"])
        benutzt.add(nr)
        aus_register = register.get(nr)
        netto = r.get("netto")
        if netto is None and aus_register:
            netto = aus_register["netto"]
        if (netto is not None and aus_register
                and aus_register["netto"] is not None
                and abs(netto - aus_register["netto"]) > 0.005):
            meldungen.append(
                f"  ! {nr}: Zuordnung sagt {netto:.2f} €, Register sagt "
                f"{aus_register['netto']:.2f} € — Zuordnung gilt")

        rid = r.get("id") or kennung(nr, "ar-")
        art = r.get("art") or (aus_register["art"] if aus_register else "Rechnung")
        eintrag = {
            "id": rid, "typ": "rechnung", "bereich": r.get("bereich", "business"),
            "titel": r.get("titel") or f"{nr} · {art}",
            "info": r.get("info", ""),
            "netto": netto,
            "status": r.get("status", "unbekannt"),
            "verbunden": [],
        }
        if r.get("faellig"):
            eintrag["faellig"] = r["faellig"]
        kid = kunde_von(r)
        if kid:
            eintrag["verbunden"].append(kid)
        knoten.append(eintrag)
        anhaengen(projekt_von(r), rid)

    # --- Rechnungen, die nur im Register stehen --------------------------
    if unzugeordnet:
        offen_im_register = [n for n in sorted(register) if n not in benutzt]
        for nr in offen_im_register:
            e = register[nr]
            knoten.append({
                "id": kennung(nr, "ar-"), "typ": "rechnung", "bereich": "business",
                "titel": f"{nr} · {e['art']}",
                "info": "aus dem Register · noch keinem Projekt zugeordnet",
                "netto": e["netto"], "status": "unbekannt", "verbunden": [],
            })
        if offen_im_register:
            meldungen.append(
                f"  {len(offen_im_register)} Rechnungen ohne Zuordnung "
                f"(blass, zaehlen nicht als offen): {', '.join(offen_im_register)}")

    # --- Angebote, Wartung, offene Punkte -------------------------------
    for a in zuordnung.get("angebote", []):
        aid = a.get("id") or kennung(a["titel"], "ang-")
        eintrag = {
            "id": aid, "typ": "angebot", "bereich": a.get("bereich", "business"),
            "titel": a["titel"], "info": a.get("info", ""),
            "netto": a.get("netto"), "status": a.get("status", "offen"),
            "verbunden": [],
        }
        if a.get("gueltig"):
            eintrag["gueltig"] = a["gueltig"]
        kid = kunde_von(a)
        if kid:
            eintrag["verbunden"].append(kid)
        knoten.append(eintrag)
        anhaengen(projekt_von(a), aid)

    for w in zuordnung.get("wartung", []):
        wid = w.get("id") or kennung(w["titel"], "wtg-")
        eintrag = {
            "id": wid, "typ": "wartung", "bereich": w.get("bereich", "business"),
            "titel": w["titel"], "info": w.get("info", ""),
            "netto": w.get("netto"), "verbunden": [],
        }
        if w.get("termin"):
            eintrag["termin"] = w["termin"]
        kid = kunde_von(w)
        if kid:
            eintrag["verbunden"].append(kid)
        knoten.append(eintrag)
        anhaengen(projekt_von(w), wid)

    for t in zuordnung.get("aufgaben", []):
        tid = t.get("id") or kennung(t["titel"], "auf-")
        knoten.append({
            "id": tid, "typ": "aufgabe", "bereich": t.get("bereich", "business"),
            "titel": t["titel"], "info": t.get("info", ""), "verbunden": [],
        })
        anhaengen(projekt_von(t), tid)

    # --- Privat (frei gepflegt) -----------------------------------------
    for p in zuordnung.get("privat", []):
        typ = p.get("typ", "aufgabe")
        if typ not in TYPEN:
            meldungen.append(f"  ! privat: unbekannter Typ '{typ}' bei '{p['titel']}'")
            typ = "aufgabe"
        eintrag = {
            "id": p.get("id") or kennung(p["titel"], "pv-"), "typ": typ,
            "bereich": "privat", "titel": p["titel"], "info": p.get("info", ""),
            "verbunden": list(p.get("verbunden", [])),
        }
        for feld in ("netto", "status", "faellig", "gueltig", "termin"):
            if p.get(feld) is not None:
                eintrag[feld] = p[feld]
        knoten.append(eintrag)

    # --- Projekte mit ihren Vorgaengen verbinden -------------------------
    for p in projekte:
        p["verbunden"].extend(anhang.get(p["id"], []))

    # --- Pruefen ---------------------------------------------------------
    alle = {k["id"] for k in knoten}
    doppelt = [i for i in alle if sum(1 for k in knoten if k["id"] == i) > 1]
    for i in sorted(doppelt):
        meldungen.append(f"  ! id '{i}' kommt mehrfach vor — der Kosmos zeigt sie nur einmal")
    for k in knoten:
        for ziel in k["verbunden"]:
            if ziel not in alle:
                meldungen.append(f"  ! '{k['id']}' zeigt auf '{ziel}', das es nicht gibt")

    return knoten


# ---------------------------------------------------------------- Schreiben

def schreiben(ziel: Path, firma: str, stand: str, knoten: list[dict]) -> None:
    zeilen = [
        "/* ==========================================================================",
        "   LEANS KOSMOS — erzeugte Daten. NICHT von Hand aendern.",
        "   Gebaut von tools/kosmos-daten.py aus kosmos/zuordnung.json",
        "   und dem Master-Register in kosmos/quellen/.",
        f"   Stand: {stand}",
        "   ========================================================================== */",
        "",
        "window.KOSMOS_DATEN = {",
        f"  firma: {json.dumps(firma, ensure_ascii=False)},",
        f"  stand: {json.dumps(stand, ensure_ascii=False)},",
        "  knoten: [",
    ]
    for k in knoten:
        zeilen.append("    " + json.dumps(k, ensure_ascii=False) + ",")
    zeilen += ["  ]", "};", ""]

    ziel.write_text("\n".join(zeilen), encoding="utf-8")


# ---------------------------------------------------------------- Hauptlauf

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Baut kosmos/daten.privat.js aus Zuordnung und Master-Register.")
    p.add_argument("--zuordnung", type=Path, default=KOSMOS / "zuordnung.json")
    p.add_argument("--register", type=Path, nargs="*", default=None,
                   help="CSV-Dateien; ohne Angabe alle in kosmos/quellen/")
    p.add_argument("--ziel", type=Path, default=KOSMOS / "daten.privat.js")
    p.add_argument("--nur-zugeordnet", action="store_true",
                   help="Rechnungen ohne Projekt-Zuordnung weglassen")
    a = p.parse_args(argv)

    if not a.zuordnung.exists():
        vorlage = KOSMOS / "zuordnung.beispiel.json"
        print(f"Keine Zuordnung gefunden: {a.zuordnung}")
        print(f"Kopiere {vorlage.name} nach {a.zuordnung.name} und trage deine Vorgaenge ein.")
        return 1

    try:
        zuordnung = json.loads(a.zuordnung.read_text(encoding="utf-8"))
    except json.JSONDecodeError as fehler:
        print(f"zuordnung.json laesst sich nicht lesen — Zeile {fehler.lineno}: {fehler.msg}")
        print("Meist fehlt ein Komma oder eine Anfuehrungszeichen-Klammer.")
        return 1

    if a.register is not None:
        register_dateien = [pf for pf in a.register if pf.exists()]
    else:
        ordner = KOSMOS / "quellen"
        register_dateien = sorted(ordner.glob("*.csv")) if ordner.is_dir() else []

    meldungen: list[str] = []
    register = register_lesen(register_dateien, meldungen) if register_dateien else {}
    if not register_dateien:
        meldungen.append("  Kein Register gefunden — es gelten nur die Betraege aus der Zuordnung.")

    knoten = knoten_bauen(zuordnung, register, not a.nur_zugeordnet, meldungen)

    quellen = ", ".join(pf.name for pf in register_dateien) or "ohne Register"
    stand = f"{date.today().isoformat()} · {quellen}"
    schreiben(a.ziel, zuordnung.get("firma", "LEANS TECH GMBH"), stand, knoten)

    zahl = {t: sum(1 for k in knoten if k["typ"] == t) for t in TYPEN}
    offen = sum(k.get("netto") or 0 for k in knoten
                if k["typ"] == "rechnung" and k.get("status") == "gestellt")

    print(f"{a.ziel.relative_to(WURZEL)} geschrieben — {len(knoten)} Knoten")
    print("  " + " · ".join(f"{t}: {n}" for t, n in zahl.items() if n))
    print(f"  offene Rechnungen (Status 'gestellt'): {offen:,.2f} €"
          .replace(",", "#").replace(".", ",").replace("#", "."))
    for m in meldungen:
        print(m)
    print("\nCockpit neu laden (F5) — fertig.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
