# Senior-Plugin (Everything Claude Code) — Anleitung

Stand: 05.08.2026 · Eingerichtet auf dem PC von Semir (Windows, PowerShell).

Das im Instagram-Guide („Senior") beworbene Plugin ist das kostenlose
Open-Source-Projekt **Everything Claude Code (ECC)**:
<https://github.com/affaan-m/ECC> (alias `everything-claude-code`,
vom Gewinner eines Anthropic-Hackathons). Es bringt ~94 Slash-Commands,
Skills, Agents und Hooks in den lokal installierten Claude Code.

## Status

- ✅ Auf dem PC installiert und aktiv (05.08.2026). `/plan` erscheint
  in der Befehlsliste.
- ℹ️ In Cloud-Sitzungen (claude.ai/code, Handy, Slack-Bot) ist das Plugin
  NICHT installiert und dort auch nicht nötig — im Chat einfach normal
  auf Deutsch beschreiben, was gewünscht ist.

## Installation (nur einmal nötig — bereits erledigt)

1. PowerShell öffnen (Windows-Taste → „PowerShell" → Enter)
2. `claude` eintippen → Enter (Claude Code startet)
3. In Claude Code nacheinander:

   ```
   /plugin marketplace add https://github.com/affaan-m/ECC
   /plugin install ecc@ecc
   ```

4. Claude Code neu starten (`/exit`, dann wieder `claude`)
5. Test: `/plan` tippen — erscheint der Befehl in der Liste, ist alles aktiv.

**Wichtig:** Keinen zweiten Installationsweg mischen (kein `install.sh` /
`install.ps1` zusätzlich ausführen) — sonst gibt es doppelte Befehle.

## Die drei Kern-Commands (am PC)

| Wann | Befehl | Was passiert |
|---|---|---|
| Vor einer größeren Aufgabe | `/plan <Beschreibung>` | Anforderungen zusammenfassen, Risiken nennen, Schritt-Plan zeigen — **wartet auf Bestätigung**, bevor Code angefasst wird |
| Nach getaner Arbeit | `/code-review` | Strenges Review der lokalen Änderungen; mit PR-Nummer/URL wird stattdessen der GitHub-PR geprüft |
| Wenn etwas nicht baut/startet | `/build-fix` | Erkennt das Build-System, findet und behebt Fehler in kleinen, sicheren Schritten |

Beispiel:

```
/plan Baue in mein Projekt eine Funktion, die hochgeladene DWG-Dateien
automatisch in einen Unterordner "eingang" sortiert
```

Weitere nützliche Commands: `/plan-prd` (erst Produkt-Kurzkonzept, dann
Plan), `/feature-dev` (geführte Feature-Entwicklung), `/test-coverage`
(Testlücken finden und schließen), `/security-scan`, `/python-review`.
Komplette Liste im Repo: `COMMANDS-QUICK-REF.md`.

## Bedienungs-Grundlagen (Merkzettel)

- Es gibt **ein** Eingabefeld (die Zeile mit `>` unten) — Befehle beginnen
  mit `/`, alles andere ist normale Unterhaltung.
- Nach `/` klappt die Befehlsliste auf; Weitertippen filtert sie.
  **Esc** schließt die Liste, ohne etwas auszuführen (Enter führt den
  markierten Eintrag sofort aus!).
- Claude Code immer **im Projektordner** starten: in PowerShell erst
  `cd C:\Pfad\zum\Projekt`, dann `claude`.
- **PC-Fenster** = `/`-Befehle für lokale Projekte (auch LEANS-OS).
  **Cloud-Chat** = normale Sätze; dort gibt es `/plan` & Co. nicht
  (Meldung „isn't available in this environment" ist dann normal).

## Optionaler Feinschliff (noch offen)

Regel-Pakete lassen sich per Plugin nicht mitliefern. Bei Bedarf am PC
diesen Prompt als normale Nachricht in Claude Code einfügen:

> Richte das frisch installierte ECC-Plugin fertig ein: Klone
> https://github.com/affaan-m/ECC in einen Temp-Ordner und kopiere daraus
> die Regel-Pakete `rules/common` und `rules/python` nach
> `~/.claude/rules/ecc/`. Erkläre mir danach kurz auf Deutsch, wie ich
> `/plan`, `/code-review` und `/build-fix` im Alltag einsetze.

## Hintergrund zum Instagram-Funnel

Der Link `sk.sandan.ai/funnel/senior` (sandan AI GmbH, Waiblingen) ist eine
Marketing-Landingpage zu genau diesem frei verfügbaren Plugin — es muss
nichts gekauft und keine E-Mail-Adresse abgegeben werden. Ähnlich klingende,
aber andere Projekte: `faizanmohiuddin482/bullpen` („The senior dev,
unbundled", 10 Skills) und `the-senior-dev/senior-dev-skills` (React-lastig).
