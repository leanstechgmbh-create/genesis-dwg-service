# Register Heizung, Wärmepumpe und Hybrid

## Planung und Berechnung

| Regelwerk | Zweck | Status/Volltext | Pflichtprüfung im Projekt |
|---|---|---|---|
| DIN EN 12831-1 + DIN/TS 12831-1 | Raum-/Gebäudeheizlast und nationale Ergänzung | aRdT, Lizenz | Eingabedaten, Lüftungswärmeverluste, Normaußentemperatur, Bestandsschätzung kennzeichnen |
| DIN EN 12831-3 | Heizlast Trinkwassererwärmung | aRdT, Lizenz | Bedarfsprofil, Speicher-/Ladeleistung, Gleichzeitigkeit |
| DIN EN 12828 | Planung wassergeführter Heizungsanlagen | aRdT, Lizenz | Sicherheit, Druckhaltung, Erzeugung, Verteilung, Regelung |
| DIN EN 14336 | Installation/Inbetriebnahme/Abnahme wassergeführter Anlagen | aRdT, Lizenz | Spülen, Dichtheit, Einregulierung, Dokumentation |
| VDI 2035 Blatt 1/2 | Steinbildung und wasserseitige Korrosion | aRdT, Lizenz | Anlagenvolumen, Werkstoffe, Füll-/Ergänzungswasser, Leitfähigkeit/pH, Anlagenbuch |
| VDI 4645 | Wärmepumpen in Ein-/Mehrfamilienhäusern | aRdT, Lizenz; legaler Einblick zentral gespeichert | Dimensionierung, Hydraulik, Schall, Inbetriebnahme, Dokumentation |
| DIN EN 14511 Reihe | Leistungsprüfung Wärmepumpen/Kältemaschinen | aRdT, Lizenz | Betriebspunkte statt nur Nennwert |
| DIN EN 14825 | Teillast und saisonale Effizienz | aRdT, Lizenz | SCOP/SEER, Klimazone, Auslegung |
| DIN EN 12102 Reihe | Schallleistungspegel | aRdT, Lizenz | Herstellerwert und Betriebszustände |
| VDI 2067 Reihe | Wirtschaftlichkeit gebäudetechnischer Anlagen | aRdT, Lizenz | Betrachtungszeitraum, Energiepreise, Wartung, Ersatz |
| VDI 3805 / Herstellerdaten | Produktdatensätze | I/Hersteller | Abmessung, Anschluss, Leistung, Druckverlust, Wartungsraum |

## Hydraulik und Komponenten

- Rohrnetz aus Auslegungsvolumenstrom und zulässigem Druckverlust
  dimensionieren; DN niemals nur aus Leistung oder einem Beispielschema
  ableiten.
- Pumpen nach Volumenstrom, ungünstigstem Strang, Ventilautorität,
  Regelbereich, Mindest-/Maximalvolumenstrom und Reserven auswählen — nicht
  nach Anschlussgröße.
- Mehrere Puffer nur parallel/Tichelmann ausführen, wenn Anschlusshydraulik,
  gleiche Druckverluste und Herstellerbedingungen dies tragen; Reihenschaltung
  ist eine eigene Funktionsentscheidung.
- Pufferfunktion eindeutig bestimmen: hydraulische Entkopplung,
  Mindestanlagenvolumen, Laufzeitverlängerung oder Leistungsspeicherung.
- Für jeden Wärmeerzeuger und Speicher: Absperrung, Entleerung, Entlüftung,
  Rückflussverhinderung/Schwerkraftbremse, Messstellen und Wartbarkeit
  projektbezogen prüfen.
- Rückströmung, Fehlzirkulation und gegenseitige Erzeugerdurchströmung
  verhindern.
- MAG/Druckhaltung nach Wasserinhalt, Temperaturen, statischer Höhe, Vordruck,
  Sicherheitsventil und Reserve rechnen — nicht pauschal aus kW.
- Luft-, Schlamm- und Magnetitabscheidung sowie Wasserqualität berücksichtigen.
- Sicherheitskette, Frostschutz, Abtauenergie, Mindestumlauf, Sperrzeiten,
  Spitzenlast und Störbetrieb schriftlich beschreiben.

## Wärmeerzeuger und Betriebsarten

- Leistung und Modulationsbereich bei den realen Auslegungspunkten prüfen.
- Betriebsweise eindeutig festlegen: monoenergetisch, bivalent-parallel,
  bivalent-alternativ oder hybrid.
- Mindest-/Maximalvolumenstrom, Restförderhöhe, Abtauanforderungen und
  Herstellerhydraulik beachten.
- Spitzenlast, Redundanz, Sperrzeiten, Bivalenzpunkt und Notbetrieb
  dokumentieren.
- Betriebszustände vollständig durchzeichnen: Grundlast, paralleler
  Spitzenlastbetrieb, Nur-Gas, Warmwasservorrang, Störung/Notbetrieb,
  Sommerbetrieb, Pumpennachlauf.

## Speicher und Trinkwarmwasser

- Speicher nicht nur nach Litern auswählen: Zapfprofil, Spitzenleistung,
  Ladezeit, Tauscherfläche, Bereitschaftsverluste und Zirkulation prüfen.
- Trinkwasser und Heizungswasser sicher trennen.
- Hygienisch erforderliche Temperaturen und bestimmungsgemäßen Betrieb
  gewährleisten (Details: `sanitaer-trinkwasser.md`).
- Parallele Speicher hydraulisch abgleichen, Fühler-/Ladestrategie festlegen.

## Gas und Feuerung

| Regelwerk | Zweck | Hinweis |
|---|---|---|
| DVGW-TRGI / DVGW G 600 | Gasinstallation | Lizenz; Netzbetreiber-TAB und eingetragenes Unternehmen ergänzen |
| 1. BImSchV | Emissionen/Überwachung | Nennleistung, Brennstoff, Bestand/Neuanlage prüfen |
| DIN EN 13384 Reihe | Abgasanlagenberechnung | Schornstein/Mehrfachbelegung/Kondensat nachweisen |
| DIN EN 15502 Reihe | Gas-Heizkessel | Produkt-/Aufstellanforderungen mit Herstellerunterlagen |
| Landes-FeuVO | Aufstellung, Verbrennungsluft, Abgas | Bundeslandfassung verbindlich; Schornsteinfeger früh beteiligen |

## GEG-Prüfpunkte

- Art der Maßnahme und Stichtag/Übergang.
- Systemtemperaturen, Regelung, hydraulischer Abgleich, Dämmung und
  Betreiberinformation.
- Erneuerbare-/Hybridanforderungen und Nachweisführung.
- Keine Förderbedingung mit gesetzlicher Mindestanforderung verwechseln.

## Frei verfügbare Volltexte im Drive (`Fachwissen TGA`)

- `01_BWP_Leitfaden_Hydraulik.pdf` — firmenübergreifende WP-Hydraulikschemata,
  überschlägige Volumenströme und Schaltungsprinzipien. Herstellerangaben
  bleiben für die Feinplanung bindend.
- `04_BWP_Leitfaden_Waermepumpendimensionierung.pdf` — Heizlast, Heizkurve,
  Modulationsbereich, Bivalenz- und Taktpunkt. Behandelt vor allem
  leistungsgeregelte Luft/Wasser-WP in kleineren Wohngebäuden: Methoden
  übertragen, Beispiele nicht kopieren.
- `02_VDI_4645_Inhaltsverzeichnis_Entwurf_2026.pdf` — nur Einblick, keine
  vollständige Richtlinie.
- `03_Weishaupt_WTC_GB_120_250_Montage_Betrieb.pdf` — verbindliche
  Herstellerbasis für Anschlüsse, zulässige Betriebsbedingungen und
  Kesselhydraulik der WTC-GB-Baureihe; herstellerspezifisch, nicht allgemein
  übertragbar.

## Projektergebnis

Heizlastnachweis, Anlagenleistung/Bivalenz, Hydraulikschema,
Betriebsartenmatrix, Rohrnetz, Pumpen/Armaturen, Druckhaltung/Sicherheit,
Schall, Elektro/MSR, Mengen, Inbetriebnahme-/Abnahmeplan und offene Freigaben.
