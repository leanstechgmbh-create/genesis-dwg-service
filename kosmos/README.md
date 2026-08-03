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

In der Suchzeile funktionieren normale Begriffe (`mehringdamm`, `sp construct`)
und diese Kürzel: `offen`, `rechnungen`, `angebote`, `kunden`, `projekte`,
`wartung`, `aufgaben`. Was nicht passt, wird dunkel — was passt, leuchtet.

## Deine Daten pflegen

Alles steht in **`daten.js`**. Nur diese Datei anfassen, mit jedem Texteditor.
Ein Eintrag sieht so aus:

```js
{ id: "ar-2026-41", typ: "rechnung", bereich: "business",
  titel: "2026-41 · 3. AR",
  info: "SP Construct · Mehringdamm",
  netto: 9800.00, status: "gestellt", faellig: "2026-09-01",
  verbunden: [] },
```

- **typ** — `projekt`, `kunde`, `rechnung`, `angebot`, `wartung`, `aufgabe`
  (bestimmt Farbe und Größe des Knotens)
- **bereich** — `business` oder `privat`
- **status** — `gestellt` / `bezahlt` / `mahnung` bei Rechnungen,
  `offen` / `beauftragt` / `abgelehnt` bei Angeboten.
  Erledigtes wird automatisch blass.
- **verbunden** — die `id`s, zu denen eine Linie gezogen wird.
  Rechnungen gehören an Projekt **und** Kunde. Ohne Verbindungen
  bleibt der Kosmos eine Punktwolke statt eines Netzes.

Nach dem Speichern einfach die Seite neu laden (`F5`).

Die Zähler oben rechts rechnen sich selbst aus:
offene Rechnungen (Summe netto), offene Angebote (Summe netto),
Anzahl offener Punkte, nächster Wartungstermin.

## Was das hier ist — und was nicht

Das Cockpit steht **neben** Obsidian, nicht darin: Obsidian bleibt der Ort zum
Schreiben (siehe `obsidian-setup/`), der Kosmos ist die Übersicht für den
zweiten Monitor. Beide benutzen dieselben Farben.

Die Daten liegen lokal in `daten.js` — nichts geht ins Netz, keine Verbindung
zu Drive oder n8n. Wenn das später automatisch aus dem Master-Register oder
aus n8n gefüttert werden soll, ist das der nächste Schritt.
