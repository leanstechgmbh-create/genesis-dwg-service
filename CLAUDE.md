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
7. §13b-Satz mit Adyen-Konto, Fußblock mit Stammdaten

Regeln: Rechnungsnummer fortlaufend `<Jahr>-<n>` (Stand Juli 2026:
zuletzt 2026-40 = 2. AR SP Construct/Mehringdamm).
Dateiname: `<Datum> <Typ> <Nr> - LEANS Tech GmbH - <Betrag> EUR`.

### Freigabe-Workflow Rechnungen & Angebote (VERBINDLICH)

1. **Entwurf IMMER zuerst als Download in den Chat** senden (PDF),
   damit der Nutzer sieht, was Sache ist. Bei jeder Änderung erneut
   die aktualisierte Fassung als Download schicken.
2. **NICHTS ungefragt ins Google Drive hochladen.** Erst wenn der
   Nutzer die Rechnung freigibt („passt", „nutzen wir", „abschicken"),
   wird GENAU DIESE Fassung dauerhaft im Drive abgelegt (Projektordner,
   Namenskonvention, Zusatz „(VERSENDETE FASSUNG)").
3. **Keine Zwischenstände/Duplikate im Drive.** Pro Rechnung existiert
   dort nur die versendete Endfassung. Veraltete eigene Uploads dem
   Nutzer zum Löschen auflisten (KI hat keine Löschrechte im Drive).
4. Gilt genauso für Angebote und alle anderen Dokumente.

### E-Mail-Versand an Kunden (VERBINDLICH)

- Rechnungen/Angebote an Kunden gehen IMMER vom Postfach **sr@** (IONOS)
  raus — NIEMALS von leanstechgmbh@gmail.com, außer der Nutzer sagt es
  ausdrücklich. Der Nutzer hat dafür eine eigene Schnittstelle
  (IONOS + Gmail) in seinem n8n gebaut (semirredzic.app.n8n.cloud).
- Ist der n8n-Connector in der Sitzung NICHT verbunden: EINMAL kurz
  sagen, dass der Versand über sr@ gerade nicht möglich ist, und sofort
  den fertigen Mailtext (An/Betreff/Text) zum Kopieren liefern. Nicht
  wiederholt erklären oder diskutieren.
- Der Gmail-Connector (leanstechgmbh@gmail.com) kann KEINE Anhänge in
  Entwürfe legen (getestet 07/2026, Anhang wird stillschweigend
  verworfen) — nicht erneut versuchen. Entwürfe dort nur auf Wunsch.

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
