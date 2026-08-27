#!/usr/bin/env python3
"""Depot-Kennzahlen aus einer CSV rechnen (nur Standardbibliothek).

Aufruf:
    python3 tools/depot_check.py depot.csv
    python3 tools/depot_check.py depot.csv --json

Erwartetes CSV-Format siehe vorlagen/depot-muster.csv (Semikolon-getrennt,
deutsche Zahlen mit Komma sind erlaubt). Pflichtspalten: Wert, Stueck, Kurs.
Alles andere ist optional und wird weggelassen, wenn es fehlt.

Das Skript bewertet nicht und empfiehlt nichts — es rechnet nur.
"""

import argparse
import csv
import json
import sys
from collections import defaultdict

PFLICHT = ("Wert", "Stueck", "Kurs")


def zahl(text):
    """'1.234,56' / '1234.56' / '' -> float. Leeres Feld ergibt 0.0."""
    if text is None:
        return 0.0
    t = str(text).strip().replace(" ", "").replace(" ", "")
    t = t.replace("%", "").replace("€", "").replace("EUR", "")
    if not t:
        return 0.0
    # Deutsches Format: Punkt ist Tausendertrenner, Komma ist Dezimaltrenner.
    if "," in t:
        t = t.replace(".", "").replace(",", ".")
    try:
        return float(t)
    except ValueError:
        raise SystemExit(f"Kann Zahl nicht lesen: {text!r}")


def lies_depot(pfad):
    with open(pfad, newline="", encoding="utf-8-sig") as f:
        probe = f.read(4096)
        f.seek(0)
        trenner = ";" if probe.count(";") >= probe.count(",") else ","
        zeilen = list(csv.DictReader(f, delimiter=trenner))

    if not zeilen:
        raise SystemExit(f"{pfad} enthaelt keine Positionen.")

    spalten = {s.strip() for s in zeilen[0].keys() if s}
    fehlt = [s for s in PFLICHT if s not in spalten]
    if fehlt:
        raise SystemExit(
            "Diese Pflichtspalten fehlen: " + ", ".join(fehlt) +
            "\nVorbild: vorlagen/depot-muster.csv"
        )

    positionen = []
    for i, z in enumerate(zeilen, start=2):
        name = (z.get("Wert") or "").strip()
        if not name:
            continue  # Leerzeile
        stueck = zahl(z.get("Stueck"))
        kurs = zahl(z.get("Kurs"))
        kaufkurs = zahl(z.get("Kaufkurs"))
        wert = stueck * kurs
        einstand = stueck * kaufkurs
        positionen.append({
            "zeile": i,
            "wert": name,
            "isin": (z.get("ISIN") or "").strip(),
            "typ": (z.get("Typ") or "unbekannt").strip() or "unbekannt",
            "region": (z.get("Region") or "unbekannt").strip() or "unbekannt",
            "branche": (z.get("Branche") or "unbekannt").strip() or "unbekannt",
            "waehrung": (z.get("Waehrung") or "EUR").strip() or "EUR",
            "stueck": stueck,
            "kurs": kurs,
            "kaufkurs": kaufkurs,
            "ter": zahl(z.get("TER")),
            "ziel": zahl(z.get("Ziel")),
            "marktwert": wert,
            "einstand": einstand,
            "gv": wert - einstand if einstand else 0.0,
        })

    if not positionen:
        raise SystemExit(f"{pfad}: keine Zeile mit einem Wert in der Spalte 'Wert'.")
    return positionen


def gruppiere(positionen, feld, gesamt):
    summen = defaultdict(float)
    for p in positionen:
        summen[p[feld]] += p["marktwert"]
    return [
        {"name": k, "wert": v, "anteil": (v / gesamt * 100) if gesamt else 0.0}
        for k, v in sorted(summen.items(), key=lambda kv: -kv[1])
    ]


def auswerten(positionen):
    gesamt = sum(p["marktwert"] for p in positionen)
    if gesamt <= 0:
        raise SystemExit("Gesamtwert ist 0 — stimmen die Spalten 'Stueck' und 'Kurs'?")

    for p in positionen:
        p["anteil"] = p["marktwert"] / gesamt * 100
        p["gv_prozent"] = (p["gv"] / p["einstand"] * 100) if p["einstand"] else 0.0

    nach_groesse = sorted(positionen, key=lambda p: -p["marktwert"])
    einstand_gesamt = sum(p["einstand"] for p in positionen)

    # Herfindahl-Index ueber die Positionsanteile: 1/HHI = effektive Anzahl
    # unabhaengiger Positionen. 10 gleich grosse Werte ergeben 10,0.
    hhi = sum((p["anteil"] / 100) ** 2 for p in positionen)

    ter_gewichtet = sum(p["ter"] * p["marktwert"] for p in positionen) / gesamt

    abweichungen = []
    if any(p["ziel"] for p in positionen):
        for p in nach_groesse:
            if not p["ziel"]:
                continue
            diff_prozent = p["anteil"] - p["ziel"]
            abweichungen.append({
                "wert": p["wert"],
                "ist": p["anteil"],
                "ziel": p["ziel"],
                "diff": diff_prozent,
                "betrag": diff_prozent / 100 * gesamt,
            })
        abweichungen.sort(key=lambda a: -abs(a["diff"]))

    return {
        "positionen": nach_groesse,
        "gesamt": gesamt,
        "einstand_gesamt": einstand_gesamt,
        "gv_gesamt": gesamt - einstand_gesamt if einstand_gesamt else 0.0,
        "gv_gesamt_prozent": (
            (gesamt - einstand_gesamt) / einstand_gesamt * 100
        ) if einstand_gesamt else 0.0,
        "anzahl": len(positionen),
        "groesste": nach_groesse[0],
        "top5_anteil": sum(p["anteil"] for p in nach_groesse[:5]),
        "hhi": hhi,
        "effektive_positionen": 1 / hhi if hhi else 0.0,
        "ter_gewichtet": ter_gewichtet,
        "ter_kosten_jahr": ter_gewichtet / 100 * gesamt,
        "nach_typ": gruppiere(positionen, "typ", gesamt),
        "nach_region": gruppiere(positionen, "region", gesamt),
        "nach_branche": gruppiere(positionen, "branche", gesamt),
        "nach_waehrung": gruppiere(positionen, "waehrung", gesamt),
        "abweichungen": abweichungen,
    }


def eur(betrag):
    s = f"{betrag:,.2f}"
    return s.replace(",", "#").replace(".", ",").replace("#", ".") + " EUR"


def prozent(wert, stellen=1):
    s = f"{wert:,.{stellen}f}"
    return s.replace(",", "#").replace(".", ",").replace("#", ".") + " %"


def zahl_de(wert, stellen=1):
    return f"{wert:.{stellen}f}".replace(".", ",")


def block(titel, eintraege):
    zeilen = [f"\n{titel}"]
    for e in eintraege:
        zeilen.append(f"  {e['name']:<24} {eur(e['wert']):>16}   {prozent(e['anteil']):>7}")
    return "\n".join(zeilen)


def drucke(a):
    print("=" * 72)
    print("DEPOT-CHECK")
    print("=" * 72)
    print(f"Positionen:            {a['anzahl']}")
    print(f"Depotwert:             {eur(a['gesamt'])}")
    if a["einstand_gesamt"]:
        print(f"Einstand:              {eur(a['einstand_gesamt'])}")
        print(f"Gewinn/Verlust:        {eur(a['gv_gesamt'])}  ({prozent(a['gv_gesamt_prozent'])})")

    print("\nKONZENTRATION")
    g = a["groesste"]
    print(f"  Groesste Position:   {g['wert']} mit {prozent(g['anteil'])}")
    print(f"  Top 5 zusammen:      {prozent(a['top5_anteil'])}")
    print(f"  Effektive Positionen:{zahl_de(a['effektive_positionen']):>6}"
          f"  (von {a['anzahl']} tatsaechlichen)")

    if a["ter_gewichtet"]:
        print("\nKOSTEN")
        print(f"  TER gewichtet:       {prozent(a['ter_gewichtet'], 2)} pro Jahr")
        print(f"  entspricht:          {eur(a['ter_kosten_jahr'])} pro Jahr")

    print(block("NACH ANLAGEART", a["nach_typ"]))
    print(block("NACH REGION", a["nach_region"]))
    print(block("NACH BRANCHE", a["nach_branche"]))
    print(block("NACH WAEHRUNG", a["nach_waehrung"]))

    print("\nEINZELPOSITIONEN")
    print(f"  {'Wert':<24} {'Marktwert':>16} {'Anteil':>8} {'G/V':>10}")
    for p in a["positionen"]:
        gv = prozent(p["gv_prozent"]) if p["einstand"] else "-"
        print(f"  {p['wert'][:24]:<24} {eur(p['marktwert']):>16} "
              f"{prozent(p['anteil']):>8} {gv:>10}")

    if a["abweichungen"]:
        print("\nABWEICHUNG VON DER ZIELGEWICHTUNG")
        print(f"  {'Wert':<24} {'Ist':>8} {'Ziel':>8} {'Diff':>8} {'Betrag':>16}")
        for w in a["abweichungen"]:
            richtung = "verkaufen" if w["diff"] > 0 else "zukaufen"
            print(f"  {w['wert'][:24]:<24} {prozent(w['ist']):>8} "
                  f"{prozent(w['ziel']):>8} {prozent(w['diff']):>8} "
                  f"{eur(abs(w['betrag'])):>16}  {richtung}")

    print("\n" + "-" * 72)
    print("Reine Rechnung, keine Anlageberatung.")


def main():
    p = argparse.ArgumentParser(description="Depot-Kennzahlen aus einer CSV rechnen.")
    p.add_argument("csv", help="Pfad zur Depot-CSV (Vorbild: vorlagen/depot-muster.csv)")
    p.add_argument("--json", action="store_true", help="Ergebnis als JSON ausgeben")
    args = p.parse_args()

    ergebnis = auswerten(lies_depot(args.csv))

    if args.json:
        json.dump(ergebnis, sys.stdout, ensure_ascii=False, indent=2)
        print()
    else:
        drucke(ergebnis)


if __name__ == "__main__":
    main()
