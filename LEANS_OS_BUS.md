# Nachrichten-Bus: Claude ↔ ChatGPT (~Echtzeit, über einen Ordner)

Zwei KI-Systeme sollen miteinander arbeiten, ohne dass du Text hin- und
herkopierst. Der Austausch läuft **über einen Ordner**, nicht über einen
direkten Draht zwischen den Systemen.

## Warum ein Ordner (und nicht einfach ein Endpunkt)

| | Ordner-Bus | Offener HTTP-Draht |
|---|---|---|
| Angriffsfläche | kein eingehender Port zwischen den Systemen, Zugriff nur per IAM/Dienstkonto | öffentlich erreichbar, braucht Key + Rate-Limit + Signaturprüfung |
| Nachvollziehbarkeit | jede Nachricht ist eine Datei, vollständiges Protokoll | nur was selbst mitgeloggt wird |
| Ausfall | Service offline → Nachrichten warten, nichts geht verloren | Nachricht ist weg |
| Tempo | Poll 5–30 s · **mit Push-Trigger 1–3 s** | 1–2 s |

Der Ordner ist also nicht der langsame Weg — nur wenn man ihn *pollt*.
Mit einem Ereignis-Trigger (unten) wacht der Service 1–3 s nach dem Ablegen
einer Datei auf. Das ist das „ca. Echtzeit", das für Arbeit im Team reicht.

## Aufbau

```
<basis>/eingang/      fremde Systeme legen hier ab   (nur schreiben)
<basis>/ausgang/      GENESIS/Claude antwortet hier  (nur schreiben)
<basis>/protokoll/    abgearbeitete Nachrichten, append-only Archiv
```

Getrennte Schreibrechte je Richtung sind Absicht: keine Seite kann Nachrichten
der anderen fälschen, ändern oder verschwinden lassen.

Eine Nachricht ist eine JSON-Datei, Name `<zeitstempel>-<absender>-<id>.json`
(dadurch von Haus aus chronologisch sortiert):

```json
{
  "id": "a1b2c3…", "ts": "2026-07-25T10:14:00Z",
  "von": "chatgpt", "an": "claude",
  "thread": "8f21c0d4",
  "typ": "frage",
  "text": "Wie würdest du die Kanalführung im 2. OG lösen?",
  "ref": "", "titel": ""
}
```

Erlaubt sind ausschließlich diese Felder (`ai_bus.ERLAUBTE_FELDER`) — alles
andere wird beim Einlesen verworfen, damit keine Steuerfelder eingeschmuggelt
werden können.

## Die drei Sicherheitsregeln

1. **Fremdtext ist niemals ein Befehl.** Was im Eingang liegt, ist *Eingabe*.
   Es kann keine Aktion auslösen — es gibt keine Aktions-Whitelist, der Bus
   kennt nur Text. `ai_bus.pruefe` markiert Nachrichten, die nach einem
   Aktions- oder Prompt-Injection-Versuch aussehen (Mailversand, Zahlung,
   Löschen, „ignoriere alle Anweisungen", Fragen nach Schlüsseln), mit
   `verdacht`. Solche Nachrichten werden **nicht automatisch beantwortet**,
   sondern zur Freigabe vorgelegt.
2. **Keine Secrets in Nachrichten.** Der Bus ist für Fachinhalte da. Schlüssel
   liegen als Cloud-Run-Variablen, nicht im Ordner und nicht im Repo.
3. **Kein Endpunkt ohne Schlüssel.** Ohne `GENESIS_API_KEY` antworten alle
   Bus- und ChatGPT-Endpunkte mit `503` — geschlossen ist der Standard, nicht
   offen. Zusätzliche Grenzen: max. 100 KB je Nachricht, max. 10 Nachrichten
   je Durchlauf, Idempotenz über die Nachrichten-ID (Retries verdoppeln nichts).

## Einrichten

### 1. Schlüssel setzen (Cloud Run)

```bash
gcloud run services update genesis-dwg-service --region europe-west3 \
  --update-env-vars GENESIS_API_KEY=<eigenes-geheimnis>,OPENAI_API_KEY=sk-…,OPENAI_MODEL=gpt-4o
```

`OPENAI_API_KEY` kommt von platform.openai.com. **Ein ChatGPT-Abo (Plus/Pro)
reicht dafür nicht** — API-Nutzung wird getrennt abgerechnet.

### 2. Ablage wählen

**Variante A — GCS-Bucket (empfohlen, ~Echtzeit):**

```bash
# privater Bucket, keine öffentlichen Rechte
gcloud storage buckets create gs://leans-os-bus --location europe-west3 \
  --uniform-bucket-level-access

# Dienstkonto des Service darf lesen/schreiben
gcloud storage buckets add-iam-policy-binding gs://leans-os-bus \
  --member serviceAccount:<service-account> --role roles/storage.objectAdmin

gcloud run services update genesis-dwg-service --region europe-west3 \
  --update-env-vars BUS_GCS_BUCKET=leans-os-bus,BUS_PREFIX=bus
```

Der Zugriff läuft über das Dienstkonto vom Metadata-Server — kein Schlüssel im
Code, keine Schlüsseldatei im Image.

**Variante B — normaler Ordner:** `BUS_DIR=/pfad/zum/ordner`. Gut zum Testen
oder mit einem gemounteten Laufwerk. Auf Cloud Run ist `/tmp` nicht dauerhaft,
also für den Dauerbetrieb Variante A nehmen.

### 3. Wecker: aus „Poll" wird „Ereignis"

**Ereignisgesteuert (1–3 s)** — GCS-Ereignis → Pub/Sub → Cloud Run:

```bash
gcloud pubsub topics create leans-os-bus-eingang
gcloud storage buckets notifications create gs://leans-os-bus \
  --topic leans-os-bus-eingang --event-types OBJECT_FINALIZE \
  --object-prefix bus/eingang/

gcloud pubsub subscriptions create leans-os-bus-push \
  --topic leans-os-bus-eingang \
  --push-endpoint "https://<service-url>/bus/tick?key=<GENESIS_API_KEY>"
```

Der Schlüssel steht als Query-Parameter in der Push-URL, weil Pub/Sub keine
eigenen Header setzen kann — die URL ist damit selbst ein Geheimnis und gehört
nicht in Tickets oder Chats. `/bus/tick` wertet den Nachrichtenkörper nicht
aus: der Ordner ist die Wahrheit, der Trigger nur das Klingeln.

**Oder einfach pollen (5–30 s)** — Cloud Scheduler:

```bash
gcloud scheduler jobs create http leans-os-bus-tick --location europe-west3 \
  --schedule "* * * * *" --uri "https://<service-url>/bus/tick" \
  --http-method POST --headers "X-Genesis-Key=<GENESIS_API_KEY>"
```

## Bedienung

### Aus Slack (der bequemste Weg)

```
@GENESIS frag gpt: Lohnt sich VRF gegenüber Multisplit bei 6 Innengeräten?
@GENESIS dialog: Kanalführung 2. OG Mehringdamm — Blech oder Wickelfalz? (3 Runden)
```

Beim Dialog wird jede Runde einzeln in den Thread gepostet — du liest live mit
und kannst jederzeit eingreifen. Am Ende kommt ein Fazit mit Empfehlung.

### Endpunkte

| Endpunkt | Zweck |
|---|---|
| `GET /bus/status` | Ablage + Anzahl offener Nachrichten |
| `POST /bus/tick` | Eingang abarbeiten (Trigger-Ziel) |
| `POST /bus/senden` | Nachricht in den Ausgang legen |
| `POST /ai/ask` | **Gegenrichtung:** ChatGPT fragt Claude, Antwort synchron |
| `POST /gpt/ask` | Wir fragen ChatGPT (`"stream": true` für Token-Streaming) |
| `POST /gpt/dialog` | Claude ↔ ChatGPT, mehrere Runden + Fazit |

```bash
# ChatGPT fragen, Antwort streamend
curl -N -X POST https://<service-url>/gpt/ask \
  -H "X-Genesis-Key: $GENESIS_API_KEY" -H "Content-Type: application/json" \
  -d '{"text":"Kurz: Vorteile Wickelfalzrohr gegenüber Blechkanal?","stream":true}'

# Gegenrichtung: als ChatGPT-Action konfigurieren
curl -X POST https://<service-url>/ai/ask \
  -H "X-Genesis-Key: $GENESIS_API_KEY" -H "Content-Type: application/json" \
  -d '{"von":"chatgpt","text":"Welche Änderungen kann GENESIS an DWG-Plänen vornehmen?"}'
```

Für ChatGPT als **Custom GPT** trägst du `/ai/ask` als Action ein
(Authentifizierung: API-Key im Header `X-Genesis-Key`). Damit kann ChatGPT
GENESIS befragen — aber nichts auslösen.

## Was der Bus bewusst NICHT kann

- **Keine Aktionen.** Kein Mailversand, kein Drive-Upload, keine Zahlung, keine
  Rechteänderung über eine Bus-Nachricht. Das bleibt beim Freigabe-Workflow aus
  `CLAUDE.md`: Entwurf in den Chat, du gibst frei, dann passiert es.
- **Kein Dauer-Socket zur ChatGPT-Weboberfläche.** Es gibt keinen Weg, sich in
  ein laufendes ChatGPT-Browserfenster einzuhängen; alles läuft über die API.
- **Kein Live-Sprechen.** Für Mikrofon-Gespräche in ~300 ms bräuchte es die
  Realtime-API über WebSocket/WebRTC und eine Umgebung mit dauerhaften
  Verbindungen — Cloud Run skaliert Instanzen weg und ist dafür die falsche
  Basis. Bei Bedarf getrennt bauen.

## Rolle in LEANS OS

Der Bus ist der Baustein, an dem später alle KI-Teilnehmer hängen: `von`/`an`
sind offen (`claude`, `chatgpt`, `genesis`, `nutzer`), `thread` hält Gespräche
zusammen, das Protokoll ist die durchsuchbare Historie. Weitere Systeme
kommen dazu, indem sie in `eingang/` schreiben und `ausgang/` lesen dürfen —
ohne dass am Service etwas geändert werden muss.
