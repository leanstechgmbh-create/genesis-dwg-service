# Mailversand über sr@leanstech-gmbh.de einrichten

Damit kann Claude fertige Mails **als Entwurf direkt in das Postfach sr@ legen**
— mit Anhängen (Rechnungen, Angebote, Behördenpost). Der Entwurf erscheint in
Outlook/Webmail unter „Entwürfe", wird geprüft und von Hand abgeschickt.
Es geht nichts ohne Freigabe raus.

Gebraucht wird nur **das Passwort des Postfachs sr@leanstech-gmbh.de** — das
gleiche, mit dem sich das Mailprogramm anmeldet.

---

## Schritt 1 — Passwort in Cloud Run hinterlegen (ohne Terminal)

1. Browser öffnen: <https://console.cloud.google.com/run>
2. Oben links prüfen, dass das Projekt **leans-social** ausgewählt ist.
3. In der Liste auf den Dienst **genesis-dwg-service** klicken.
4. Oben auf **NEUE ÜBERARBEITUNG BEARBEITEN UND BEREITSTELLEN** klicken.
5. Reiter **Variablen und Secrets** anklicken.
6. Auf **VARIABLE HINZUFÜGEN** klicken und eintragen:

   | Name | Wert |
   |------|------|
   | `IONOS_MAIL_USER` | `sr@leanstech-gmbh.de` |
   | `IONOS_MAIL_PASSWORT` | *(Passwort des Postfachs sr@)* |

   Für jede Zeile einmal **VARIABLE HINZUFÜGEN** klicken.
7. Unten auf **BEREITSTELLEN** klicken und warten, bis der grüne Haken kommt
   (etwa 1 Minute — es wird nur neu gestartet, nicht neu gebaut).

## Schritt 2 — Prüfen, ob es angekommen ist

Im Browser aufrufen:

```
https://genesis-dwg-service-24363325360.europe-west3.run.app/
```

In der Antwort muss stehen: `"sr_mail": true`.
Steht dort `false`, fehlt noch eine der beiden Variablen aus Schritt 1.

---

## Was danach möglich ist

### Entwurf ablegen (Normalfall — es wird nichts verschickt)

```
POST /mail/entwurf
Header: x-genesis-key: <GENESIS_API_KEY>
{
  "betreff": "Rechnung 2026-41 - LEANS Tech GmbH",
  "text":    "Sehr geehrte Damen und Herren,\n\nanbei die Rechnung.\n",
  "an":      "kunde@example.de",
  "anhaenge": [
    {"dateiname": "Rechnung.pdf", "inhalt_base64": "JVBERi0xLjQ..."}
  ]
}
```

Antwort: `{"status": "entwurf_abgelegt", "ordner": "Entwürfe", ...}`

Das Feld `an` darf leer bleiben — dann wird die Adresse im Postfach eingetragen.
Mit `antwort_auf` (Message-ID der Ursprungsmail) hängt sich der Entwurf an den
richtigen Mailverlauf.

### Direkt senden (nur nach ausdrücklicher Freigabe)

```
POST /mail/senden
```

Gleicher Aufbau, `an` ist Pflicht. Eine Kopie landet automatisch im Ordner
„Gesendet".

### Ohne Server, direkt vom Rechner

```bash
python3 tools/mail_entwurf.py \
    --betreff "Nutzerkonto Transparenzregister - LEANS Tech GmbH" \
    --text-datei mailtext.txt \
    --anhang Berechtigungsnachweis.pdf \
    --anhang Gesellschafterliste.pdf
```

Dafür müssen `IONOS_MAIL_USER` und `IONOS_MAIL_PASSWORT` in der Shell gesetzt
sein (oder in einer lokalen `.env` stehen).

---

## Technische Eckdaten

| | |
|---|---|
| SMTP (Versand) | `smtp.ionos.de`, Port 465, SSL |
| IMAP (Entwürfe/Kopien) | `imap.ionos.de`, Port 993, SSL |
| Code | `mailer/ionos.py`, Endpunkte in `main.py` |
| Ordnersuche | erst über das IMAP-Kennzeichen `\Drafts` / `\Sent`, sonst über die Ordnernamen (`Drafts`, `Entwürfe`, `Sent`, `Gesendet`, …) |

Das Passwort steht **nur** in den Cloud-Run-Variablen, nie im Repository.
