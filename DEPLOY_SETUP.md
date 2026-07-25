# Automatik-Deploy einrichten (einmalig, nur Klicken — kein Terminal)

Danach deployt sich der Service bei jeder Code-Änderung selbst.
Funktioniert am Handy oder PC im normalen Browser (kein Cloud Shell nötig).

**Zwei Wege — einer genügt.** Weg A ist kürzer und sicherer, weil kein
Generalschlüssel für dein Google-Projekt bei GitHub liegt. Weg B ist der
bisherige Weg über die GitHub-Action.

---

## Weg A: Cloud Run baut selbst aus GitHub (empfohlen, ~3 Min)

Kein Schlüssel, keine JSON-Datei, keine GitHub-Secrets. Google verbindet sich
selbst mit dem Repository und baut bei jedem Push auf `main`.

1. Öffne https://console.cloud.google.com/run (mit leanstechgmbh@gmail.com)
2. **Zuerst oben die Projektauswahl prüfen** — im falschen Projekt ist die
   Dienstliste leer, obwohl der Dienst existiert.
3. Steht dort **`genesis-dwg-service`**? → anklicken, dann
   **„Kontinuierliche Bereitstellung einrichten"** (englisch: *Set up
   continuous deployment*) und weiter bei Schritt 4.
   **Liste leer / Dienst nicht vorhanden?** (dann wurde noch nie deployt) →
   **Dienst erstellen** → **„Kontinuierlich aus einem Repository
   bereitstellen"** → **Cloud Build einrichten** → weiter bei Schritt 4.
4. **Mit GitHub verbinden** → GitHub-Login → die Cloud-Build-App für
   `leanstechgmbh-create/genesis-dwg-service` freigeben
   **Repository:** `leanstechgmbh-create/genesis-dwg-service`
   **Branch:** `^main$`
   **Build-Typ:** **Dockerfile** (Pfad `/Dockerfile`) → **Speichern**
5. Beim Neuanlegen diese Einstellungen setzen — sie entsprechen dem, was der
   Workflow bisher per `gcloud run deploy` mitgegeben hat:

   | Einstellung | Wert | Warum |
   |---|---|---|
   | Dienstname | `genesis-dwg-service` | Anleitungen/URLs bauen darauf auf |
   | Region | **europe-west3** | Frankfurt |
   | Authentifizierung | **Nicht authentifizierte Aufrufe zulassen** | sonst erreichen Slack, n8n und die Webseite den Service nicht |
   | Speicher | **1 GiB** | weniger reicht für LibreDWG nicht |
   | Zeitlimit | **300 s** | DWG-Umwandlung dauert |
   | Port | **8080** | `ENV PORT=8080` im Dockerfile |

6. **Erstellen / Speichern** → der erste Build startet sofort (dauert 5–8 Min,
   weil LibreDWG kompiliert wird)

Beim Speichern fragt Google nach den nötigen Rechten und richtet sie selbst
ein. Läuft der Build durch, steht die Service-URL oben auf der Seite.

**Danach:** Die GitHub-Action `deploy.yml` würde parallel weiterhin rot laufen
(sie kennt die Secrets nicht). Entweder ignorieren oder abschalten:
Repository → **Actions** → links **Deploy zu Cloud Run** → **⋯ → Disable
workflow**.

---

## Weg B: GitHub-Action mit zwei Secrets (~8 Min)

### Schritt 1: Schlüssel in der Google-Konsole erzeugen (~5 Min)

1. Öffne https://console.cloud.google.com/iam-admin/serviceaccounts
   (mit leanstechgmbh@gmail.com; falls oben eine Projektauswahl kommt: das Projekt anklicken)
2. Oben **„+ Dienstkonto erstellen"**
3. Name: `github-deploy` → **„Erstellen und fortfahren"**
4. Bei „Rolle auswählen" nacheinander diese ZWEI Rollen hinzufügen:
   - **Bearbeiter** (unter „Einfach/Basic")
   - **Dienstkontonutzer** (Suchfeld: „Dienstkontonutzer" / „Service Account User")
   → **„Weiter"** → **„Fertig"**
5. In der Liste beim neuen Konto rechts auf **⋮ → „Schlüssel verwalten"**
6. **„Schlüssel hinzufügen" → „Neuen Schlüssel erstellen" → JSON → „Erstellen"**
   → eine Datei wird heruntergeladen (z. B. `projektname-abc123.json`)
7. Notiere außerdem die **Projekt-ID** (steht in der Projektauswahl oben,
   z. B. `leanstech-genesis-123456` — die ID, nicht der Anzeigename)

### Schritt 2: Beide Werte bei GitHub einfügen (~3 Min)

1. Öffne https://github.com/leanstechgmbh-create/genesis-dwg-service/settings/secrets/actions
2. **„New repository secret"**:
   - Name: `GCP_SA_KEY`
   - Secret: den **kompletten Inhalt** der heruntergeladenen JSON-Datei einfügen
     (Datei mit Editor/Notizen öffnen → alles markieren → kopieren → einfügen)
   - **„Add secret"**
3. Nochmal **„New repository secret"**:
   - Name: `GCP_PROJECT`
   - Secret: die Projekt-ID aus Schritt 1.7
   - **„Add secret"**

**Wichtig:** Die JSON-Datei ist ein Generalschlüssel fürs Google-Projekt.
Nur bei GitHub-Secrets einfügen, niemals in den Chat, niemals ins Repository.

Fehlt eines der beiden Secrets, bricht der Workflow gleich am Anfang mit einer
klaren Meldung ab („fehlende GitHub-Secrets: …") und deployt nichts — der
Service läuft dann unverändert auf dem Stand des letzten erfolgreichen Deploys.

---

## Schritt 3 (beide Wege): Bescheid sagen

Sag Claude „Deploy läuft" bzw. „Secrets sind drin" — Claude prüft das Ergebnis,
ruft die Health-Antwort des Services ab (`GET /` zeigt `slack`, `mail_ready`,
`instagram`, `youtube`, `chatgpt`, `bus`) und sagt, welche
Umgebungsvariablen noch fehlen.

**Danach noch einzutragen** (Cloud Run → Dienst bearbeiten → Variablen; sie
bleiben bei allen künftigen Deploys erhalten):

| Variable | Wofür | Anleitung |
|---|---|---|
| `ANTHROPIC_API_KEY` | Claude im Slack-Bot | — |
| `SLACK_BOT_TOKEN`, `SLACK_SIGNING_SECRET` | Slack-Bot | `SLACK_SETUP.md` |
| `GENESIS_API_KEY` | schützt `/modify-dwg`, `/send-mails`, Bus | frei wählbar |
| `OPENAI_API_KEY` | ChatGPT-Brücke, Bus | `LEANS_OS_BUS.md` |
| `GMAIL_APP_PASSWORD` | Bestellungen auf Rechnung, Mailer | — |
| 5 Social-Schlüssel | Instagram-Reels, YouTube-Shorts | `SOCIAL_SETUP.md` |
| `STRIPE_SECRET_KEY` | Kartenzahlung im Katalog (optional) | — |
