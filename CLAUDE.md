# CLAUDE.md

## Sprache / Language

**Immer auf Deutsch antworten.** Alle Antworten an den Nutzer ausschließlich
auf Deutsch verfassen — niemals auf Englisch, auch nicht teilweise. Das gilt
für getippte Eingaben genauso wie für Spracheingabe (Voice).

Ausnahme: Code, Befehle, Dateinamen, Logs und technische Bezeichner bleiben
unverändert (werden nicht übersetzt).

## Projekt

`genesis-dwg-service` — Python/FastAPI-Backend, das DWG/DXF-Dateien entgegennimmt,
kleine Änderungen vornimmt (verschieben/ergänzen/löschen via LibreDWG) und wieder
als DWG ausgibt. Läuft als Google Cloud Run Service, angebunden an n8n (Formular-Upload)
und einen Slack-Bot.

- `main.py` — FastAPI-App, HTTP-Endpunkte (`/`, `/modify-dwg`)
- `dwg_core.py` — Kernlogik (DWG<->DXF-Konvertierung, Änderungen)
- `slack_bot.py` — Slack-Bot (Chat + Plan-Bearbeitung, Claude-gestützt)
- `START_HIER.md` — Deploy-Anleitung (Google Cloud Run)

## Rechnungen & Angebote — Layout (WICHTIG)

Rechnungen und Angebote **immer im bestehenden LEANS-Tech-Layout** erstellen —
so wie die bisherigen Dokumente aussehen. **Kein eigenes/neues Design.**

- **Vorlage/Referenz:** die bereits vorhandenen PDFs in Google Drive, z. B.
  Rechnungen „Rechnung 2026-37", „Rechnung 2026-38" und Angebote „Angebot 301"
  (Ordner „Mehringdamm 44-46" bzw. die jeweiligen Kundenordner).
- Vor dem Erstellen die **alte Vorlage heranziehen** und Aufbau 1:1 übernehmen:
  Kopf (LEANS Tech GmbH, Semir Redzic, Berlepschstr. 165, 14165 Berlin),
  Empfängerblock, Rechnungs-/Angebotsnummer, Datum, Positions-Tabelle,
  Netto/USt/Gesamt, § 13b-Hinweis (Steuerschuldnerschaft Leistungsempfänger),
  Fußzeile mit HRB 249080 B, USt-IdNr. DE357948720 und Bankverbindung.
- Absender für Kundenmails ist **info@leanstech-gmbh.de**.
