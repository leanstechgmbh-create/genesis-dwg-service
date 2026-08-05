#!/usr/bin/env python3
"""Erzeugt Angebote und Rechnungen im AAM-Stil (AAM Handwerk & Montage,
Inhaber Mahit Ramovic) als HTML und optional als PDF.

AAM-Stil heisst: ausschliesslich AAM als Absender - eigenes Logo, eigene
Anschrift, eigene USt-IdNr./Steuernummer, eigenes Konto, 19 % MwSt.
Von der LEANS Tech GmbH taucht NICHTS auf (kein Logo, keine Adresse,
keine Bankverbindung), ausser der Nutzer verlangt es ausdruecklich.

Layout nachgebaut nach AAM-Rechnung RE260026 vom 30.07.2026.

Aufruf:
    python3 tools/aam_angebot.py auftrag.json [-o ausgabe.html] [--pdf]

Beispiel fuer auftrag.json:
{
  "typ": "Angebot",
  "nummer": "AN260027",
  "datum": "05.08.26",
  "empfaenger": ["Herrn", "Filip Rimac", "Musterstr. 1", "10787 Berlin"],
  "kostenstelle": "/",
  "bauvorhaben": "Hotel, Kleiststrasse 1, 10787 Berlin",
  "zusatzzeilen": ["Fabrikat: Geberit Silent-db20"],
  "datum_label": "Gueltig bis",
  "datum_wert": "30.09.2026",
  "abschnitte": [
    {"titel": "Schmutzwasserleitung DN 100", "positionen": [
      {"titel": "Abflussrohr Silent-db20 DN 100", "beschreibung": "Liefern und montieren ...",
       "menge": 53.5, "einheit": "m", "einzelpreis": 89.30}
    ]}
  ],
  "hinweise": "Angebot freibleibend."
}
"""
import argparse
import json
import pathlib
import subprocess
import sys

VORLAGEN = pathlib.Path(__file__).resolve().parent.parent / "vorlagen"
LOGO = VORLAGEN / "aam-logo.jpg"
MWST_SATZ = 0.19

CHROME_KANDIDATEN = [
    "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
    "/usr/bin/google-chrome",
]

CSS = """
@page{size:A4;margin:0}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:Arial,Helvetica,sans-serif;font-size:10pt;color:#000;width:210mm;padding:16mm 18mm 10mm}
.kopfzeile{display:flex;justify-content:space-between;align-items:flex-start}
.logo{width:19.6mm;height:auto;display:block}
.kopf-rechts{text-align:right;font-weight:bold;line-height:1.55}
.mail{font-family:Calibri,Arial,sans-serif;font-size:11pt;font-weight:bold;text-align:right;margin-top:2px}
.absenderzeile{font-style:italic;font-size:8pt;margin-top:14px;padding-bottom:2px}
.empf-zeile{display:flex;justify-content:space-between;align-items:flex-start;margin-top:4px}
.empfaenger{font-weight:bold;line-height:1.55}
.ortdatum{text-align:right;line-height:1.55}
.ortdatum .ort{font-family:Calibri,Arial,sans-serif;font-size:11pt}
.ortdatum .datum{font-style:italic}
h1{font-size:10pt;font-weight:bold;margin:52px 0 6px}
.dokmeta{line-height:1.62;margin-bottom:30px}
table.pos{width:100%;border-collapse:collapse;font-size:10pt}
table.pos thead th{font-weight:bold;padding:5px 4px;text-align:right;border-bottom:1px solid #000;white-space:nowrap}
table.pos thead th.l{text-align:left}
table.pos td{padding:5px 4px;text-align:right;vertical-align:top}
table.pos td.l{text-align:left}
table.pos td.nr{text-align:center;width:34px}
table.pos tbody tr td{border-bottom:1px solid #d5d5d5}
.detail{font-size:8.5pt;line-height:1.45;color:#333;margin-top:2px}
.abs-zeile td{font-weight:bold;padding-top:10px;border-bottom:1px solid #000 !important}
table.summen{width:100%;border-collapse:collapse;font-size:10pt;margin-top:14px}
table.summen td{padding:4px 4px;text-align:right}
table.summen td.lbl{text-align:left;width:55%;padding-left:47%;white-space:nowrap}
table.summen tr.b td{font-weight:bold}
table.summen tr.zahl td{font-weight:bold;border-top:1px solid #000}
.hinweis{font-size:8.5pt;line-height:1.5;color:#333;margin-top:26px}
.fuss{margin-top:40px;padding-top:6px;font-family:Calibri,Arial,sans-serif;font-size:8pt;line-height:1.5;
      display:flex;justify-content:space-between;border-top:1px solid #999}
.fuss div:nth-child(2){text-align:center}
.fuss div:nth-child(3){text-align:right}
"""


def eur(v):
    return f"{v:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.') + " &euro;"


def zahl(v):
    return f"{v:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')


def logo_datauri():
    import base64
    return "data:image/jpeg;base64," + base64.b64encode(LOGO.read_bytes()).decode()


def tabelle_bauen(abschnitte):
    """Liefert (html, nettosumme). Abschnittstitel sind optional."""
    zeilen, netto, nr = [], 0.0, 1
    for abschnitt in abschnitte:
        titel = abschnitt.get("titel")
        if titel:
            zeilen.append(f'    <tr class="abs-zeile"><td colspan="6" class="l">{titel}</td></tr>')
        for pos in abschnitt["positionen"]:
            menge = float(pos["menge"])
            ep = float(pos["einzelpreis"])
            betrag = round(menge * ep, 2)
            netto += betrag
            beschreibung = pos.get("beschreibung", "")
            detail = f'<div class="detail">{beschreibung}</div>' if beschreibung else ""
            zeilen.append(f"""    <tr>
      <td class="nr">{nr}</td>
      <td class="l"><strong>{pos["titel"]}</strong>{detail}</td>
      <td>{zahl(menge)}</td><td>{pos.get("einheit", "Stk.")}</td>
      <td>{eur(ep)}</td><td>{eur(betrag)}</td>
    </tr>""")
            nr += 1
    return "\n".join(zeilen), round(netto, 2)


def dokument_bauen(auftrag):
    typ = auftrag.get("typ", "Angebot")
    nummer_label = "Rechnungsnummer" if typ.lower().startswith("rechnung") else "Angebotsnummer"
    summen_label = "Zahlungsbetrag" if typ.lower().startswith("rechnung") else "Angebotsbetrag"

    tabelle, netto = tabelle_bauen(auftrag["abschnitte"])
    mwst = round(netto * MWST_SATZ, 2)
    brutto = round(netto + mwst, 2)

    meta = [f'{nummer_label}: {auftrag["nummer"]}',
            f'Kst.Nr.: {auftrag.get("kostenstelle", "/")}',
            f'Bauvorhaben: {auftrag.get("bauvorhaben", "")}']
    meta += auftrag.get("zusatzzeilen", [])
    if auftrag.get("datum_wert"):
        meta.append(f'{auftrag.get("datum_label", "Leistungsdatum")}: {auftrag["datum_wert"]}')

    html = f"""<!DOCTYPE html><html lang="de"><head><meta charset="UTF-8">
<title>{typ} {auftrag["nummer"]} - AAM Handwerk und Montage</title><style>{CSS}</style></head><body>

<div class="kopfzeile">
  <img class="logo" src="{logo_datauri()}" alt="AAM Handwerk &amp; Montage">
  <div>
    <div class="kopf-rechts">
      AAM Handwerk&amp;Montage<br>
      Scharnweberstr. 33<br>
      13405 Berlin<br>
      Tel.: +491629825633
    </div>
    <div class="mail">info@aam-handwerk-montage.de</div>
  </div>
</div>

<div class="absenderzeile">AAM Handwerk&amp;Montage * Scharnweberstr. 33 * 13405 Berlin</div>

<div class="empf-zeile">
  <div class="empfaenger">{"<br>".join(auftrag["empfaenger"])}</div>
  <div class="ortdatum">
    <span class="ort">Berlin</span> <span class="datum">{auftrag.get("datum", "")}</span>
  </div>
</div>

<h1>{typ}</h1>
<div class="dokmeta">{"<br>".join(meta)}</div>

<table class="pos">
  <thead>
    <tr>
      <th class="l" style="width:34px">Pos.</th>
      <th class="l">Bezeichnung</th>
      <th style="width:58px">Menge</th><th style="width:52px">Einheit</th>
      <th style="width:72px">Einzel &euro;</th><th style="width:82px">Gesamt &euro;</th>
    </tr>
  </thead>
  <tbody>
{tabelle}
  </tbody>
</table>

<table class="summen">
  <tr class="b"><td class="lbl">Gesamtbetrag Netto</td><td>{eur(netto)}</td></tr>
  <tr><td class="lbl">zzgl. 19% MwSt</td><td>{eur(mwst)}</td></tr>
  <tr class="zahl"><td class="lbl">{summen_label}</td><td>{eur(brutto)}</td></tr>
</table>

<div class="hinweis">{auftrag.get("hinweise", "")}</div>

<div class="fuss">
  <div>AAM Handwerk&amp;Montage<br>Scharnweberstr. 33<br>13405 Berlin<br>Tel.: +491629825633</div>
  <div>USt-IdNr.: DE460797759<br>Steuernummer: 17/484/02061</div>
  <div>Mahit Ramovic<br>Commerzbank<br>IBAN: DE80 1004 0000 0792 1190 00<br>BIC: COBADEFFXXX</div>
</div>

</body></html>"""
    return html, netto, mwst, brutto


def pdf_drucken(html_pfad, pdf_pfad):
    chrome = next((c for c in CHROME_KANDIDATEN if pathlib.Path(c).exists()), None)
    if not chrome:
        print("Kein Chromium gefunden - PDF uebersprungen.", file=sys.stderr)
        return False
    subprocess.run([chrome, "--headless", "--disable-gpu", "--no-sandbox",
                    "--no-pdf-header-footer", f"--print-to-pdf={pdf_pfad}",
                    f"file://{html_pfad.resolve()}"],
                   check=True, capture_output=True)
    return True


def main():
    ap = argparse.ArgumentParser(description="Angebot/Rechnung im AAM-Stil erzeugen")
    ap.add_argument("auftrag", help="JSON-Datei mit Kopfdaten und Positionen")
    ap.add_argument("-o", "--out", help="Ziel-HTML (Standard: neben der JSON-Datei)")
    ap.add_argument("--pdf", action="store_true", help="zusaetzlich PDF drucken")
    args = ap.parse_args()

    auftrag = json.loads(pathlib.Path(args.auftrag).read_text(encoding="utf-8"))
    html, netto, mwst, brutto = dokument_bauen(auftrag)

    ziel = pathlib.Path(args.out) if args.out else \
        pathlib.Path(args.auftrag).with_suffix(".html")
    ziel.write_text(html, encoding="utf-8")
    print(f"HTML   : {ziel}")

    if args.pdf:
        pdf = ziel.with_suffix(".pdf")
        if pdf_drucken(ziel, pdf):
            print(f"PDF    : {pdf}")

    print(f"Netto  : {zahl(netto)} EUR")
    print(f"MwSt   : {zahl(mwst)} EUR")
    print(f"Brutto : {zahl(brutto)} EUR")


if __name__ == "__main__":
    main()
