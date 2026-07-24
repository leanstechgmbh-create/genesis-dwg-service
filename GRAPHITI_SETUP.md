# Graphiti einrichten — Gedächtnis-Konnektor für claude.ai (einmalig)

Graphiti merkt sich Fakten dauerhaft über alle Chats hinweg (Kunden,
Projekte, Ansprechpartner, letzte Rechnungsnummer …) und legt sie in
einem Wissensgraphen ab. Danach kann Claude in jeder Sitzung darauf
zugreifen.

Alles läuft im Browser, kein Terminal nötig. Dauer: ca. 20 Minuten.
Der Code (Ordner `graphiti-mcp/`) ist schon fertig im Repository —
es fehlen nur 4 Schlüssel von Dir.

## Schritt 1: Kostenlose Neo4j-Datenbank anlegen (~5 Min)

Hier wird das Gedächtnis dauerhaft gespeichert (kostenlose Stufe reicht).

1. Öffne https://console.neo4j.io und melde Dich mit
   leanstechgmbh@gmail.com an („Continue with Google")
2. **„New Instance"** → Typ **„Free"** (AuraDB Free) wählen,
   Region Europa (z. B. Frankfurt) → erstellen
3. Es erscheint EINMALIG ein Fenster mit Zugangsdaten →
   **„Download"** klicken (Datei mit Passwort) und gut aufheben
4. Notiere Dir aus der Instanz-Übersicht:
   - **Connection URI** — sieht so aus: `neo4j+s://xxxxxxxx.databases.neo4j.io`
   - **Passwort** — aus der heruntergeladenen Datei (Benutzer ist `neo4j`)

## Schritt 2: OpenAI-Schlüssel holen (~5 Min)

Graphiti braucht ein KI-Modell zum Erkennen und Einsortieren der Fakten
(Kosten: Cent-Beträge pro Nutzung).

1. Öffne https://platform.openai.com und registriere Dich / melde Dich an
2. Menü **„API keys"** → **„Create new secret key"** → Name z. B.
   `graphiti` → Schlüssel kopieren (beginnt mit `sk-…`, wird nur
   einmal angezeigt!)
3. Unter **„Billing"** einmalig kleines Guthaben aufladen (5–10 €
   reichen sehr lange)

## Schritt 3: Geheimwort erzeugen (~1 Min)

Das Geheimwort schützt Dein Gedächtnis — nur wer es kennt, kommt an die
Daten. Es wird Teil der Konnektor-Adresse.

- Nimm eine lange Zufallszeichenkette, NUR Kleinbuchstaben und Zahlen,
  mindestens 30 Zeichen, z. B. aus einem Passwort-Generator —
  oder sag Claude im Chat „erzeug mir ein Geheimwort für Graphiti".
- Beispiel-Format: `k7w2m9x4q8r5t1z6b3n0p7v4c2f9h5j8`
- NIEMALS weitergeben und nicht in Dateien/Chats ablegen (GitHub-Secret
  und claude.ai-Eingabe sind okay).

## Schritt 4: Die 4 Werte bei GitHub eintragen (~3 Min)

1. Öffne https://github.com/leanstechgmbh-create/genesis-dwg-service/settings/secrets/actions
2. Viermal **„New repository secret"**:

   | Name | Inhalt |
   |---|---|
   | `GRAPHITI_NEO4J_URI` | Connection URI aus Schritt 1 (`neo4j+s://…`) |
   | `GRAPHITI_NEO4J_PASSWORD` | Neo4j-Passwort aus Schritt 1 |
   | `GRAPHITI_OPENAI_API_KEY` | OpenAI-Schlüssel aus Schritt 2 (`sk-…`) |
   | `GRAPHITI_MCP_PATH_SECRET` | Dein Geheimwort aus Schritt 3 |

(Die zwei Google-Secrets `GCP_SA_KEY` und `GCP_PROJECT` aus
`DEPLOY_SETUP.md` müssen schon vorhanden sein — sind sie, wenn der
Automatik-Deploy läuft.)

## Schritt 5: Deploy starten (~5 Min Wartezeit)

Sag Claude im Chat „Graphiti-Secrets sind drin" — oder selbst:
https://github.com/leanstechgmbh-create/genesis-dwg-service/actions →
Workflow **„Deploy Graphiti-MCP zu Cloud Run"** → **„Run workflow"**.

Am Ende des Logs steht die Service-Adresse, z. B.
`https://genesis-graphiti-mcp-xxxxx.a.run.app`. Deine Konnektor-Adresse
ist dann (Geheimwort selbst einsetzen):

```
https://genesis-graphiti-mcp-xxxxx.a.run.app/<DEIN-GEHEIMWORT>/mcp/
```

## Schritt 6: Auf claude.ai als Konnektor eintragen (~2 Min)

1. claude.ai → **Einstellungen → Konnektoren**
2. **„Eigenen Konnektor hinzufügen"** (Custom Connector)
3. Name: `Graphiti`, URL: die Konnektor-Adresse aus Schritt 5
4. Hinzufügen — eine Anmeldung (OAuth) ist nicht nötig, der Schutz
   ist das Geheimwort in der Adresse

## Schritt 7: Testen

Im Chat: „Merk Dir: <irgendein Fakt>" → neuen Chat öffnen →
„Was weißt Du über <Thema>?" — kommt der Fakt zurück, läuft alles.

## Kosten & Sicherheit

- **Neo4j AuraDB Free:** 0 € (schläft nach längerer Inaktivität ein,
  wacht beim nächsten Zugriff wieder auf; bei Aura ggf. alle 30 Tage
  einmal in die Konsole schauen, damit die Free-Instanz nicht wegen
  Inaktivität pausiert/gelöscht wird)
- **OpenAI:** Cent-Beträge pro gespeichertem/gesuchtem Fakt
- **Cloud Run:** bei dieser Nutzung praktisch 0 € (skaliert auf null)
- Das Geheimwort ist der einzige Schutz der Daten. Wenn es je
  durchsickert: einfach neues Geheimwort als GitHub-Secret setzen,
  Workflow neu laufen lassen, Konnektor-URL auf claude.ai anpassen.
