# Register Elektro, MSR und Gebäudeautomation

> **Neu erstellt 22.08.2026, noch nicht fachlich gegengeprüft.** Im Drive gab
> es zu Elektro keinen Volltext und keinen Leitfaden. Dieses Register ist ein
> Prüfraster für die TGA-Schnittstelle — es ersetzt **keine** Elektrofachplanung
> und keinen Stromlaufplan. Anschlussleistungen, Schutzorgane, Selektivität,
> Netzform und Kurzschlussdaten kommen von der Elektroplanung bzw. der
> Elektrofachkraft.

## Elektro — Regelwerke

| Regelwerk | Zweck | Status/Volltext | Projektprüfung |
|---|---|---|---|
| DIN VDE 0100 Reihe (insb. -410, -420, -430, -520, -540, -600) | Errichten von Niederspannungsanlagen: Schutzmaßnahmen, Kabel/Leitungen, Erdung, Erstprüfung | aRdT, Lizenz | Netzform, Schutz gegen elektrischen Schlag, Überstrom, Leitungsdimensionierung, Erstprüfprotokoll |
| DIN VDE 0100-701/-702/-703/-705 | Bäder/Duschen, Schwimmbäder, Saunen, landwirtschaftliche Betriebsstätten | aRdT, Lizenz | Bereichseinteilung, IP-Schutzart, Potentialausgleich |
| DIN VDE 0100-722 | Ladeeinrichtungen für Elektrofahrzeuge | aRdT, Lizenz | Fehlerstromschutz, Lastmanagement, Netzbetreiber-Anmeldung |
| DIN VDE 0105-100 | Betrieb elektrischer Anlagen | aRdT, Lizenz | Arbeiten unter Spannung, Freischalten, fünf Sicherheitsregeln, Verantwortlichkeiten |
| DIN VDE 0701-0702 | Prüfung nach Instandsetzung / Wiederholungsprüfung ortsveränderlicher Geräte | aRdT, Lizenz | Prüfumfang, Fristen, Protokoll |
| DIN 18015 Reihe | Elektrische Anlagen in Wohngebäuden | aRdT, Lizenz | Anzahl Stromkreise, Ausstattungswerte, Leitungsführungszonen |
| DIN EN IEC 62305 Reihe | Blitz- und Überspannungsschutz | aRdT, Lizenz | Risikoanalyse, äußerer/innerer Blitzschutz, SPD-Konzept, Trennungsabstand |
| TAB des Netzbetreibers + NAV | Technische Anschlussbedingungen Niederspannung | V/R, meist frei | Anmeldung, Zählerplatz, Anschlussleistung, Steuerbare Verbrauchseinrichtungen (§ 14a EnWG) |
| VDE-AR-N 4100 | Anschluss an das Niederspannungsnetz | aRdT | Zählerplatz, Messkonzept, Anmeldeverfahren |
| DIN VDE 0100-560 / Landesbauordnung | Sicherheitsstromversorgung, Funktionserhalt | aRdT/L | nach Brandschutzkonzept |
| DGUV Vorschrift 3 | Prüfung elektrischer Anlagen und Betriebsmittel | R | Fristen, befähigte Person, Dokumentation |

## Elektro-Schnittstellen der TGA (immer abzustimmen)

- Anschlussleistungen, Anlaufströme, Schutzorgane, Selektivität, Netzform und
  Kurzschlussdaten durch die Elektroplanung bestätigen lassen.
- Abschalt-/Not-Aus-Konzept, Potentialausgleich, Überspannungsschutz, EMV und
  sichere Trennung.
- Sicherheitsfunktionen und Funktionserhalt nach Brandschutzkonzept.
- Hersteller-Schaltpläne und Freigaben sind verbindlich; ein TGA-Schema
  ersetzt keinen Stromlaufplan.
- Für jedes Gerät festhalten: Spannung/Phasen, Leistung, Absicherung,
  Zuleitungsquerschnitt, Anlaufart, FI-Typ (bei Frequenzumrichtern ggf. Typ B),
  Steuerspannung, Verriegelungen.
- Frequenzumrichter: EMV-gerechte Verlegung, geschirmte Motorleitung,
  Netzdrossel/Filter, Ableitströme.
- Kältemittel-/Gasräume: Zündquellenfreiheit, Detektion, Zwangslüftung und
  Not-Aus mit der Elektroplanung abstimmen (siehe `kaelte-klima.md`).

## MSR und Gebäudeautomation

| Regelwerk | Zweck |
|---|---|
| VDI 3814 Reihe | Gebäudeautomation: Funktionen, Kennzeichnung, Planung |
| DIN EN ISO 52120-1 | Einfluss der Automation auf die Energieeffizienz |
| DIN EN ISO 16484 Reihe, insb. BACnet | GA-Systeme und Kommunikation |
| VDI 3813 Reihe | Raumautomation |

Für jedes Projekt zu liefern:

- Anlagenkennzeichnung nach festgelegtem Schlüssel
- Datenpunktliste (AI/AO/DI/DO, Bus), Sensor- und Aktorliste
- Regelbeschreibung je Anlage in Worten, nicht nur als Schema
- Betriebsarten- und Prioritätenmatrix (Normal, Sommer, Nacht, Warmwasser-
  vorrang, Störung, Brandfall, Handbetrieb)
- Alarmierung, Ausfallverhalten, Rückfallebene, Handübersteuerung
- Brandschutzmatrix (Klappen, Entrauchung, Abschaltungen)
- Schnittstellen zu Fremdgewerken und Fremdsystemen inkl. Protokoll
- Funktionsprüfung/Wirkprinzipprüfung mit Protokoll

## Projektergebnis

Elektro-Leistungsliste je Verbraucher, abgestimmte Schnittstellenliste,
Datenpunktliste, Regelbeschreibung, Betriebsarten-/Prioritätenmatrix,
Alarm- und Ausfallkonzept, Funktionsprüfprotokoll, Einweisung und
Betreiberunterlagen.
