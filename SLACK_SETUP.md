# Slack + Claude Integration — Einrichten

Der GENESIS-Service enthaelt jetzt einen Claude-gestuetzten Slack-Bot.
**@mention** im Channel oder **DM** an den Bot → Claude antwortet im Thread.

## 1 — Slack App anlegen
→ https://api.slack.com/apps → **Create New App** → *From scratch*

**OAuth & Permissions** → *Bot Token Scopes* hinzufuegen:
```
app_mentions:read
chat:write
im:history
im:read
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
- `@DeinBot Was kann GENESIS?` → Claude antwortet im Thread.
- Status pruefen: `GET /` zeigt `"slack": true`, wenn Token + Secret gesetzt sind.

---
*Technik:* Endpoint `POST /slack/events` in `slack_bot.py`. Signaturpruefung per
HMAC-SHA256 (5-Min-Replay-Schutz), Claude-Aufruf laeuft im Hintergrund, damit Slack
das geforderte 200 innerhalb von 3 Sekunden erhaelt. Retries werden per `event_id`
dedupliziert, Bot-eigene Nachrichten ignoriert (keine Schleifen).
