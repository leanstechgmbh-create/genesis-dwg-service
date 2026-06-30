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

## Hinweise

- **Status `muster`** in der CSV bedeutet: E-Mail-Adresse nach Traeger-Schema
  gebildet, nicht 100% bestaetigt — kann selten abprallen (Bounce). Die
  Unzustellbarkeits-Mail landet dann im Gmail-Posteingang.
- Werbe-E-Mails an Unternehmen unterliegen rechtlichen Vorgaben (UWG/DSGVO).
  Versand erfolgt in eigener Verantwortung.
- `sent_log.csv` enthaelt Versanddaten und ist per `.gitignore` ausgeschlossen.
