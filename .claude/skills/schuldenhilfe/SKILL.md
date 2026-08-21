---
name: schuldenhilfe
description: Hilfe bei Kontopfändung, Kontosperre, Bankmahnung, Kündigung der Kreditlinie, Ratenzahlung und P-Konto — für Mitarbeiter der LEANS Tech GmbH oder den Nutzer selbst. Nutzen, sobald es um gesperrte Konten, Pfändung, Schulden bei einer Bank oder ein Mahnschreiben eines Kreditinstituts geht.
---

# Schuldenhilfe: P-Konto, Kontosperre, Bankmahnung

Typischer Fall: Ein Mitarbeiter bekommt eine Mahnung mit Kündigung der Kreditlinie.
Das Konto steht im Minus, die Bank kündigt an, Guthaben zu sperren und zu verrechnen.
Das nächste **Gehalt wäre damit weg**. Genau das verhindert das P-Konto.

## Reihenfolge (immer so)

1. **Gehalt umleiten.** Wichtigster und schnellster Handgriff. Neue IBAN in die
   Lohnbuchhaltung. Solange der Lohn auf das gesperrte Konto läuft, ist er gefährdet.
2. **P-Konto-Verlangen an die Bank** — Vorlage `vorlagen/pkonto-schreiben-muster.html`.
3. **Bescheinigung nach § 903 ZPO** ausstellen — Vorlage
   `vorlagen/pkonto-bescheinigung-903-muster.html`. Darf der **Arbeitgeber** ausstellen,
   also LEANS Tech GmbH selbst. Kostet nichts.
4. **Basiskonto** bei einer anderen Bank beantragen (§ 31 ZKG), dort als P-Konto führen.
5. **Schuldnerberatung** vor Ort einschalten (kostenlos, staatlich anerkannt).

## Die Rechtsgrundlagen, auf die es ankommt

- **§ 850k Abs. 1 ZPO** — Anspruch auf Umwandlung des Girokontos in ein P-Konto.
  Die Bank **muss**, spätestens zu Beginn des vierten Geschäftstages nach dem Verlangen.
  Keine Zustimmung, keine Bonitätsprüfung. **Nur ein P-Konto pro Person.**
- **§ 901 Abs. 2 ZPO** — bei Konto **im Minus** darf die Bank ab dem Verlangen nicht mehr
  aufrechnen/verrechnen, soweit das Geld auf einem P-Konto pfändungsfrei wäre.
  Das ist der eigentliche Hebel gegen die AGB-Sperre (Nr. 14 AGB der Banken).
- **§ 902 ZPO** — Erhöhungsbeträge für Unterhaltspflichten; **Kindergeld ist zusätzlich**
  geschützt (§ 902 S. 1 Nr. 2 ZPO), wird also nicht angerechnet.
- **§ 903 Abs. 1 S. 2 ZPO** — Aussteller der Bescheinigung: Arbeitgeber, Familienkasse,
  Sozialleistungsträger, Schuldnerberatung, Anwalt, Steuerberater.
- **§ 31 ZKG** — Anspruch auf ein Basiskonto, unabhängig von Schufa und Schulden.
  Angebot oder begründete Ablehnung binnen **10 Geschäftstagen** (§ 34 ZKG).
  Bei Ablehnung: **Antrag auf Verwaltungsverfahren bei der BaFin, § 48 ZKG** (kostenlos);
  keine Entscheidung binnen 4 Wochen -> Untätigkeitsklage (§ 50 ZKG).
- **§ 504a / § 505 Abs. 2 BGB** — bei dauerhaft hoher Überziehung muss die Bank von sich
  aus eine Beratung über günstigere Alternativen anbieten. Wurde das versäumt, ist das
  ein gutes Argument in der Verhandlung.
- **§ 497 Abs. 1 BGB** — Verzugszins beim Verbraucherdarlehen: 5 Prozentpunkte über
  Basiszinssatz. **§ 497 Abs. 3 S. 1 BGB** — Zahlungen tilgen zuerst Kosten, dann die
  **Hauptforderung**, erst zuletzt Zinsen. Zinseszins ist ausgeschlossen.
- **§ 850c ZPO** — Pfändungstabelle für Lohnpfändung (relevant für die Lohnbuchhaltung,
  falls ein Pfändungs- und Überweisungsbeschluss eingeht).

## Beträge — JEDES JAHR ZUM 1. JULI NEU PRÜFEN

Die Freibeträge werden jährlich zum 1. Juli angepasst (Pfändungsfreigrenzen-
bekanntmachung im BGBl., § 850c ZPO). Vor jedem Schreiben im Netz gegenprüfen,
nicht aus dem Gedächtnis schreiben.

Stand **1. Juli 2026 bis 30. Juni 2027**:

| Posten | Betrag |
|---|---|
| P-Konto-Grundfreibetrag | 1.589,99 EUR |
| + 1. unterhaltsberechtigte Person | 597,42 EUR |
| + 2. bis 5. Person, je | 332,83 EUR |
| Beispiel: zwei Kinder | **2.520,24 EUR** |
| Basiszinssatz § 247 BGB | 1,52 % (Verzugszins § 497 BGB: 6,52 %) |

Lohnpfändung § 850c ZPO, unpfändbar bis: 1.589,99 EUR (ohne Unterhalt),
2.189,99 (1), 2.519,99 (2), 2.859,99 (3), 3.189,99 (4), 3.519,99 (5).

## Was die Firma tun kann — ohne Geld

- Bescheinigung nach § 903 ZPO ausstellen, Gehalt umleiten,
  Einkommensbescheinigung für den Ratenantrag.
- **Arbeitgeberdarlehen** nur wenn Mittel da sind: bis **2.600 EUR** ist ein Zinsvorteil
  lohnsteuerlich unschädlich (Freigrenze der Lohnsteuer-Richtlinien) — vorher mit dem
  Steuerberater abstimmen. Auszahlung **niemals** auf das gesperrte Konto.
- Für die GmbH entsteht kein Risiko: Es sind private Schulden des Mitarbeiters.
  Eine spätere Lohnpfändung ist reine Routine in der Lohnabrechnung.

## Datenschutz (WICHTIG)

Das Repository `genesis-dwg-service` ist **öffentlich**. Deshalb gilt:

- **Niemals** personenbezogene Daten von Mitarbeitern in dieses Repo committen —
  keine Namen, Anschriften, Geburtsdaten, IBANs, Aktenzeichen, Schuldenhöhen,
  Gehälter, Geburtsurkunden.
- Die Vorlagen in `vorlagen/` enthalten ausschließlich anonyme Platzhalter
  (Max Mustermann, Musterbank). Die für einen echten Fall gefüllte Fassung wird
  **nur im Scratchpad** erzeugt und dem Nutzer als Download geschickt.
- Auch keine Unterschriften- oder Stempelbilder committen.

## Unterschrift und Stempel des Geschäftsführers

Semir Redžić hat generell freigegeben, seine Unterschrift und den Firmenstempel
elektronisch in eigene Dokumente der LEANS Tech GmbH einzusetzen — nicht jedes Mal
neu nachfragen. Die Dateien liegen in **Google Drive**, Ordner
`unterschriften und stempel`:

- `Semir Original Unterschrift.png` (PNG mit Transparenz, am besten geeignet)
- `stempel.jpg` (Firmenstempel LEANS Tech GmbH)

Ablauf: Datei über den Drive-Konnektor herunterladen, als data-URI ins HTML
einbetten, den Signaturblock in ein `<div style="page-break-inside:avoid">`
packen (sonst rutscht der Stempel auf die nächste Seite), danach das gerenderte
PDF zur Kontrolle als Bild ansehen.

**Nur für eigene Dokumente der LEANS Tech GmbH.** Niemals für Dokumente Dritter
und niemals die Unterschrift einer anderen Person einsetzen.

## E-Mail-Signatur Semir Redžić

Verbindlicher Wortlaut — **exakt so übernehmen**, nichts hinzufügen, nichts umformatieren
(Original im Drive: `Semir - 20240607 - Signatur - in Ordnung.rtf`):

```
Freundliche Grüße

Semir Redzic

Klima ▪ Lüftung ▪ Sanitär ▪ Heizung

Wir verstehen unser Handwerk

+491708280836

sr@leanstech-gmbh.de

www.leanstech-gmbh.de

Firmensitz: Berlepschstr. 165, 14165 Berlin

Geschäftsführer: Semir Redzic
```

Achtung: Im Signaturblock **ohne** diakritische Zeichen („Semir Redzic“, nicht
„Redžić“), Telefonnummer **ohne Leerzeichen**, keine HRB-/USt-IdNr.-Zeile und keine
Zusatzzeile „Geschäftsführer“ unter dem Namen. Für jeden Mitarbeiter existiert eine
eigene Signaturdatei im selben Drive-Ordner (`<Vorname> - 20240607 - Signatur - in
Ordnung.rtf`).

Kundenmails gehen immer von **sr@** (IONOS) raus, nicht von der Gmail-Adresse.

## Ton und Grenzen

- Immer klarstellen: **rechtliche Orientierung, keine Rechtsberatung.** Bei Eskalation
  auf Schuldnerberatung oder Fachanwalt für Bank- und Kapitalmarktrecht verweisen.
- Einen **Anspruch auf Ratenzahlung oder Zinserlass gibt es nicht** — das ist
  Verhandlung. Das Argument, das zieht: Wenn Lohn und Konto gesetzlich geschützt sind,
  ist die Rate für die Bank der einzige Weg, überhaupt Geld zu sehen.
- Rate lieber **niedrig und sicher** ansetzen als hoch und geplatzt.
- Fristen im Mahnschreiben sofort im Kalender nachrechnen und im Chat nennen.

## PDF rendern

`/opt/pw-browsers/chromium-*/chrome-linux/chrome --headless --no-sandbox --disable-gpu
--no-pdf-header-footer --print-to-pdf=<datei> <html>`

Danach das PDF mit Read öffnen und prüfen, ob die Gliederung stimmt.
Entwurf immer zuerst als Download in den Chat (Freigabe-Workflow), nichts ungefragt
ins Drive hochladen.
