# Herkunft der Skills in diesem Ordner

## Eigene Skills

| Skill | Herkunft |
|---|---|
| `rechnung` | Eigenentwicklung LEANS Tech GmbH |

## Übernommen aus ECC

Vier Skills stammen aus dem Open-Source-Projekt **ECC** von Affaan Mustafa
(https://github.com/affaan-m/ECC), übernommen am 16.08.2026 aus Version 2.2.0.

| Skill | Wofür wir sie nutzen |
|---|---|
| `fastapi-patterns` | `main.py` — Endpunkte, Pydantic-Schemas, async, Tests |
| `python-testing` | pytest-Tests für `dwg_core.py` (bisher gibt es keine) |
| `docker-patterns` | `Dockerfile` / `docker-compose.yml`, Cloud-Run-Image |
| `error-handling` | Fehlerbehandlung bei DWG↔DXF-Konvertierung, Retries |

### Was bewusst NICHT übernommen wurde

ECC bringt insgesamt 285 Skills, 68 Agents, 94 Befehle und 4 Hooks mit
(3.488 Dateien, 93 MB). Übernommen wurden **nur die vier Markdown-Dateien
oben** — rund 55 KB reiner Text.

Nicht übernommen und ausdrücklich nicht erwünscht:

- **Hooks** — ECC hängt sich bei jedem Bash-Befehl und jeder Dateiänderung
  mit Node-Skripten dazwischen. Fremder Code, der bei jeder Aktion mitläuft.
- **Skripte, `install.sh`, npm-Pakete, AgentShield** — nichts Ausführbares.
- **Eigene `CLAUDE.md` und Regelwerke** von ECC — würden mit unseren
  Vorgaben kollidieren (Deutschpflicht, Rechnungsmuster, Freigabe-Workflow).
- **Die übrigen 281 Skills** — Android, Flutter, Blender, ClickHouse, DeFi,
  Cisco-Router, Marketing. Ohne Bezug zu diesem Projekt.

Aus `docker-patterns` wurde zusätzlich der Abschnitt „Hardened CLI Installer
Harnesses" entfernt, weil er sich auf ECC-eigene Test-Infrastruktur bezieht,
die wir nicht haben.

### Aktualisieren

Die Dateien sind eingefrorene Kopien und aktualisieren sich nicht von selbst.
Das ist Absicht: So ändert sich nichts an unserem Verhalten, ohne dass jemand
draufgeschaut hat. Wer aktualisieren will, holt die neue Fassung einzeln aus
dem ECC-Repo, liest den Unterschied durch und ersetzt die Datei.

### Lizenz

```
MIT License

Copyright (c) 2026 Affaan Mustafa

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
