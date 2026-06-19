# CLAUDE.md

## Angebote — Standardvorgabe (immer befolgen)

**Wenn der Nutzer ein „Angebot" wünscht (Wort „Angebot" / „angebot"), IMMER automatisch
im LEANS-Tech-Muster erstellen — NICHT nachfragen, einfach im Format der bestehenden
~100 Angebote (z. B. Angebot 282/283) ausgeben und abspeichern.**

### Ablauf
1. Angebot exakt im Muster (siehe unten) erstellen.
   **IMMER auch das vollständige Angebot direkt hier im Chat ausgeben** (kompletter
   Text im Muster-Layout), zusätzlich zu Doc + PDF.
2. Als **Google Doc** im Drive-Ordner `0AM9CvPIUCfZkUk9PVA` speichern
   (dort liegen die anderen Angebote, z. B. Angebot 282).
   - Doc-Titel: `ANGEBOT <Nr> - LEANS Tech GmbH - <Kurzbeschreibung> - <Summe> EUR`
3. Als **PDF** exportieren (`exportMimeType: application/pdf`) und dem Nutzer senden.
4. **Angebotsnummer** fortlaufend hochzählen. Zuletzt vergeben: **283** → nächste = 284.
5. Fehlende Felder (Kunde/Empfänger, Bauvorhaben) als Platzhalter `[…]` einsetzen,
   nicht extra nachfragen.

### Muster / Layout (nach Angebot 282)
```
LEANS Tech GmbH · Semir Redzic · Berlepschstr. 165 • 14165 • Berlin

[Kunde / Empfänger]
[Straße]
[PLZ Ort]

ANGEBOT
(optional: Projektkürzel, z. B. (MBK M40))

RAUMLUFTTECHNIK · HEIZUNG

Angebotsnummer: <Nr>
Angebotsdatum: <Datum>   Gültig bis: <Datum + 2 Monate>   Bauvorhaben: [Bauvorhaben]

<kurze Beschreibung des Leistungsumfangs>

Tabelle: Nr. | Beschreibung | Menge | Einheit | Einzelpreis | Betrag
  - Positions-Nummerierung wie 1.1.1, 1.2.1, … (oder 1.1, 1.2, 1.3)
  - Einheiten: Stk, psch, m, lfm, h …

Zwischensumme  <netto>
Nettobetrag    <netto>
Gesamt (netto) <netto>

Die Umsatzsteuer für diese Leistung schuldet nach § 13b UStG der Leistungsempfänger
(Reverse-Charge-Verfahren für Bauleistungen).

Zahlungsbedingungen: 14 Tage netto. Es gelten unsere allgemeinen Geschäftsbedingungen.
Wir freuen uns auf Ihre Beauftragung.

Adresse:          Berlepschstr. 165 14165 Berlin
Kontakt:          info@leanstech-gmbh.de  Tel. +49 170 8280836  www.leanstech-gmbh.de
Register / Bank:  HR-Nr HRB 249080 B · USt-IdNr. DE357948720
                  Berliner Volksbank · BIC BEVODEBB · IBAN DE21 1009 0000 2911 7280 04
```

### Regeln
- Standardmäßig **Reverse-Charge nach § 13b UStG** (Bauleistung, B2B) — keine 19 % MwSt
  ausweisen, außer der Nutzer sagt ausdrücklich etwas anderes (z. B. Endkunde/Privat).
- Gültigkeit: 2 Monate ab Angebotsdatum.
- Zahlungsbedingungen: 14 Tage netto.
- Sprache: Deutsch.
- „ohne Geräte" = nur Leistung/Arbeit (Geräte bauseits gestellt).

## Repo
GENESIS DWG-Service (FastAPI, `main.py`): DWG/DXF rein → kleine Änderungen → DWG/DXF raus.
