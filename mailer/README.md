# Klima-Anschreiben-Versender

Verschickt das Klimaanlagen-Anschreiben per **Gmail-SMTP** von `leanstechgmbh@gmail.com`
an die Pflegeeinrichtungen aus `recipients.csv`. Reine Python-Standardbibliothek,
keine zusaetzlichen Pakete noetig.

## Dateien

| Datei               | Zweck                                                        |
|---------------------|-------------------------------------------------------------|
| `send_mails.py`     | Das Versand-Skript (CLI)                                     |
| `recipients.csv`    | Empfaengerliste (Einrichtung, E-Mail, Status)               |
| `email_vorlage.txt` | Text-Vorlage des Anschreibens (mit Platzhaltern)            |
| `sent_log.csv`      | Wird automatisch angelegt: Protokoll gegen Doppelversand    |

## 1. Gmail vorbereiten (einmalig)

Gmail erlaubt SMTP-Versand nur mit einem **App-Passwort** (nicht dem normalen Passwort):

1. Google-Konto -> **Sicherheit** -> **2-Schritt-Bestaetigung** aktivieren
2. Danach: **App-Passwoerter** -> neues Passwort erzeugen (16 Zeichen)
3. Dieses Passwort als Umgebungsvariable setzen:

```bash
export GMAIL_APP_PASSWORD="xxxxxxxxxxxxxxxx"
```

Optional ueberschreibbar (haben sinnvolle Standardwerte):
`GMAIL_USER`, `MAIL_ABSENDER`, `MAIL_FIRMA`, `MAIL_WEBSITE`.

## 2. Vorschau (verschickt nichts)

Ohne `--send` laeuft alles als **Dry-Run** — zeigt nur an, was gesendet wuerde:

```bash
python3 send_mails.py
```

## 3. Testmail an sich selbst

```bash
GMAIL_APP_PASSWORD=... python3 send_mails.py --test deine@adresse.de
```

## 4. Echter Versand

Empfehlung: in kleinen Wellen senden (Gmail-Tageslimit ~500, Spam-Schutz):

```bash
# Erste 10 senden, 30s Abstand
GMAIL_APP_PASSWORD=... python3 send_mails.py --send --limit 10 --delay 30

# Nur die sicher bestaetigten Adressen
GMAIL_APP_PASSWORD=... python3 send_mails.py --send --only-confirmed
```

Bereits versendete Adressen werden beim naechsten Lauf automatisch **uebersprungen**
(dank `sent_log.csv`). So kannst Du den Versand gefahrlos ueber mehrere Tage verteilen.

## Wichtige Optionen

| Option             | Wirkung                                                       |
|--------------------|--------------------------------------------------------------|
| `--send`           | Wirklich senden (sonst nur Vorschau)                         |
| `--test EMAIL`     | Eine Testmail an EMAIL senden und beenden                    |
| `--limit N`        | Hoechstens N Mails pro Lauf                                  |
| `--delay SEK`      | Pause zwischen den Mails (Standard 20s)                      |
| `--only-confirmed` | Nur Status `bestaetigt`                                      |
| `--status a,b`     | Nur bestimmte Status (z.B. `bestaetigt,zentral`)            |
| `--resend`         | Protokoll ignorieren und erneut senden                      |
| `--yes`            | Sicherheitsabfrage ueberspringen                            |

## Weg B: Server-Endpunkt (automatischer Versand ueber Cloud Run)

Statt lokal kann der Versand auch direkt vom laufenden `genesis-dwg-service`
ausgeloest werden — dann verschickt der Service, nicht Dein Laptop.

### Einrichtung

1. App-Passwort als **Secret/Umgebungsvariable** in Cloud Run hinterlegen:
   `GMAIL_APP_PASSWORD` (zusaetzlich optional `GMAIL_USER`, `MAIL_ABSENDER`,
   `MAIL_FIRMA`, `MAIL_WEBSITE`).
2. Zum Schutz `GENESIS_API_KEY` setzen — der Endpunkt verlangt dann den Header
   `X-Genesis-Key`.

Im Health-Check (`GET /`) zeigt `"mail_ready": true`, sobald ein App-Passwort gesetzt ist.

### Aufruf

`POST /send-mails` mit JSON-Body (alle Felder optional):

| Feld             | Typ   | Default | Wirkung                                  |
|------------------|-------|---------|------------------------------------------|
| `send`           | bool  | `false` | `true` = wirklich senden (sonst Vorschau)|
| `limit`          | int   | `0`     | hoechstens N Mails (0 = alle)            |
| `delay`          | float | `2`     | Sekunden Pause zwischen Mails            |
| `only_confirmed` | bool  | `false` | nur Status `bestaetigt`                  |
| `status`         | list  | –       | z.B. `["bestaetigt","zentral"]`          |
| `resend`         | bool  | `false` | Sende-Protokoll ignorieren               |

```bash
# Vorschau (sendet nichts)
curl -X POST https://<service-url>/send-mails \
  -H "X-Genesis-Key: $GENESIS_API_KEY" -H "Content-Type: application/json" \
  -d '{"limit": 5}'

# Erste 10 wirklich senden
curl -X POST https://<service-url>/send-mails \
  -H "X-Genesis-Key: $GENESIS_API_KEY" -H "Content-Type: application/json" \
  -d '{"send": true, "limit": 10, "delay": 5}'
```

Hinweis: Der Aufruf antwortet erst nach dem Versand. Bei grossen Mengen mit
`limit` arbeiten (z.B. per n8n-Zeitplan mehrfach aufrufen) — `delay * Anzahl`
sollte unter dem Cloud-Run-Timeout bleiben. Das Sende-Protokoll im Container
ist fluechtig; fuer dauerhaften Doppelversand-Schutz `limit`/`status` gezielt
einsetzen oder ein persistentes Volume anbinden.

## Hinweise

- **Status `muster`** in der CSV bedeutet: E-Mail-Adresse nach Traeger-Schema
  gebildet, nicht 100% bestaetigt — kann selten abprallen (Bounce). Die
  Unzustellbarkeits-Mail landet dann im Gmail-Posteingang.
- Werbe-E-Mails an Unternehmen unterliegen rechtlichen Vorgaben (UWG/DSGVO).
  Versand erfolgt in eigener Verantwortung.
- `sent_log.csv` enthaelt Versanddaten und ist per `.gitignore` ausgeschlossen.
