# Obsidian im „Kosmos"-Look — Anleitung

Ziel: Obsidian sieht aus wie die Sternenkarte aus dem Video — schwarzer
Hintergrund, leuchtende Knoten, 3D-Graph, den man drehen kann.

## Was geht — und was nicht

| Aus dem Video | In Obsidian |
|---|---|
| Dreidimensionaler, drehbarer Wissens-Graph | **Ja** — Community-Plugin (siehe Schritt 2) |
| Schwarzer Hintergrund, Neon-Knoten, farbige Gruppen | **Ja** — CSS-Snippet + Farbgruppen |
| Beschriftete Knoten (BUSINESS, PRODUCTS, SERVICES …) | **Ja** — über Ordner/Tags als Farbgruppen |
| Leiste oben („BRIEFING · LIVE"), Zähler für Leads/Tasks | **Teilweise** — mit Dataview als Notiz-Kopfzeile, nicht als schwebende Leiste |
| Leuchtender Partikel-Orb in der Mitte, Kamerafahrten | **Nein** — das ist eine eigene Web-Anwendung, kein Obsidian |
| Chat-Eingabe „talk to kronos" im Graph | **Nein** in dieser Form; Chat-Plugins gibt es, aber als Seitenleiste |

Kurz: Optik und 3D-Graph bekommst du sehr nah hin. Der Partikel-Effekt und
die schwebende Live-Leiste sind ein eigenprogrammiertes Frontend.

## Schritt 1 — CSS-Snippet einbauen

1. `snippets/leans-kosmos.css` kopieren nach
   `<Dein Vault>/.obsidian/snippets/leans-kosmos.css`
   (Ordner `snippets` ggf. anlegen)
2. Obsidian → Einstellungen → **Erscheinungsbild**
   → Basisfarbschema auf **Dunkel**
3. Ganz unten bei **CSS-Snippets** auf das Nachlade-Symbol, dann den
   Schalter bei `leans-kosmos` einschalten

Sofort sichtbar: schwarzer Hintergrund, cyanfarbene Links, violette Tags,
Graph mit dunkler Vignette.

## Schritt 2 — 3D-Graph installieren

Einstellungen → **Community-Plugins** → Durchsuchen → nach `3D Graph`
suchen. Es gibt mehrere Varianten (u. a. *3D Graph* und *Extended Graph*);
nimm die mit den meisten Downloads und aktuellem Datum. Installieren,
aktivieren, dann über die Befehlspalette (`Strg/Cmd + P`) → `3D Graph`
öffnen.

Einstellungen im Plugin, die dem Video am nächsten kommen:
- Hintergrund: `#020307`
- Knotengröße klein, Link-Deckkraft niedrig (ca. 0,25)
- „Show labels" an, Labelgröße klein
- Partikel/Link-Animation an, falls vorhanden

Wichtig: Community-Plugins müssen einmalig freigeschaltet werden
(Einstellungen → Community-Plugins → „Eingeschränkten Modus" ausschalten).

## Schritt 3 — Farbgruppen im Graph

Graph-Ansicht öffnen → Zahnrad oben links → **Groups** → Gruppe hinzufügen.
Das erzeugt die farbigen Cluster wie im Video:

| Suchbegriff | Farbe | Bedeutung |
|---|---|---|
| `path:10-Projekte` | `#38e1ff` Cyan | Baustellen / BV |
| `path:20-Kunden` | `#ffd166` Gold | Auftraggeber |
| `path:30-Rechnungen` | `#3ddc97` Grün | Rechnungen, AR |
| `path:40-Angebote` | `#a855f7` Violett | Angebote |
| `path:50-Wartung` | `#ff7a59` Orange | Wartungsverträge |
| `tag:#offen` | `#ff4d6d` Rot | offene Punkte |

## Schritt 4 — Ordnerstruktur und Vorlagen

Siehe `struktur.md` für den Aufbau des Vaults und `vorlagen/` für fertige
Notiz-Vorlagen (Projekt, Kunde, Rechnung, Angebot, Wartung). Die Vorlagen
sind so gebaut, dass durch die Verlinkung untereinander automatisch das
Sternennetz entsteht — ohne Verlinkung bleibt der Graph eine Punktwolke.

## Schritt 5 (optional) — Live-Zahlen wie die Briefing-Leiste

Plugin **Dataview** installieren, dann in `00-Start.md`:

````markdown
```dataview
TABLE länge AS "Offene Punkte"
FROM #offen
GROUP BY file.folder
```
````

Das ersetzt die Zählerleiste aus dem Video — als Tabelle oben auf der
Startseite statt als schwebendes Element.

## Hinweis zur Umgebung

Dein Obsidian liegt auf deinem eigenen Rechner. Diese Sitzung läuft in der
Cloud und hat darauf keinen Zugriff — deshalb liegen die Dateien hier im
Repo zum Kopieren. Wenn etwas nicht wie erwartet aussieht: Screenshot in
den Chat ziehen, dann passe ich das CSS an.
