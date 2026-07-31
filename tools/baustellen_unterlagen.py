#!/usr/bin/env python3
"""Baustellen-Unterlagen für ein Bauvorhaben erzeugen (LEANS Tech GmbH).

Erstellt den kompletten Satz Nachweise/Erklärungen, den Generalunternehmer vor
Arbeitsbeginn verlangen (Anschreiben mit Checkliste, MiLoG-Eigenerklärung,
Mitarbeiterliste, Nachunternehmererklärung, Benennung Bauleiter,
Fachunternehmer-/Fachbauleitererklärung, Gefährdungsbeurteilung, Bautagebuch)
sowie den Antrag auf eine neue Freistellungsbescheinigung nach § 48b EStG.

Aufruf:
    python3 tools/baustellen_unterlagen.py [--projekt projekt.json] [--out ORDNER]

Die Projektdaten stehen in PROJEKT und lassen sich per JSON-Datei überschreiben.
Ausgabe: HTML + PDF (gerendert mit dem vorinstallierten Chromium).
"""
import argparse, base64, json, pathlib, subprocess, sys
from datetime import date

REPO = pathlib.Path(__file__).resolve().parent.parent

PROJEKT = {
    "bv": "17899 – Hallesches Ufer 40, EG, „The Visit“ Coffee Rösterei & Gastro, 10963 Berlin",
    "bv_kurz": "BV 17899",
    "auftrag_nr": "26-17899-AG01-NU20.01",
    "auftraggeber": "apoprojekt GmbH, Holstenwall 5, 20355 Hamburg",
    "gewerk": "Heizung, Lüftung, Sanitär (HLS) / Raumlufttechnik",
    "empfaenger": ["apoprojekt GmbH", "Niederlassung Berlin", "Kurfürstendamm 195", "10707 Berlin"],
    "ansprechpartner": "Herrn Pascal Jansen",
    "ansprechpartner_zusatz": "Projektleitung • +49 151 53836502",
    "datum": date.today().strftime("%d.%m.%Y"),
}

ap = argparse.ArgumentParser()
ap.add_argument("--projekt", help="JSON-Datei, die einzelne Felder aus PROJEKT überschreibt")
ap.add_argument("--out", default=str(REPO / "out" / "baustellen-unterlagen"))
args = ap.parse_args()
if args.projekt:
    PROJEKT.update(json.loads(pathlib.Path(args.projekt).read_text(encoding="utf-8")))

OUT = pathlib.Path(args.out)
OUT.mkdir(parents=True, exist_ok=True)
LOGO = REPO / "vorlagen" / "leans-logo.png"
logo_b64 = base64.b64encode(LOGO.read_bytes()).decode()
DATUM = PROJEKT["datum"]

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:Arial,Helvetica,sans-serif;font-size:11.5px;color:#1a1a1a;padding:34px 40px;line-height:1.55}
.hdr{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:22px;padding-bottom:12px;border-bottom:3px solid #1a5276}
.logoimg{height:64px;width:auto;display:block;margin-bottom:5px}
.sub{font-size:9.5px;color:#666;line-height:1.7}
.an{text-align:right;font-size:10.5px;line-height:1.6}
h1{font-size:17px;font-weight:bold;color:#1a5276;margin:14px 0 10px;letter-spacing:1.2px}
h2{font-size:12.5px;color:#1a5276;margin:16px 0 6px}
.meta{display:grid;grid-template-columns:170px 1fr;gap:3px 14px;margin:10px 0 14px;font-size:11px;
      background:#eaf1f8;padding:10px 12px;border-left:4px solid #1a5276}
.ml{font-weight:bold;color:#34495e}
p{margin:7px 0}
ul,ol{margin:6px 0 6px 20px}
li{margin:3px 0}
table{width:100%;border-collapse:collapse;margin:10px 0;font-size:10.5px}
th{background:#1a5276;color:#fff;padding:6px 6px;text-align:left;font-weight:bold}
td{padding:5px 6px;border:1px solid #dde;vertical-align:top}
tr.sec td{background:#eaf1f8;font-weight:bold;color:#1a5276}
.ok{color:#1e7b34;font-weight:bold}
.warn{color:#b8860b;font-weight:bold}
.miss{color:#a93226;font-weight:bold}
.line{border-bottom:1px solid #999;display:inline-block;min-width:230px}
.sign{margin-top:34px;display:flex;gap:60px}
.sign div{flex:1;border-top:1px solid #333;padding-top:5px;font-size:10px;color:#444}
.hint{margin-top:14px;font-size:9.5px;color:#777;font-style:italic;border-top:1px solid #eee;padding-top:8px}
.ftr{margin-top:26px;padding-top:6px;border-top:1px solid #ccc;
     font-size:8.5px;color:#999;text-align:center;line-height:1.7}
table{page-break-inside:auto}
tr{page-break-inside:avoid}
h1,h2{page-break-after:avoid}
.small{font-size:9.5px;color:#666}
"""

FTR = ("LEANS Tech GmbH &bull; Berlepschstr. 165, 14165 Berlin &bull; Geschäftsführer: Semir Redžić &bull; "
       "HRB 249080 B &bull; USt-IdNr. DE357948720 &bull; Tel. +49 170 828 0836 &bull; "
       "info@leanstech-gmbh.de &bull; www.leanstech-gmbh.de")

EMPF = ("<strong>An:</strong><br>" + "<br>".join(PROJEKT["empfaenger"]) +
        "<br><br>z. Hd. " + PROJEKT["ansprechpartner"] + "<br>"
        "<span class='small'>" + PROJEKT["ansprechpartner_zusatz"] + "</span>")

BV_META = f"""
<div class="meta">
  <span class="ml">Bauvorhaben:</span><span>{PROJEKT["bv"]}</span>
  <span class="ml">Auftrag-Nr.:</span><span>{PROJEKT["auftrag_nr"]}</span>
  <span class="ml">Auftraggeber:</span><span>{PROJEKT["auftraggeber"]}</span>
  <span class="ml">Auftragnehmer:</span><span>LEANS Tech GmbH, Berlepschstr. 165, 14165 Berlin</span>
  <span class="ml">Gewerk:</span><span>{PROJEKT["gewerk"]}</span>
  <span class="ml">Datum:</span><span>{DATUM}</span>
</div>"""


def page(title, body, empf=EMPF):
    return f"""<!DOCTYPE html><html lang="de"><head><meta charset="UTF-8"><title>{title}</title>
<style>{CSS}</style></head><body>
<div class="hdr">
  <div>
    <img src="data:image/png;base64,{logo_b64}" class="logoimg" alt="LEANS Tech GmbH">
    <div class="sub">LEANS Tech GmbH &bull; Semir Redžić &bull; Berlepschstr. 165 &bull; 14165 Berlin<br>
    Tel. +49 170 828 0836 &bull; info@leanstech-gmbh.de</div>
  </div>
  <div class="an">{empf}</div>
</div>
{body}
<div class="ftr">{FTR}</div>
</body></html>"""


SIGN = ('<div class="sign"><div>Ort, Datum: Berlin, ' + DATUM +
        '</div><div>Semir Redžić &ndash; Geschäftsführer, LEANS Tech GmbH</div></div>')

DOCS = {}

# ---------------------------------------------------------------- 00 Anschreiben + Checkliste
DOCS["00_Anschreiben_und_Checkliste_Baustellenunterlagen_BV17899"] = page(
    "Anschreiben Baustellenunterlagen BV 17899", f"""
<h1>BAUSTELLENUNTERLAGEN &ndash; ÜBERGABE UND NACHWEIS-CHECKLISTE</h1>
{BV_META}
<p>Sehr geehrter Herr Jansen,</p>
<p>anbei übersenden wir Ihnen die für das oben genannte Bauvorhaben angeforderten Unterlagen unserer Firma.
Die nachstehende Übersicht zeigt den Stand aller üblicherweise geforderten Nachweise, die beigefügten
Eigenerklärungen sowie die Bescheinigungen, die wir kurzfristig nachreichen.</p>

<table>
  <thead><tr><th style="width:34px">Nr.</th><th>Unterlage</th><th style="width:112px">Status</th><th style="width:210px">Bemerkung</th></tr></thead>
  <tbody>
    <tr class="sec"><td colspan="4">A &ndash; Firmen- und Steuernachweise</td></tr>
    <tr><td>1</td><td>Gewerbeanmeldung</td><td class="ok">liegt vor</td><td>unverändert seit Gründung 11.10.2022</td></tr>
    <tr><td>2</td><td>Handelsregisterauszug HRB 249080 B</td><td class="warn">wird nachgereicht</td><td>aktueller Auszug wird abgerufen (Nachweis halbjährlich)</td></tr>
    <tr><td>3</td><td>Handwerkskarte (HWK Berlin)</td><td class="ok">liegt vor</td><td>&ndash;</td></tr>
    <tr><td>4</td><td>Freistellungsbescheinigung § 48b EStG</td><td class="miss">Verlängerung läuft</td><td>letzte Bescheinigung gültig bis 02.07.2026; Neuantrag beim FA für Körperschaften III, StNr. 29/414/31448, ist gestellt</td></tr>
    <tr><td>5</td><td>Bescheinigung in Steuersachen (Finanzamt)</td><td class="warn">wird nachgereicht</td><td>Neuanforderung beim Finanzamt</td></tr>
    <tr><td>6</td><td>USt-IdNr. DE357948720</td><td class="ok">liegt vor</td><td>&ndash;</td></tr>
    <tr class="sec"><td colspan="4">B &ndash; Versicherung und Sozialkassen</td></tr>
    <tr><td>7</td><td>Betriebshaftpflicht &ndash; NÜRNBERGER Allgemeine Versicherungs-AG, Schein-Nr. 223000795052<br>
        <span class="small">Personen-, Sach- und Vermögensschäden pauschal 5 Mio. EUR je Versicherungsfall / 10 Mio. EUR je Versicherungsjahr</span></td>
        <td class="ok">liegt vor</td><td>Bestätigung vom 08.09.2025, Beiträge laufend gezahlt</td></tr>
    <tr><td>8</td><td>Unbedenklichkeitsbescheinigung Berufsgenossenschaft (BG BAU)</td><td class="warn">wird nachgereicht</td><td>Anforderung über das BG-BAU-Portal</td></tr>
    <tr><td>9</td><td>Unbedenklichkeits-/Negativbescheinigung SOKA-BAU (Urlaubskasse)</td><td class="warn">wird nachgereicht</td><td>Gültigkeit max. 3 Monate</td></tr>
    <tr><td>10</td><td>Unbedenklichkeitsbescheinigung der Krankenkassen</td><td class="warn">wird nachgereicht</td><td>Gültigkeit max. 3 Monate</td></tr>
    <tr class="sec"><td colspan="4">C &ndash; Erklärungen (diesem Schreiben beigefügt)</td></tr>
    <tr><td>11</td><td>Eigenerklärung Mindestlohngesetz (§ 19 Abs. 3 MiLoG)</td><td class="ok">beigefügt</td><td>Anlage 1</td></tr>
    <tr><td>12</td><td>Erklärung Sozialversicherung / Mindestlohn und baustellenbezogene Mitarbeiterliste</td><td class="ok">beigefügt</td><td>Anlage 2 &ndash; Personalzeilen vor Einsatzbeginn ergänzt</td></tr>
    <tr><td>13</td><td>Nachunternehmererklärung</td><td class="ok">beigefügt</td><td>Anlage 3</td></tr>
    <tr><td>14</td><td>Benennung deutschsprachiger Ansprechpartner / Bauleiter</td><td class="ok">beigefügt</td><td>Anlage 4 &ndash; gem. Vertragsbedingungen Ziff. 1 b)</td></tr>
    <tr><td>15</td><td>Fachunternehmererklärung</td><td class="ok">beigefügt</td><td>Anlage 5 &ndash; zur Vorlage bei Fertigstellung</td></tr>
    <tr><td>16</td><td>Fachbauleitererklärung</td><td class="ok">beigefügt</td><td>Anlage 6</td></tr>
    <tr><td>17</td><td>Gefährdungsbeurteilung und Sicherheitsunterweisung</td><td class="ok">beigefügt</td><td>Anlage 7 &ndash; inkl. Unterweisungsnachweis</td></tr>
    <tr><td>18</td><td>Bautagebuch (förmliche Führung gem. Vertragsbedingungen Ziff. 1 c)</td><td class="ok">beigefügt</td><td>Anlage 8 &ndash; Vordruck, wird täglich geführt</td></tr>
    <tr class="sec"><td colspan="4">D &ndash; Baustellenorganisation</td></tr>
    <tr><td>19</td><td>Mitführung der Personaldokumente auf der Baustelle (SchwarzArbG)</td><td class="ok">zugesichert</td><td>siehe Anlage 2</td></tr>
    <tr><td>20</td><td>Teilnahme am Lean-/LPS-Verfahren und an Baubesprechungen</td><td class="ok">zugesichert</td><td>Ansprechpartner siehe Anlage 4</td></tr>
  </tbody>
</table>

<p>Die als „wird nachgereicht&ldquo; gekennzeichneten Bescheinigungen werden bei den jeweiligen Stellen angefordert
und Ihnen unaufgefordert übersandt, sobald sie vorliegen. Für Rückfragen stehen wir Ihnen jederzeit zur Verfügung.</p>
<p>Mit freundlichen Grüßen</p>
{SIGN}
""")

# ---------------------------------------------------------------- 01 MiLoG
DOCS["01_Eigenerklaerung_Mindestlohngesetz_BV17899"] = page(
    "Eigenerklärung MiLoG", f"""
<h1>EIGENERKLÄRUNG NACH § 19 ABS. 3 MINDESTLOHNGESETZ (MiLoG)</h1>
{BV_META}
<p>Nach § 19 Abs. 3 MiLoG fordern Auftraggeber beim Gewerbezentralregister Auskünfte über rechtskräftige
Bußgeldentscheidungen wegen einer Ordnungswidrigkeit nach § 21 Abs. 1 oder Abs. 2 MiLoG an oder verlangen
vom Auftragnehmer eine Erklärung, dass die Voraussetzungen für einen Ausschluss nach § 19 Abs. 1 MiLoG
nicht vorliegen.</p>

<h2>Erklärung</h2>
<p>Hiermit erklären wir, die LEANS Tech GmbH, Berlepschstr. 165, 14165 Berlin, verbindlich:</p>
<ol>
  <li>Die Voraussetzungen für einen Ausschluss nach § 19 Abs. 1 MiLoG liegen nicht vor. Unser Unternehmen
      ist nicht wegen eines Verstoßes nach § 21 MiLoG mit einer Geldbuße von wenigstens 2.500 EUR belegt worden.</li>
  <li>Allen auf der oben genannten Baustelle eingesetzten Arbeitnehmerinnen und Arbeitnehmern wird
      mindestens der jeweils geltende gesetzliche Mindestlohn nach dem MiLoG bzw. der einschlägige
      Branchenmindestlohn nach dem Arbeitnehmer-Entsendegesetz (AEntG) gezahlt.</li>
  <li>Die Melde-, Aufzeichnungs- und Dokumentationspflichten nach §§ 16, 17 MiLoG werden eingehalten;
      die Arbeitszeitaufzeichnungen werden auf Verlangen der Behörden und des Auftraggebers vorgelegt.</li>
  <li>Sozialversicherungsbeiträge werden ordnungsgemäß abgeführt. Es besteht kein Beitragsrückstand.</li>
  <li>Etwaige von uns eingesetzte Nachunternehmer werden vertraglich zur Einhaltung derselben
      Verpflichtungen verpflichtet; ihr Einsatz erfolgt nur nach vorheriger schriftlicher Zustimmung
      des Auftraggebers (siehe gesonderte Nachunternehmererklärung).</li>
</ol>
<p>Wir haben zur Kenntnis genommen, dass der Auftraggeber jederzeit zusätzlich Auskünfte des
Gewerbezentralregisters nach § 150a Gewerbeordnung anfordern kann.</p>
{SIGN}
""")

# ---------------------------------------------------------------- 02 Mitarbeiterliste
zeilen = "".join(
    f"<tr><td>{i}</td><td></td><td></td><td></td><td></td><td></td><td></td></tr>" for i in range(2, 11))
DOCS["02_Erklaerung_Sozialversicherung_und_Mitarbeiterliste_BV17899"] = page(
    "Mitarbeiterliste und Sozialversicherungserklärung", f"""
<h1>BAUSTELLENBEZOGENE MITARBEITERLISTE UND ERKLÄRUNG ZUR SOZIALVERSICHERUNG</h1>
{BV_META}
<h2>1. Erklärung des Auftragnehmers</h2>
<p>Wir erklären, dass die nachfolgend aufgeführten Personen bei der LEANS Tech GmbH ordnungsgemäß angemeldet
und sozialversichert sind bzw. als Geschäftsführer tätig sind, dass für sie der gesetzliche Mindestlohn
gezahlt wird und dass sie ihre Personaldokumente (Personalausweis/Pass, ggf. Aufenthalts- und
Arbeitserlaubnis, Sozialversicherungsausweis) gemäß § 2a Schwarzarbeitsbekämpfungsgesetz auf der Baustelle
mitführen und auf Verlangen vorzeigen.</p>
<p>Änderungen des Personalbestands auf dieser Baustelle werden der Bauleitung unaufgefordert und vor
Einsatzbeginn schriftlich mitgeteilt.</p>

<h2>2. Auf der Baustelle eingesetzte Personen</h2>
<table>
  <thead><tr>
    <th style="width:30px">Nr.</th><th>Name, Vorname</th><th style="width:78px">geb. am</th>
    <th style="width:104px">Funktion</th><th style="width:96px">Staatsang.</th>
    <th style="width:92px">Ausweis-Nr.</th><th style="width:80px">Einsatz ab</th>
  </tr></thead>
  <tbody>
    <tr><td>1</td><td>Redžić, Semir</td><td>25.02.1987</td><td>Geschäftsführer / Bauleiter</td><td></td><td></td><td></td></tr>
    {zeilen}
  </tbody>
</table>
<p class="small">Die Zeilen 2 ff. werden vor Einsatzbeginn ausgefüllt und der Bauleitung übergeben.
Für jede eingesetzte Person wird auf Verlangen eine Kopie des Personaldokuments sowie die
Mindestlohnbescheinigung vorgelegt.</p>

<h2>3. Sozialkassen und Versicherungen</h2>
<table>
  <thead><tr><th>Stelle</th><th style="width:250px">Nummer / Nachweis</th></tr></thead>
  <tbody>
    <tr><td>Berufsgenossenschaft BG BAU &ndash; Mitgliedsnummer</td><td><span class="line">&nbsp;</span></td></tr>
    <tr><td>SOKA-BAU &ndash; Betriebsnummer</td><td><span class="line">&nbsp;</span></td></tr>
    <tr><td>Krankenkasse(n) der Beschäftigten</td><td><span class="line">&nbsp;</span></td></tr>
    <tr><td>Betriebshaftpflicht &ndash; NÜRNBERGER Allgemeine Versicherungs-AG</td><td>Versicherungsschein-Nr. 223000795052</td></tr>
  </tbody>
</table>
{SIGN}
""")

# ---------------------------------------------------------------- 03 Nachunternehmer
DOCS["03_Nachunternehmererklaerung_BV17899"] = page(
    "Nachunternehmererklärung", f"""
<h1>NACHUNTERNEHMERERKLÄRUNG</h1>
{BV_META}
<p>Zum oben genannten Bauvorhaben erklären wir als Auftragnehmer Folgendes:</p>
<table>
  <thead><tr><th style="width:34px">&nbsp;</th><th>Erklärung</th></tr></thead>
  <tbody>
    <tr><td style="text-align:center">☐</td><td>Die beauftragten Leistungen werden <strong>ausschließlich mit eigenem Personal</strong>
        der LEANS Tech GmbH ausgeführt. Nachunternehmer werden nicht eingesetzt.</td></tr>
    <tr><td style="text-align:center">☐</td><td>Es werden die nachfolgend aufgeführten <strong>Nachunternehmer</strong> eingesetzt.
        Der Einsatz erfolgt erst nach schriftlicher Zustimmung des Auftraggebers.</td></tr>
  </tbody>
</table>

<h2>Angaben zu eingesetzten Nachunternehmern</h2>
<table>
  <thead><tr>
    <th style="width:30px">Nr.</th><th>Firma, Anschrift</th><th style="width:150px">Leistungsumfang</th>
    <th style="width:104px">Zeitraum</th><th style="width:110px">Ansprechpartner</th>
  </tr></thead>
  <tbody>
    <tr><td>1</td><td></td><td></td><td></td><td></td></tr>
    <tr><td>2</td><td></td><td></td><td></td><td></td></tr>
    <tr><td>3</td><td></td><td></td><td></td><td></td></tr>
  </tbody>
</table>

<h2>Verpflichtungen</h2>
<ul>
  <li>Für jeden eingesetzten Nachunternehmer werden sämtliche vom Auftraggeber geforderten Nachweise
      (Gewerbeanmeldung, Freistellungsbescheinigung § 48b EStG, Unbedenklichkeitsbescheinigungen von
      Finanzamt, Berufsgenossenschaft, SOKA-BAU und Krankenkassen, Betriebshaftpflicht,
      MiLoG-Eigenerklärung, Mitarbeiterliste) <strong>vor Arbeitsaufnahme</strong> vorgelegt.</li>
  <li>Der Nachunternehmer wird vertraglich zur Einhaltung des Mindestlohngesetzes, des
      Arbeitnehmer-Entsendegesetzes und des Schwarzarbeitsbekämpfungsgesetzes verpflichtet.</li>
  <li>Eine Weitervergabe an weitere Nachunternehmer (Kettenvergabe) erfolgt nicht ohne gesonderte
      schriftliche Zustimmung des Auftraggebers.</li>
  <li>Ein Wechsel oder eine Ergänzung der eingesetzten Nachunternehmer wird unverzüglich schriftlich angezeigt.</li>
</ul>
{SIGN}
""")

# ---------------------------------------------------------------- 04 Ansprechpartner
DOCS["04_Benennung_Ansprechpartner_und_Bauleiter_BV17899"] = page(
    "Benennung Ansprechpartner und Bauleiter", f"""
<h1>BENENNUNG DES DEUTSCHSPRACHIGEN ANSPRECHPARTNERS UND BAULEITERS</h1>
{BV_META}
<p>Gemäß den Vertragsbedingungen des Auftraggebers (Ziff. 1 b: jederzeitige Verfügbarkeit eines
deutschsprachigen Vertreters auf der Baustelle) benennen wir für das oben genannte Bauvorhaben:</p>

<h2>1. Verantwortlicher Bauleiter / Ansprechpartner vor Ort</h2>
<table>
  <tbody>
    <tr><td style="width:190px"><strong>Name</strong></td><td>Herr Semir Redžić</td></tr>
    <tr><td><strong>Funktion</strong></td><td>Geschäftsführer, verantwortlicher Fachbauleiter für das gesamte Bauvorhaben</td></tr>
    <tr><td><strong>Firma</strong></td><td>LEANS Tech GmbH, Berlepschstr. 165, 14165 Berlin</td></tr>
    <tr><td><strong>Telefon</strong></td><td>+49 170 828 0836</td></tr>
    <tr><td><strong>E-Mail</strong></td><td>info@leanstech-gmbh.de</td></tr>
    <tr><td><strong>Sprache</strong></td><td>deutsch (verhandlungssicher)</td></tr>
  </tbody>
</table>

<h2>2. Stellvertretung</h2>
<table>
  <tbody>
    <tr><td style="width:190px"><strong>Name</strong></td><td><span class="line">&nbsp;</span></td></tr>
    <tr><td><strong>Funktion</strong></td><td><span class="line">&nbsp;</span></td></tr>
    <tr><td><strong>Telefon / E-Mail</strong></td><td><span class="line">&nbsp;</span></td></tr>
  </tbody>
</table>

<h2>3. Zusicherungen</h2>
<ul>
  <li>Während der gesamten Ausführungszeit steht auf der Baustelle mindestens ein deutschsprachiger
      Vertreter unseres Unternehmens als Ansprechpartner für die Projektleitung zur Verfügung.</li>
  <li>Der benannte Bauleiter ist bevollmächtigt, alle für die Vertragsabwicklung erforderlichen Erklärungen
      für und gegen den Auftragnehmer abzugeben und entgegenzunehmen.</li>
  <li>An den Baubesprechungen / Jour fixe sowie an den Lean-Besprechungen nach dem Last Planner System
      nehmen wir vorbereitet teil.</li>
  <li>Ein Wechsel der benannten Person wird dem Auftraggeber rechtzeitig schriftlich mitgeteilt.</li>
</ul>
{SIGN}
""")

# ---------------------------------------------------------------- 05 Fachunternehmererklärung
DOCS["05_Fachunternehmererklaerung_BV17899"] = page(
    "Fachunternehmererklärung", f"""
<h1>FACHUNTERNEHMERERKLÄRUNG | HEIZUNG, LÜFTUNG, SANITÄR</h1>
{BV_META}
<p>Als ausführendes Fachunternehmen erklären wir für den oben genannten Auftrag:</p>
<ul>
  <li>Die im Auftrag enthaltenen Leistungen wurden nach den anerkannten Regeln der Technik ausgeführt.</li>
  <li>Der Auftrag wurde nach den geltenden Vorschriften, Normen und Verordnungen durchgeführt,
      insbesondere nach den einschlägigen DIN-Normen, den VDI-Richtlinien (u. a. VDI 6022 Hygiene in
      raumlufttechnischen Anlagen, VDI 2052 Küchenlüftung), der DIN 1988 / DIN EN 806 (Trinkwasser)
      sowie den Vorgaben der VOB/B und VOB/C.</li>
  <li>Die verarbeiteten Materialien, Baustoffe und Produkte sind von einer Materialprüfanstalt, einem
      Überwachungsinstitut, dem TÜV oder einer vergleichbaren Stelle zugelassen; die erforderlichen
      Verwendbarkeitsnachweise liegen vor.</li>
  <li>Die Herstellerangaben und Einbauvorschriften wurden bei der Verarbeitung eingehalten.</li>
  <li>Die Anlagen wurden funktionsgeprüft, gespült bzw. eingeregelt; Mess- und Einregulierungsprotokolle
      sowie die Revisionsunterlagen werden mit der Abnahme übergeben.</li>
  <li>Brandschutztechnische Bauteile (u. a. Brandschutzklappen, Schottungen) wurden entsprechend ihrer
      Zulassung eingebaut und dokumentiert.</li>
</ul>
<p class="small">Diese Erklärung wird mit Fertigstellung des Gewerks bzw. zur Abnahme vorgelegt und bezieht
sich auf den vorstehend genannten Leistungsumfang.</p>
{SIGN}
""")

# ---------------------------------------------------------------- 06 Fachbauleitererklärung
DOCS["06_Fachbauleitererklaerung_BV17899"] = page(
    "Fachbauleitererklärung", f"""
<h1>FACHBAULEITERERKLÄRUNG</h1>
{BV_META}
<p>Der Auftragnehmer (AN) benennt seinen verantwortlichen, deutschsprachigen Fachbauleiter im Sinne der
gültigen und anwendbaren Landesbauordnung (Bauordnung für Berlin &ndash; BauO Bln):</p>
<table>
  <tbody>
    <tr><td style="width:190px"><strong>Firma</strong></td><td>LEANS Tech GmbH | Berlepschstr. 165 | 14165 Berlin</td></tr>
    <tr><td><strong>Fachbauleiter</strong></td><td>Herr Semir Redžić (für das gesamte Bauvorhaben)</td></tr>
    <tr><td><strong>Leistungsbereich</strong></td><td>Heizung, Lüftung, Sanitär / Raumlufttechnik</td></tr>
    <tr><td><strong>Erreichbarkeit</strong></td><td>+49 170 828 0836 &bull; info@leanstech-gmbh.de</td></tr>
  </tbody>
</table>
<p>Ein etwaiger Wechsel der Person des Fachbauleiters wird durch den AN rechtzeitig schriftlich mitgeteilt.
Der Fachbauleiter erklärt mit seiner Unterschrift, dass ihm die einschlägigen Bestimmungen der gültigen
Landesbauordnung bekannt sind und er die Aufgaben des Fachbauleiters für die Ausführung des oben genannten
Bauvorhabens bzw. Gewerks im Sinne der gültigen Landesbauordnung übernimmt. Er ist ermächtigt, alle für die
Vertragsabwicklung erforderlichen Erklärungen für und gegen den Auftragnehmer abzugeben und
entgegenzunehmen. Darüber hinaus verfügt er über die für sein Fachgebiet erforderliche Sachkunde und
Erfahrung. Im Rahmen seines Wirkungskreises ist er unmittelbar und allein verantwortlich im
ordnungsrechtlichen Sinne.</p>
<p class="small">Diese Erklärung entspricht keiner Bestellung als Bauleiter nach Landesbauordnung.</p>
{SIGN}
""")

# ---------------------------------------------------------------- 07 Gefährdungsbeurteilung
unterw = "".join(f"<tr><td>{i}</td><td></td><td></td><td></td></tr>" for i in range(1, 9))
DOCS["07_Gefaehrdungsbeurteilung_und_Sicherheitsunterweisung_BV17899"] = page(
    "Gefährdungsbeurteilung und Sicherheitsunterweisung", f"""
<h1>GEFÄHRDUNGSBEURTEILUNG UND SICHERHEITSUNTERWEISUNG</h1>
{BV_META}
<p>Gefährdungsbeurteilung nach § 5 Arbeitsschutzgesetz (ArbSchG) und § 3 Betriebssicherheitsverordnung
für die Montagearbeiten HLS / Raumlufttechnik auf der oben genannten Baustelle.</p>

<h2>1. Gefährdungen und Schutzmaßnahmen</h2>
<table>
  <thead><tr><th style="width:150px">Tätigkeit</th><th style="width:180px">Gefährdung</th><th>Schutzmaßnahme</th></tr></thead>
  <tbody>
    <tr><td>Allgemeiner Baustellenaufenthalt</td><td>Stolpern, Rutschen, Stürzen; herabfallende Teile</td>
        <td>Sicherheitsschuhe S3, Schutzhelm, Warnweste; Ordnung am Arbeitsplatz; Verkehrswege freihalten</td></tr>
    <tr><td>Montage von Kanälen, Rohrleitungen und Hauben über Kopf</td><td>Absturz, herabfallende Lasten, Quetschungen</td>
        <td>Standsichere Arbeitsbühne / Gerüst, kein Leiternersatz; Absperren des Bereichs unterhalb; Schutzhandschuhe</td></tr>
    <tr><td>Einbringen und Montage der Küchen-Dunstabzugshaube (ca. 197 kg)</td><td>Herabfallen der Last, Quetschgefahr, Rückenbelastung</td>
        <td>Hebehilfen/Traversen, geprüfte Anschlagmittel, mindestens 2 Personen, bauseitige Befestigungspunkte vorab prüfen, Transportweg freimachen</td></tr>
    <tr><td>Trennen, Bohren, Schleifen</td><td>Lärm, Funkenflug, Späne, Staub</td>
        <td>Gehörschutz, Schutzbrille, Staubschutzmaske FFP2, Funkenflug abschirmen, Brandwache bei Heißarbeiten</td></tr>
    <tr><td>Löt- und Schweißarbeiten / Heißarbeiten</td><td>Brandgefahr, Verbrennungen</td>
        <td>Erlaubnisschein für Heißarbeiten, Feuerlöscher vor Ort, Nachkontrolle, brennbares Material entfernen</td></tr>
    <tr><td>Elektrische Betriebsmittel</td><td>Elektrischer Schlag</td>
        <td>Nur geprüfte Geräte (DGUV V3), Baustromverteiler mit FI, Sichtprüfung vor Gebrauch</td></tr>
    <tr><td>Arbeiten an Trinkwasserleitungen</td><td>Hygienerisiko / Verkeimung</td>
        <td>Arbeiten nach DIN 1988 / DIN EN 806, Spülen und Dokumentation, hygienisches Arbeiten mit sauberem Werkzeug</td></tr>
    <tr><td>Arbeiten in fremden Gewerken / Publikumsbereich</td><td>Gefährdung Dritter</td>
        <td>Abstimmung mit Bauleitung, Absperrung, Beschilderung, Baustellenordnung des Auftraggebers einhalten</td></tr>
  </tbody>
</table>

<h2>2. Persönliche Schutzausrüstung (PSA)</h2>
<p>Sicherheitsschuhe S3, Schutzhelm, Warnweste, Schutzhandschuhe, Schutzbrille; tätigkeitsbezogen
zusätzlich Gehörschutz, Atemschutz FFP2 und Schweißerschutz. Die PSA wird vom Arbeitgeber gestellt.</p>

<h2>3. Notfallorganisation</h2>
<table>
  <tbody>
    <tr><td style="width:190px"><strong>Notruf</strong></td><td>112 (Feuerwehr / Rettungsdienst) &bull; 110 (Polizei)</td></tr>
    <tr><td><strong>Ersthelfer / Verbandkasten</strong></td><td>Verbandkasten im Baustellencontainer bzw. im Firmenfahrzeug</td></tr>
    <tr><td><strong>Unfallversicherung</strong></td><td>BG BAU &ndash; Berufsgenossenschaft der Bauwirtschaft</td></tr>
    <tr><td><strong>Verantwortlicher vor Ort</strong></td><td>Semir Redžić, +49 170 828 0836</td></tr>
  </tbody>
</table>

<h2>4. Unterweisungsnachweis</h2>
<p class="small">Die nachstehend genannten Personen wurden vor Aufnahme der Tätigkeit über die
Gefährdungen und Schutzmaßnahmen sowie über die Baustellenordnung des Auftraggebers unterwiesen.</p>
<table>
  <thead><tr><th style="width:30px">Nr.</th><th>Name, Vorname</th><th style="width:100px">Datum</th><th style="width:200px">Unterschrift</th></tr></thead>
  <tbody>{unterw}</tbody>
</table>
{SIGN}
""")

# ---------------------------------------------------------------- 08 Bautagebuch
tage = "".join(f"<tr><td style='height:26px'></td><td></td><td></td><td></td><td></td><td></td></tr>" for _ in range(12))
DOCS["08_Bautagebuch_Vordruck_BV17899"] = page(
    "Bautagebuch", f"""
<h1>BAUTAGEBUCH</h1>
{BV_META}
<p class="small">Förmliches Bautagebuch gemäß Vertragsbedingungen des Auftraggebers (Ziff. 1 c).
Wird arbeitstäglich geführt und der Bauleitung auf Nachfrage vorgelegt.</p>
<table>
  <thead><tr>
    <th style="width:70px">Datum</th><th style="width:78px">Wetter / °C</th>
    <th style="width:56px">Pers.</th><th>Ausgeführte Leistungen / Bereich</th>
    <th style="width:180px">Besondere Vorkommnisse, Behinderungen, Anweisungen</th>
    <th style="width:96px">Material / Geräte</th>
  </tr></thead>
  <tbody>{tage}</tbody>
</table>
<h2>Hinweise zur Führung</h2>
<ul>
  <li>Behinderungen, fehlende Vorleistungen und Bedenken werden zusätzlich unverzüglich schriftlich
      gegenüber der Bauleitung angezeigt (§ 6 Abs. 1 VOB/B, § 4 Abs. 3 VOB/B).</li>
  <li>Stundenlohnarbeiten werden gesondert auf Stundenlohnzetteln erfasst und arbeitstäglich zur
      Gegenzeichnung vorgelegt.</li>
  <li>Anweisungen der Bauleitung werden mit Datum, Uhrzeit und Namen des Anweisenden vermerkt.</li>
</ul>
<div class="sign"><div>Bauleiter AN: Semir Redžić</div><div>Kenntnisnahme Bauleitung AG</div></div>
""")

# ---------------------------------------------------------------- 09 Antrag 48b
DOCS["09_Antrag_Freistellungsbescheinigung_48b_Finanzamt"] = page(
    "Antrag Freistellungsbescheinigung 48b",
    f"""
<h1>ANTRAG AUF ERTEILUNG EINER FREISTELLUNGSBESCHEINIGUNG NACH § 48b ESTG</h1>
<div class="meta">
  <span class="ml">Antragsteller:</span><span>LEANS Tech GmbH, Berlepschstr. 165, 14165 Berlin</span>
  <span class="ml">Steuernummer:</span><span>29/414/31448</span>
  <span class="ml">Aktenzeichen:</span><span>29/414/31448</span>
  <span class="ml">USt-IdNr.:</span><span>DE357948720</span>
  <span class="ml">Handelsregister:</span><span>HRB 249080 B, Amtsgericht Charlottenburg</span>
  <span class="ml">Datum:</span><span>{DATUM}</span>
</div>
<p>Sehr geehrte Damen und Herren,</p>
<p>hiermit beantragen wir die Erteilung einer neuen Freistellungsbescheinigung zum Steuerabzug bei
Bauleistungen gemäß § 48b Abs. 1 Satz 1 EStG.</p>
<p>Die zuletzt erteilte Bescheinigung (Sicherheitsnummer 58413844) war vom 03.07.2025 bis zum 02.07.2026
gültig. Wir erbringen weiterhin Bauleistungen im Sinne des § 48 Abs. 1 EStG in den Gewerken Heizung,
Lüftung, Sanitär und Kältetechnik und benötigen die Bescheinigung fortlaufend zur Vorlage bei unseren
Auftraggebern.</p>
<p>Unsere steuerlichen Pflichten kommen wir ordnungsgemäß nach; Steuererklärungen und Voranmeldungen
wurden fristgerecht abgegeben, Zahlungsrückstände bestehen nicht. Wir bitten um Erteilung einer
Bescheinigung für einen Zeitraum von drei Jahren, hilfsweise für den längstmöglichen Zeitraum.</p>
<p>Um Übersendung der Bescheinigung an die oben genannte Anschrift wird gebeten. Für Rückfragen stehen
wir Ihnen gern zur Verfügung.</p>
<p>Mit freundlichen Grüßen</p>
{SIGN}
<div class="hint">Hinweis für den internen Gebrauch: Ohne gültige Freistellungsbescheinigung nach § 48b EStG
ist der Auftraggeber verpflichtet, 15 % Bauabzugssteuer von jeder Zahlung einzubehalten und an das
Finanzamt abzuführen. Der Antrag sollte daher umgehend abgesendet werden &ndash; alternativ elektronisch
über ELSTER (Formular „Antrag auf Freistellungsbescheinigung zum Steuerabzug bei Bauleistungen&ldquo;).</div>
""",
    empf=("<strong>An:</strong><br>Finanzamt für Körperschaften III<br>Volkmarstraße 13<br>12099 Berlin<br>"
          "<br><span class='small'>Postfach 42 08 44, 12068 Berlin</span>"))

# ---------------------------------------------------------------- render
CHROME = next((str(p) for p in sorted(pathlib.Path("/opt/pw-browsers").glob("chromium-*/chrome-linux/chrome"))), None)
if not CHROME:
    sys.exit("Chromium nicht gefunden – PDF-Rendering nicht möglich.")
for name, html in DOCS.items():
    hp = OUT / f"{name}.html"
    hp.write_text(html, encoding="utf-8")
    pdf = OUT / f"{name}.pdf"
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-sandbox",
                    "--no-pdf-header-footer", f"--print-to-pdf={pdf}", f"file://{hp}"],
                   check=True, capture_output=True)
    print(f"{pdf.name}  {pdf.stat().st_size//1024} KB")
