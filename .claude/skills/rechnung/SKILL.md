---
name: rechnung
description: Erstellt eine LEANS-Tech-Rechnung (AR/Schlussrechnung/Rechnung) im verbindlichen Firmen-Design. Nutzen, sobald der Nutzer eine Rechnung, Abschlagsrechnung (AR) oder Schlussrechnung erstellen will.
---

# Rechnung erstellen (LEANS Tech GmbH)

Verbindlicher Ablauf — KEINE Abweichungen vom Muster:

1. **Vorlage nutzen:** `vorlagen/rechnung-muster.html` (echtes Firmen-Design:
   Logo `vorlagen/leans-logo.png` oben mittig, grüner Titel #55a047, hellgrüne
   Tabellenkopfzeile #cbdcc6, grüne „Rechnungssumme"-Zeile, zentrierter
   §13b-Text, grüne Fußlinie). Visuelles Vorbild: Rechnung „2026-8" im Drive.
2. **Platzhalter füllen:** `{{RECHNUNGSNUMMER}}` (fortlaufend `<Jahr>-<n>`,
   Stand im Drive-Register „Master <Jahr>" prüfen; Juli 2026: zuletzt 2026-40),
   `{{RECHNUNGSDATUM}}`, `{{ZAHLUNGSBEDINGUNGEN}}` (Standard 7 Tage),
   `{{FAELLIGKEITSDATUM}}`, `{{KUNDE_*}}`, `{{BV_UND_AUFTRAG}}`, `{{GEWERK}}`,
   `{{LIEFERZEITRAUM}}`. Titel/H1 an Rechnungstyp anpassen
   („1. AR"/„2. ABSCHLAGSRECHNUNG"/„SCHLUSSRECHNUNG"/„RECHNUNG").
3. **Positionstabelle:** Bei 2./3./x. AR kumuliert wie Rechnung 2026-8:
   alle bisherigen AR als Zeilen, Zwischensumme (grüne Linien), dann
   „Abzüglich n. Abschlagsrechnung" negativ. USt. immer 0,00 % (§ 13b).
4. **Konto:** IMMER Adyen Bank, IBAN DE24 1001 9000 1000 0012 17,
   BIC ADYBDEB2XXX — NIEMALS Berliner Volksbank (nur historisch).
5. **PDF rendern:**
   `/opt/pw-browsers/chromium-*/chrome-linux/chrome --headless --no-sandbox
   --disable-gpu --no-pdf-header-footer --print-to-pdf=<datei> <html>`
   (Logo-PNG muss im selben Verzeichnis liegen wie das HTML).
6. **Selbst prüfen:** Das gerenderte PDF mit Read öffnen und VISUELL mit dem
   Muster vergleichen (Logo da? Grün? Tabelle richtig?), erst dann versenden.
7. **Benennen & ablegen:** `<JJJJ-MM-TT> <Typ> <Nr> - LEANS Tech GmbH -
   <Betrag> EUR.pdf`; PDF an Nutzer senden + in den Projektordner im
   Google Drive hochladen.
