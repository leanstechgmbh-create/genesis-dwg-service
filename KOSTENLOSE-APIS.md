# Kostenlose APIs — Kurzliste für LEANS

Stand: 26.08.2026

**Public APIs** (<https://github.com/public-apis/public-apis>) ist kein Programm,
sondern ein Verzeichnis: über tausend offene Schnittstellen, sortiert nach Thema.
Es gibt nichts zu installieren — Lesezeichen setzen, fertig.

Damit die Liste einen Nutzen hat, hier die Handvoll Dienste, die zu unserem
Geschäft passen. Alle ohne Anmeldung und ohne Schlüssel nutzbar, also direkt
im n8n-Knoten „HTTP Request" einsetzbar.

| Zweck bei uns | Dienst | Adresse |
|---|---|---|
| Wetter/Vorhersage — Wartungstermine, Hitzeperioden, Klima-Nachfrage | Open-Meteo | `open-meteo.com` |
| Deutsche Wetterdaten des DWD (Stationen, Messwerte) | Bright Sky | `brightsky.dev` |
| Feiertage je Bundesland — Termin- und Personalplanung | Nager.Date | `date.nager.at` |
| Adresse → Koordinaten, für Anfahrt und Routen | Nominatim (OpenStreetMap) | `nominatim.openstreetmap.org` |
| Währungskurse (EZB) für Materialeinkauf | Frankfurter | `frankfurter.app` |

Naheliegende Anwendungen:

- **Wartungs-Rechner / Wartungsverträge:** vor einer Hitzewoche automatisch
  Erinnerungsmails an Kunden mit Wartungsvertrag (Wetter-API + n8n).
- **Terminplanung:** Feiertage je Bundesland abfragen, damit keine Montage auf
  einen Feiertag gelegt wird.
- **Angebote:** Kundenadresse in Koordinaten umwandeln und die Anfahrt-Pauschale
  aus der Entfernung berechnen.

Hinweise:

- Aus der Cloud-Sitzung heraus sind diese Adressen wegen der Netzsperre nicht
  erreichbar — der Test gehört ohnehin in n8n, wo die Abfragen später laufen.
- Nutzungsregeln beachten: Nominatim erlaubt höchstens eine Abfrage pro Sekunde
  und verlangt einen eigenen User-Agent (z. B. `LEANS-Tech-n8n`).
- Für kostenlose Dienste ohne Vertrag gilt: keine Garantie auf Verfügbarkeit.
  Nichts darauf bauen, was zwingend funktionieren muss (z. B. Rechnungsstellung).
