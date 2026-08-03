# LEANS Kosmos — Cockpit für den rechten Monitor

Der Bildschirm aus dem Video, gebaut mit deinen Vorgängen: Sternenkarte,
Partikel-Orb in der Mitte, Briefing-Leiste, Live-Zähler, Suchzeile.
Läuft als einzelne Seite im Browser, ohne Internet, ohne Installation.

## Starten

1. Diesen Ordner `kosmos/` auf deinen Rechner kopieren — Desktop reicht.
2. **Windows:** Doppelklick auf `Kosmos-rechter-Monitor.cmd`
   **Mac:** Doppelklick auf `Kosmos-rechter-Monitor.command`
   (beim ersten Mal ggf. Rechtsklick → Öffnen)

Der Kosmos geht im Vollbild auf dem rechten Monitor auf.

**Geht er auf dem falschen Bildschirm auf?** Datei mit dem Editor öffnen und
oben `X` auf die Breite deines **linken** Monitors setzen:

| Linker Monitor | X |
|---|---|
| Full HD (1920×1080) | `1920` |
| WQHD (2560×1440) | `2560` |
| 4K (3840×2160) | `3840` |

Ohne Launcher geht es auch: `index.html` doppelklicken, Fenster auf den rechten
Monitor ziehen, **F11** drücken.

## Bedienung

| Taste / Klick | Wirkung |
|---|---|
| Klick auf einen Knoten | Detailkarte rechts: Beträge, Status, Fälligkeit, verknüpfte Vorgänge |
| Klick ins Leere | Karte schließen |
| `/` | Sprung in die Suchzeile |
| `Esc` | Suche und Auswahl zurücksetzen |
| `F` | Vollbild an/aus |
| Business / Privat | schaltet den ganzen Kosmos um |

In der Suchzeile funktionieren normale Begriffe (`beispielstr`, `muster bau`)
und diese Kürzel: `offen`, `rechnungen`, `angebote`, `kunden`, `projekte`,
`wartung`, `aufgaben`. Was nicht passt, wird dunkel — was passt, leuchtet.

## Deine Daten

Zwei Dateien, und nur die zweite gehört dir:

| Datei | was drin steht |
|---|---|
| `daten.js` | Beispieldaten, alles erfunden. Liegt im öffentlichen Repo. |
| `daten.privat.js` | deine echten Vorgänge. Wird **nicht** eingecheckt und überschreibt beim Laden die Beispiele. |

Fehlt `daten.privat.js`, läuft der Kosmos mit den Beispielen weiter — kaputt
geht nichts.

### Der Weg: Register rein, Kosmos raus

`daten.privat.js` schreibst du nicht von Hand, sondern lässt sie bauen:

1. **Register exportieren.** `Master <Jahr> Ausgang.csv` aus dem Drive nach
   `kosmos/quellen/` legen. Da kommen die Rechnungsnummern und Beträge her.
2. **Zuordnung pflegen.** `zuordnung.beispiel.json` einmal als
   `zuordnung.json` kopieren und eintragen, was das Register nicht weiß:
   welche Rechnung zu welchem Projekt und Kunden gehört, was bezahlt ist,
   welche Angebote laufen, welche Punkte offen sind.
3. **Bauen lassen:**

   ```bash
   python3 tools/kosmos-daten.py
   ```

   Das Werkzeug schreibt `daten.privat.js`, zählt zusammen, was es gefunden
   hat, und meckert bei krummen Zuordnungen (Kunde nicht angelegt, Betrag
   im Register anders als in der Zuordnung, `id` doppelt).
4. **Seite neu laden** (`F5`). Oben in der Briefing-Leiste steht der Stand.

Rechnungen, die im Register stehen, aber noch keinem Projekt zugeordnet sind,
kommen als blasse Punkte auf den äußeren Ring — Status `unbekannt`, sie zählen
nicht als offen. Genau so siehst du, was noch einzusortieren ist. Mit
`--nur-zugeordnet` bleiben sie weg.

### Was in die Zuordnung gehört

- **typ** — `projekt`, `kunde`, `rechnung`, `angebot`, `wartung`, `aufgabe`
  (bestimmt Farbe und Größe des Knotens)
- **bereich** — `business` oder `privat`
- **status** — `gestellt` / `bezahlt` / `mahnung` / `unbekannt` bei Rechnungen,
  `offen` / `beauftragt` / `abgelehnt` bei Angeboten.
  Erledigtes und Unbekanntes wird blass und zählt nicht mit.
- **projekt / kunde** — der `kurz`-Name von oben. Daraus entstehen die Linien:
  Rechnung hängt am Kunden, Projekt hängt an allem, was auf es zeigt.

Die Zähler oben rechts rechnen sich selbst aus:
offene Rechnungen (Summe netto), offene Angebote (Summe netto),
Anzahl offener Punkte, nächster Wartungstermin.

## Was das hier ist — und was nicht

Das Cockpit steht **neben** Obsidian, nicht darin: Obsidian bleibt der Ort zum
Schreiben (siehe `obsidian-setup/`), der Kosmos ist die Übersicht für den
zweiten Monitor. Beide benutzen dieselben Farben.

Nichts geht ins Netz: keine Verbindung zu Drive, Gmail oder n8n. Der Weg von
Drive ins Cockpit läuft über den CSV-Export von Hand. Dieses Repo ist
**öffentlich** — deshalb stehen `zuordnung.json`, `daten.privat.js` und
`quellen/` in `.gitignore`. Bitte auch keine Kundennamen oder Beträge in
`daten.js` schreiben.
