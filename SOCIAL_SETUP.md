# Social-Posting einrichten (Instagram + YouTube)

Der Service kann fertige Videos **selbst posten**: als **Instagram-Reel** und als
**YouTube-Short** — über den Endpunkt `POST /post-social`. Danach postet Claude
(oder n8n) mit einem einzigen Befehl, ganz ohne Handy.

Damit das darf, verlangen Meta und Google **einmalig** eine Freigabe (Schlüssel).
Das ist bei jedem Tool so (auch Buffer, Later & Co.). Dauert zusammen ca. 30 Minuten.
Wenn du irgendwo hängst: Screenshot schicken, ich sage dir den nächsten Klick.

---

## Teil 1: Instagram (über Meta) — 4 Schlüssel-Schritte

**Voraussetzung (hast du vermutlich schon):**
- Instagram-Konto ist ein **professionelles Konto** (Business/Creator)
- und ist mit der **Facebook-Seite** (Leansklima) **verknüpft**
  (Facebook-Seite → Einstellungen → Verknüpfte Konten → Instagram)

**Schritt 1 — Meta-App anlegen (einmalig, kostenlos):**
1. https://developers.facebook.com/apps öffnen, mit dem Facebook-Konto anmelden
2. „App erstellen" → Anwendungsfall „Sonstiges" → Typ **„Business"** → Name egal
   (z. B. „Leans Poster") → erstellen

**Schritt 2 — Token holen:**
1. https://developers.facebook.com/tools/explorer öffnen
2. Rechts oben deine App auswählen
3. Bei „Berechtigungen" diese vier hinzufügen:
   `pages_show_list`, `business_management`, `instagram_basic`, `instagram_content_publish`
4. „Generate Access Token" → anmelden → alles bestätigen
5. Den angezeigten Token kopieren (das ist der **kurze** Token, hält nur 1 Stunde)

**Schritt 3 — langlebigen Token machen:**
App-ID und App-Geheimcode findest du im App-Dashboard unter
„Einstellungen → Allgemein". Dann diese Adresse im Browser aufrufen
(die 3 GROSSEN Wörter ersetzen):

```
https://graph.facebook.com/v21.0/oauth/access_token?grant_type=fb_exchange_token&client_id=APP_ID&client_secret=APP_GEHEIMCODE&fb_exchange_token=KURZER_TOKEN
```

Die Antwort enthält `"access_token": "..."` → das ist der **lange Token**.

**Schritt 4 — Seiten-Token (läuft nie ab) + Instagram-ID holen:**
1. Im Browser aufrufen (LANGER_TOKEN ersetzen):
   `https://graph.facebook.com/v21.0/me/accounts?access_token=LANGER_TOKEN`
   → bei der Leansklima-Seite das `access_token` kopieren = **META_ACCESS_TOKEN**
   (dieser Seiten-Token läuft nicht ab) und die `id` merken (= SEITEN_ID)
2. Im Browser aufrufen:
   `https://graph.facebook.com/v21.0/SEITEN_ID?fields=instagram_business_account&access_token=LANGER_TOKEN`
   → die Zahl unter `instagram_business_account.id` = **IG_USER_ID**

---

## Teil 2: YouTube — 5 Schritte

1. https://console.cloud.google.com öffnen (mit leanstechgmbh@gmail.com) →
   oben „Projekt erstellen" (Name egal, z. B. „leans-social")
2. Menü „APIs & Dienste → Bibliothek" → **„YouTube Data API v3"** suchen → **Aktivieren**
3. „APIs & Dienste → OAuth-Zustimmungsbildschirm" → Extern → App-Name egal →
   deine Gmail eintragen → speichern.
   **Wichtig:** danach auf **„App veröffentlichen"** klicken (Status „In Produktion") —
   sonst läuft der Zugang alle 7 Tage ab.
4. „APIs & Dienste → Anmeldedaten" → „Anmeldedaten erstellen → OAuth-Client-ID" →
   Typ **„Desktop-App"** → erstellen → **Client-ID** und **Clientschlüssel** kopieren
5. Am eigenen PC (einmalig) ausführen:
   ```
   python tools/youtube_token.py CLIENT_ID CLIENTSCHLUESSEL
   ```
   Browser geht auf → mit dem YouTube-Konto anmelden → zustimmen.
   Das Skript druckt die 3 fertigen Zeilen (`YT_CLIENT_ID`, `YT_CLIENT_SECRET`,
   `YT_REFRESH_TOKEN`).

---

## Teil 3: Schlüssel in Cloud Run eintragen

1. https://console.cloud.google.com/run → Service anklicken →
   „Bearbeiten und neue Revision bereitstellen"
2. Unter „Variablen und Secrets" diese 5 Variablen anlegen:

| Variable | Wert aus |
|----------|----------|
| `META_ACCESS_TOKEN` | Teil 1, Schritt 4.1 |
| `IG_USER_ID` | Teil 1, Schritt 4.2 |
| `YT_CLIENT_ID` | Teil 2, Schritt 5 |
| `YT_CLIENT_SECRET` | Teil 2, Schritt 5 |
| `YT_REFRESH_TOKEN` | Teil 2, Schritt 5 |

3. „Bereitstellen" klicken. Fertig.

**Kontrolle:** Die Startseite des Service (`/`) zeigt danach
`"instagram": true, "youtube": true`.

---

## Teil 4: Posten (macht danach Claude oder n8n für dich)

```
curl -X POST https://DEIN-SERVICE.run.app/post-social \
  -H "Content-Type: application/json" \
  -H "X-Genesis-Key: DEIN_GENESIS_KEY" \
  -d '{
    "video_url": "https://.../video.mp4",
    "caption": "Text unterm Reel #klima #berlin",
    "title": "YouTube-Titel"
  }'
```

- `video_url` muss eine öffentliche Video-URL sein (z. B. der Higgsfield-Link) —
  Instagram lädt das Video direkt von dort, YouTube bekommt es vom Service hochgeladen.
- Hochkant-Videos unter 3 Minuten werden bei YouTube automatisch **Shorts**.
- Antwort enthält die fertigen Links zum Reel und zum YouTube-Video.
- Nur eine Plattform? `"platforms": ["instagram"]` bzw. `["youtube"]` mitgeben.

**Hinweis Facebook:** Reels zusätzlich auf die Facebook-Seite zu posten geht mit
demselben Meta-Token — sag Bescheid, dann baue ich das als dritte Plattform dazu.

---

## Teil 5: Posten per Zuruf — „poste Video 6"

Die fertigen Posts (Video-Link + Caption + Hashtags + YouTube-Titel) stehen in
**`posts.json`**. Damit gibt es zwei ganz einfache Wege:

**1. In Slack** (an den GENESIS-Bot, als DM oder @mention):
```
poste Video 6
```
Der Bot postet das Video auf Instagram + YouTube und antwortet mit den Links.

**2. Per API** (für Claude/n8n):
```
curl -X POST https://DEIN-SERVICE.run.app/post-video \
  -H "Content-Type: application/json" -H "X-Genesis-Key: DEIN_KEY" \
  -d '{"video": 6}'
```

`GET /posts` listet alle vorbereiteten Posts. Neue Videos = neuer Eintrag in
`posts.json` (macht Claude auf Zuruf mit fertigem Text).
