# Slack + Claude Integration — Einrichten

Der GENESIS-Service enthaelt jetzt einen Claude-gestuetzten Slack-Bot.
**@mention** im Channel oder **DM** an den Bot → Claude antwortet im Thread.

## 1 — Slack App anlegen
→ https://api.slack.com/apps → **Create New App** → *From scratch*

**OAuth & Permissions** → *Bot Token Scopes* hinzufuegen:
```
app_mentions:read
chat:write
channels:history     (Thread-Kontext in oeffentlichen Channels lesen)
groups:history       (Thread-Kontext in privaten Channels lesen)
im:history
im:read
files:read           (hochgeladene DWG/DXF herunterladen)
files:write          (bearbeitete DWG/DXF zurueck in den Thread laden)
```
Dann **Install to Workspace** → das **Bot User OAuth Token** (`xoxb-...`) kopieren.

**Basic Information** → *Signing Secret* kopieren.

## 2 — Environment-Variablen setzen
Beim Deploy (Cloud Run / Docker) setzen:
```
SLACK_BOT_TOKEN       = xoxb-...        (Bot User OAuth Token)
SLACK_SIGNING_SECRET  = ...             (Signing Secret)
ANTHROPIC_API_KEY     = sk-ant-...      (Claude API Key)
```
Optional:
```
CLAUDE_MODEL          = claude-opus-4-8 (Standard)
CLAUDE_MAX_TOKENS     = 4096
CLAUDE_HISTORY        = 20   (max. Thread-Nachrichten als Kontext)
CLAUDE_SYSTEM_PROMPT  = eigener System-Prompt
```

Cloud-Run-Beispiel:
```bash
gcloud run deploy genesis-ezdxf --source . --region europe-west3 \
  --allow-unauthenticated --memory 1Gi --timeout 300 \
  --set-env-vars SLACK_BOT_TOKEN=xoxb-...,SLACK_SIGNING_SECRET=...,ANTHROPIC_API_KEY=sk-ant-...
```

## 3 — Events-API verbinden
**Event Subscriptions** → *Enable Events* →
**Request URL:** `https://<deine-service-url>/slack/events`

Slack schickt eine `url_verification` — der Service antwortet automatisch mit dem
Challenge-Wert; die URL wird sofort gruen (*Verified*).

**Subscribe to bot events** → hinzufuegen:
```
app_mention      (Bot wird in einem Channel erwaehnt)
message.im       (Direktnachricht an den Bot)
```
Speichern → ggf. App neu installieren, wenn Slack dazu auffordert.

## 4 — Testen
- Bot in einen Channel einladen: `/invite @DeinBot`
- **Frage:** `@DeinBot Was kann GENESIS?` → Claude antwortet im Thread.
- **Plan-Aenderung:** eine **DWG/DXF-Datei** hochladen und im selben Kommentar
  `@DeinBot Zuluft-Auslass bei 1200,800 um 200mm nach rechts verschieben`
  → der Bot erzeugt die `elements`, bearbeitet die Datei und laedt die fertige
  DWG/DXF in den Thread.
- Status pruefen: `GET /` zeigt `"slack": true`, wenn Token + Secret gesetzt sind.

## Zwei Modi
| Eingabe im Thread | Was passiert |
|---|---|
| Nur Text (`@Bot …` oder DM) | Claude antwortet als GENESIS-Assistent (mit Thread-Kontext) |
| **DWG/DXF-Datei + Text** | Claude → `elements`-JSON → `dwg_core.modify_drawing` → fertige Datei zurueck |

---
*Technik:* Endpoint `POST /slack/events` in `slack_bot.py`. Signaturpruefung per
HMAC-SHA256 (5-Min-Replay-Schutz), schwere Arbeit laeuft im Hintergrund, damit Slack
das geforderte 200 innerhalb von 3 Sekunden erhaelt. Retries werden per `event_id`
dedupliziert, Bot-eigene Nachrichten ignoriert (keine Schleifen). Chat nutzt den
gesamten Thread-Verlauf (`conversations.replies`). Die Plan-Aenderung verwendet
dieselbe Kernlogik (`dwg_core.py`) wie der `/modify-dwg`-Endpoint — Claude erzeugt
das `elements`-JSON per Tool-Use aus der natuerlichsprachlichen Beschreibung.
