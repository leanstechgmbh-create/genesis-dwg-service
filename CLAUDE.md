# CLAUDE.md

## Sprache / Language

**Immer auf Deutsch antworten.** Alle Antworten an den Nutzer ausschließlich
auf Deutsch verfassen — niemals auf Englisch, auch nicht teilweise. Das gilt
für getippte Eingaben genauso wie für Spracheingabe (Voice).

Ausnahme: Code, Befehle, Dateinamen, Logs und technische Bezeichner bleiben
unverändert (werden nicht übersetzt).

**Überschriften/Titel passend zum Inhalt.** Chat-Titel, Sitzungs-Titel und
Überschriften in Antworten immer auf Deutsch formulieren und so wählen, dass
sie das tatsächliche Thema des Inhalts wiedergeben — keine generischen oder
englischen Titel. Das gilt auch für den Slack-Bot: Jede Bot-Antwort beginnt
mit einer kurzen, fetten Überschrift zum Thema der Antwort.

## Projekt

`genesis-dwg-service` — Python/FastAPI-Backend, das DWG/DXF-Dateien entgegennimmt,
kleine Änderungen vornimmt (verschieben/ergänzen/löschen via LibreDWG) und wieder
als DWG ausgibt. Läuft als Google Cloud Run Service, angebunden an n8n (Formular-Upload)
und einen Slack-Bot.

- `main.py` — FastAPI-App, HTTP-Endpunkte (`/`, `/modify-dwg`)
- `dwg_core.py` — Kernlogik (DWG<->DXF-Konvertierung, Änderungen)
- `slack_bot.py` — Slack-Bot (Chat + Plan-Bearbeitung, Claude-gestützt)
- `START_HIER.md` — Deploy-Anleitung (Google Cloud Run)
