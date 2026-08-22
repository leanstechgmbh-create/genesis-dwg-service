---
name: tga-wissen
description: Fachliche Arbeitsbasis für alle TGA-Gewerke der LEANS Tech GmbH — Heizung/Wärmepumpe, Lüftung/RLT, Kälte/Klima, Sanitär/Trinkwasser/Entwässerung, Elektro/MSR sowie Bau-, Anlagen- und Vertragsrecht. Nutzen bei jeder fachlichen Frage, Auslegung, Berechnung, Angebots- oder Planprüfung, bei Normen-, Regelwerks- und Rechtsfragen (DIN, EN, VDI, DVGW, GEG, TrinkwV, F-Gase, VOB) und bei Streit-, Mängel-, Abnahme- oder Nachtragsthemen.
---

# TGA-Wissensbasis LEANS Tech GmbH

Gültig für alle laufenden und zukünftigen Projekte. Quelle: Drive-Ordner
`Fachwissen TGA` (Stand 17.08.2026), hier versioniert und erweitert.

## Wie dieser Skill benutzt wird

1. Diese Datei lesen — sie enthält die Arbeitsregeln.
2. Danach **nur** das Register des betroffenen Gewerks aus `references/`
   lesen. Nicht alle Register auf Verdacht laden.
3. Projektspezifische Pläne, Aufmaße und Berechnungen immer zusätzlich im
   jeweiligen Projektordner (Drive) prüfen.

| Frage betrifft | Datei |
|---|---|
| Kessel, Heizflächen, Rohrnetz, Pumpen, Speicher, MAG, Gas, Wärmepumpe, Bivalenz | `references/heizung-waermepumpe.md` |
| Trinkwasser, Warmwasser, Zirkulation, Hygiene, Enthärtung, Abwasser, Rückstau | `references/sanitaer-trinkwasser.md` |
| Luftmengen, Kanalnetz, Ventilatoren, RLT, Küchenlüftung, Brandschutzklappen | `references/lueftung-rlt.md` |
| Kühllast, Split/VRF, Kältemittel, F-Gase, Sicherheitszonen, Kondensat | `references/kaelte-klima.md` |
| Anschlussleistung, Schutzorgane, Datenpunkte, Regelbeschreibung, GA/BACnet | `references/elektro-msr.md` |
| Brandschutz, Schall, Arbeitsschutz, Schnittstellen zwischen Gewerken | `references/brandschutz-schall.md` |
| GEG, TrinkwV, BImSchG, BetrSichV, Genehmigung, Betreiberpflichten | `references/recht-normen.md` |
| Vertrag, VOB, Nachtrag, Behinderung, Abnahme, Mängel, Verzug, Sicherheiten | `references/baurecht-vertrag.md` |
| Bundesland, LBO, FeuVO, VV TB, Versorger-TAB | `references/landesrecht-check.md` |
| Woher kommt eine Quelle, welche Lizenz, wann geprüft | `references/quellen-pflege.md` |

## Quellenhierarchie (bei Konflikt gilt die niedrigere Nummer)

1. Geltendes EU-/Bundes-/Landesrecht und Genehmigungsbescheid
2. Eingeführte Technische Baubestimmungen (Landesumsetzung, nicht MVV TB)
3. Anwendbare aktuelle technische Regeln/Normen (DIN, EN, VDI, DVGW)
4. Herstelleranforderungen und Konformitätsunterlagen des exakten Typs
5. Projektspezifischer Vertrag/LV
6. Fachbuch/Leitfaden — nur als Erläuterung, nie als Nachweis

Konflikte nicht still selbst entscheiden: Konflikt, betroffene Funktion und
benötigte Freigabe dokumentieren.

## Unveränderliche Regeln

- **Nichts erfinden.** Fehlt ein Normvolltext oder eine Herstellerangabe,
  wird das als Blocker/offener Nachweis markiert — keine Plausibelwerte.
- **Kein Beispielwert ungeprüft übernehmen.** DN, Kvs, Pumpe, Speicher, MAG
  und Ventilzahl erst nach Berechnung festschreiben.
- **Normbezeichnung ≠ Norminhalt.** Die Register hier dürfen frei genutzt
  werden. Geschützte Volltexte (DIN, VDI, DVGW) nur mit rechtmäßiger
  Firmenlizenz öffnen oder ablegen — keine Kopien aus unbekannter Quelle.
- **Status kennzeichnen.** Jedes Ergebnis eindeutig als Vorplanung,
  Ausführungsplanung oder Bestandsdokumentation benennen. Vorplanung ist
  niemals eine Ausführungsfreigabe.
- Diese Wissensbasis hilft beim Planen, ersetzt aber keine objektbezogene
  Berechnung, Fachplanerfreigabe, Herstellerfreigabe oder vorgeschriebene
  Prüfung.

## Statuslogik in allen Registern

- **R – Recht:** Gesetz/Verordnung, bei erfülltem Anwendungsbereich verbindlich.
- **L – Landesrecht:** Bundesland, teils Kommune/Versorger bestimmen die Fassung.
- **TB – Technische Baubestimmung:** erst über Landeseinführung verbindlich.
- **aRdT – anerkannte Regel der Technik:** vertraglich/haftungsrechtlich
  regelmäßig maßgeblich; Anwendungsbereich prüfen.
- **V – Vertrag:** VOB/C, LV, Hersteller- oder Betreiberanforderung.
- **I – Information:** Leitfaden/Planungshilfe, kein Normersatz.
- **Frei** = Volltext legal frei zugänglich · **Lizenz** = Volltext beschaffen.

## Projektablauf

1. Nutzungsart, Gebäudeklasse, Sonderbau, Bundesland, Kommune, Betreiber klären.
2. Anlagenarten, Leistungen, Drücke, Temperaturen, Kältemittel/Füllmengen,
   Brennstoffe und Aufstellorte erfassen.
3. Rechtsmatrix und Landesrecht prüfen; Genehmigungen/Anzeigen/Prüfstellen
   bestimmen (`references/landesrecht-check.md` je Projekt ausfüllen).
4. Aktuelle Normausgaben und Herstellerunterlagen beschaffen.
5. Heiz-/Kühllast, Warmwasser, Luftmengen, Rohr-/Kanalnetz, Druckhaltung,
   Schall, Brand und Regelzustände berechnen.
6. Eingabedaten und fehlende Angaben sichtbar auflisten.
7. Schnittstellen zwischen den Gewerken und **alle** Betriebszustände
   dokumentieren.
8. Mengen und Angebot erst aus dem geprüften Stand ableiten.
9. Abnahme-, Inbetriebnahme-, Hygiene-, Prüf- und Betreiberunterlagen festlegen.

## Zeichenstandard für Schemata

- Große, übersichtliche Zeichenfläche, genormte technische Symbole.
- Vorlauf rot, Rücklauf blau gestrichelt; Trinkwasserwege eindeutig separat.
- Pumpen, Ventile, Fühler und Sicherheitseinrichtungen am tatsächlichen
  Einbauort, nicht schematisch „irgendwo".
- Leitungen mit Medium, DN und Flussrichtung beschriften.
- Legende, Bauteilnummern und Planungsstatus angeben.
- Fremde Schemen nur als Prinzipreferenz, immer ans konkrete Projekt anpassen.

## Pflege

- Projektspezifische Ergebnisse bleiben im Projektordner.
- Allgemeingültige neue Erkenntnisse erst nach Quellenprüfung hierher
  übernehmen (Vorschläge im Drive unter `99 Projekt-Learnings`).
- Veraltete Norm-/Herstellerstände sichtbar kennzeichnen und ersetzen —
  alte Nachweise nicht stillschweigend weiterverwenden.
- Prüfrhythmus: Rechtsquellen quartalsweise und vor Projektstart; Normen bei
  Projektstart und vor Ausführungsfreigabe; Herstellerunterlagen vor
  Bestellung, Montage und Inbetriebnahme.
