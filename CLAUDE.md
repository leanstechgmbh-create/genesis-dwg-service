# CLAUDE.md

## Angebote — Standardvorgabe (immer befolgen)

**Wenn der Nutzer ein „Angebot" wünscht (Wort „Angebot" / „angebot"), IMMER automatisch
im echten LEANS-Tech-Template erstellen — NICHT nachfragen, einfach im Format der
bestehenden ~100 Angebote (Referenz: Angebot 297) ausgeben, anzeigen und abspeichern.**

### Ablauf
1. Angebot mit dem Generator `gen_angebot.py` erstellen (Positionsdaten oben im Script
   anpassen). Das Script erzeugt das **branded PDF** exakt im Original-Template — das PDF
   ist die **fertige, kanonische Angebotsdatei** (Logo `leans_logo.png` ist aus
   Bestandsangebot 297 extrahiert). **IMMER auch das vollständige PDF direkt hier im Chat
   senden** + kurze Zusammenfassung.
   - WICHTIG: Die per Drive-Schnittstelle erzeugten Google-Docs können das **Logo NICHT
     einbetten** (Bild-Import nicht unterstützt) und sehen „nackt" aus — sie sind NUR eine
     editierbare Kopie, NICHT das Angebot. Niemals das nackte Doc als „das Angebot" zeigen.
     Maßgeblich ist immer das PDF.
2. PDF dem Nutzer senden (SendUserFile) **und IMMER zusätzlich in `~/Downloads` ablegen**
   (macht `gen_angebot.py` automatisch).
3. **Drive-Ablage standardmäßig NICHT nötig** — das branded PDF (Chat + `~/Downloads`) ist
   das Angebot. **Keine nackten Google-Docs mehr in Drive anlegen.** Nur auf ausdrücklichen
   Wunsch in Drive ablegen (dann via n8n/Drive-Flow mit Logo, nicht als Doc-Kopie).
   - Ordner falls doch gebraucht: „Cloud Angebote" `1lS-n7kan-pwbgFDP_NYwyRtGI-JIMd6C`
     (neu) / „Bestand Angebote" `1KDlM4-GnjG_9IcERuwYmuyKoEw2HHLov` (alt),
     Drive-Stamm `0AM9CvPIUCfZkUk9PVA`.
4. **Angebotsnummer-Regel:**
   - **Neues Angebot** (neues Thema/Vorgang) → neue, fortlaufende Nummer.
   - **Änderung/Iteration am selben, im Chat besprochenen Angebot** → Nummer NICHT ändern,
     Datei einfach überschreiben.
   - Zuletzt vergeben: **283** → nächste neue = 284.
5. Fehlende Felder (Kunde/Empfänger, Bauvorhaben) als Platzhalter `[…]` einsetzen,
   nicht extra nachfragen.

### Template (echtes Layout, siehe `gen_angebot.py` + `leans_logo.png`)
- **Format:** US-Letter (612×792 pt), Schrift **Arial/LiberationSans**.
- **Kopf:** Logo `leans_logo.png` oben links (54,54, ca. 86×58 pt); Empfänger oben rechts,
  rechtsbündig, beginnend mit fettem „An:".
- **Absenderzeile** (klein, grau): `Semir Redžić • Berlepschstr. 165 • 14165 Berlin •
  Tel: +49 170 828 0836 • info@leanstech-gmbh.de`, darunter dunkelblauer Akzentbalken.
- **Titel** „ANGEBOT" groß/fett. Darunter Meta (fett): Angebotsnummer, Angebotsdatum,
  Gültig bis, Leistung, Gewerk, Fabrikat.
- **Tabelle:** dunkelblaue Kopfzeile (RGB 26,82,118, weiße Schrift) mit Spalten
  `OZ | Beschreibung | Menge | Einh. | EP netto | Betrag netto | MwSt`; hellblaue
  Abschnittszeile (RGB 234,241,248) je Gewerk; Positionen mit fettem Titel + grauer
  Sub-Beschreibung; OZ wie 1.1, 1.2, …; MwSt-Spalte = „§13b".
- **Summenblock** rechts: `Nettobetrag`, `USt § 13b UStG (0 %)  0,00 €`,
  `Gesamtbetrag` (dunkelblauer Balken, weiß, fett). Gesamtbetrag = Nettobetrag.
- **Seite 2 (AGB, kursiv):** Leistungsumfang-Absatz, §13b-Hinweis, „Dieses Angebot ist
  freibleibend und gültig bis <Datum>.", unten Fußzeile:
  `LEANS Tech GmbH • Berlepschstr. 165, 14165 Berlin • GF: Semir Redžić • HRB 249080 B •
  USt-IdNr: DE357948720 • IBAN: DE24 1001 9000 1000 0012 17 • Adyen Bank • BIC: ADYBDEB2XXX`

### Regeln
- Standardmäßig **Reverse-Charge nach § 13b UStG** (Bauleistung, B2B) — keine MwSt
  ausweisen (USt 0 %, Gesamt = Netto), außer der Nutzer sagt ausdrücklich etwas anderes.
- Gültigkeit: **3 Monate** ab Angebotsdatum.
- Sprache: Deutsch.
- „ohne Geräte" = nur Leistung/Arbeit (Geräte bauseits gestellt).

## Kontakte / E-Mail-Aliasse
- **Mita** („schick zu Mita") → `info@aam-handwerk-montage.de`

## Repo
GENESIS DWG-Service (FastAPI, `main.py`): DWG/DXF rein → kleine Änderungen → DWG/DXF raus.
