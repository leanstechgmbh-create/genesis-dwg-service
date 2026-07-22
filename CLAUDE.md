# CLAUDE.md

## Sprache / Language

**Immer auf Deutsch antworten.** Alle Antworten an den Nutzer ausschließlich
auf Deutsch verfassen — niemals auf Englisch, auch nicht teilweise. Das gilt
für getippte Eingaben genauso wie für Spracheingabe (Voice).

Ausnahme: Code, Befehle, Dateinamen, Logs und technische Bezeichner bleiben
unverändert (werden nicht übersetzt).

**Überschriften/Titel passend zum Inhalt.** Chat-Titel, Sitzungs-Titel und
Überschriften in Antworten immer auf Deutsch formulieren und so wählen, dass
sie das tatsächliche Thema des Inhalts wiedergeben — keine generischen oder
englischen Titel. Das gilt auch für den Slack-Bot: Jede Bot-Antwort beginnt
mit einer kurzen, fetten Überschrift zum Thema der Antwort.

## Projekt

`genesis-dwg-service` — Python/FastAPI-Backend, das DWG/DXF-Dateien entgegennimmt,
kleine Änderungen vornimmt (verschieben/ergänzen/löschen via LibreDWG) und wieder
als DWG ausgibt. Läuft als Google Cloud Run Service, angebunden an n8n (Formular-Upload)
und einen Slack-Bot.

- `main.py` — FastAPI-App, HTTP-Endpunkte (`/`, `/modify-dwg`)
- `dwg_core.py` — Kernlogik (DWG<->DXF-Konvertierung, Änderungen)
- `slack_bot.py` — Slack-Bot (Chat + Plan-Bearbeitung, Claude-gestützt)
- `START_HIER.md` — Deploy-Anleitung (Google Cloud Run)

## Firma / Kaufmännisches (LEANS Tech GmbH)

Der Nutzer ist die **LEANS Tech GmbH** (Semir Redžić), Berlepschstr. 165,
14165 Berlin — Gewerke: Klimatisierung / Kältetechnik, Heizung, Lüftung,
Sanitär. **Kein QuickBooks** — niemals QuickBooks vorschlagen oder dort
suchen. Ablage ist Google Drive („GBrain"): Projektordner (z. B.
„Mehringdamm 44-46"), Rechnungsordner („03 Rechnungen LEANS", „Rechnungen/
<Jahr>"), Register „Master <Jahr> Gesamt.xlsx" / „Master <Jahr> Ausgang.csv".

Stammdaten (für alle Dokumente):
- HR-Nr **HRB 249080 B** · USt-IdNr. **DE357948720**
- E-Mail info@leanstech-gmbh.de · Tel. +491708280836 · www.leanstech-gmbh.de
- **Zahlungskonto auf Rechnungen (IMMER dieses): Adyen Bank** ·
  IBAN **DE24 1001 9000 1000 0012 17** · BIC ADYBDEB2XXX ·
  Kontoinhaber „Leans Tech GmbH" (so auf 2026-39/2026-40 verwendet)
- Altes Konto Berliner Volksbank (DE21 1009 0000 2911 7280 04, BEVODEBB)
  steht nur auf älteren Rechnungen — NICHT mehr für neue Rechnungen verwenden,
  außer der Nutzer sagt es ausdrücklich
- Bauleistungen i. d. R. **§ 13b UStG** (Reverse Charge, 0 % USt):
  Pflichtsatz „Steuerschuldnerschaft des Leistungsempfängers (§ 13b UStG)."

### Rechnungsmuster (VERBINDLICH — „für immer fixiert")

Rechnungen IMMER nach `vorlagen/rechnung-muster.html` erstellen
(entspricht z. B. Rechnung „2. AR 2026-34" / „2026-8"). Aufbau:

1. Titel kurz: „1. AR" / „2. AR" / „SCHLUSSRECHNUNG" / „RECHNUNG"
2. Absenderblock LEANS Tech GmbH, dann Kundenblock
3. Metazeilen: Rechnungsnummer, Rechnungsdatum, Zahlungsbedingungen
   (Standard 7–10 Tage), Fälligkeitsdatum
4. BV-Zeile: BV, Auftrag/Angebot-Nr., Gewerk (ggf. Lieferzeitraum)
5. Tabelle: Beschreibung | Datum | Menge | Einheit | Einzelpreis |
   USt. % | Nettobetrag | Betrag — bei 2./3./x. AR wahlweise kumuliert
   (alle AR + Zwischensumme + „Abzüglich n. Abschlagsrechnung")
6. Summenblock: Nettobetrag / USt. 0,00 % / **Gesamtsumme**
7. §13b-Satz, Fußblock mit Stammdaten und Volksbank-Konto

Regeln: Rechnungsnummer fortlaufend `<Jahr>-<n>` (Stand Juli 2026:
zuletzt 2026-39 = 1. AR Klement/Mehringdamm; 2026-40 vergeben).
Dateiname: `<Datum> <Typ> <Nr> - LEANS Tech GmbH - <Betrag> EUR`.
Ablage: als Google Doc + PDF in den jeweiligen Projektordner im Drive.

### Angebotsmuster (VERBINDLICH)

Angebote IMMER nach der Regel von **Angebot 301** erstellen
(`vorlagen/angebot-muster.html`, Vorbild im Drive: „Angebot 301 LG
Mehringdamm ….html"): blauer Kopf (#1a5276) mit Logo/Firmenzeile und
„An:"-Block rechts, Titel ANGEBOT, Meta-Raster (Angebotsnummer/-datum,
Gültig bis, Projekt, Auftraggeber, Gewerk, Fabrikat, Leistung),
Positionstabelle Nr. | OZ | Beschreibung | Menge | Einh. | EP netto |
Betrag netto | MwSt mit Abschnitts- und Zwischensummenzeilen, blauer
Summenkasten (Nettobetrag / USt § 13b 0 % / Gesamtbetrag), kursiver
Hinweisblock, zentrierte Fußzeile mit Stammdaten.
