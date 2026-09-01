# Superpowers-Plugin — Anleitung

Stand: 26.08.2026 · Version 6.3.0 · Quelle: offizieller Anthropic-Marktplatz
(`superpowers@claude-plugins-official`, Original: <https://github.com/obra/superpowers>)

Superpowers ist eine Skill-Bibliothek für Claude Code: Arbeitsweisen für
Planen, testgetriebene Entwicklung, systematisches Fehlersuchen und
Code-Review. Kein eigenes Konto, keine Schlüssel, kostenlos.

## Status

- ✅ Für dieses Repository eingetragen (`.claude/settings.json`, Abschnitt
  `enabledPlugins`) — gilt für alle, die hier arbeiten.
- ✅ In Cloud-Sitzungen aktiv (am 01.09.2026 in einem frischen Container geprüft,
  siehe unten).
- ⬜ Auf dem PC von Semir noch nicht installiert → zwei Befehle, siehe unten.
- ℹ️ **Kein Konflikt mit dem ECC-Plugin** (`SENIOR-PLUGIN-ANLEITUNG.md`):
  Superpowers bringt keine gleichnamigen Slash-Befehle mit, sondern 14 Skills,
  die Claude selbst zieht. `/plan`, `/code-review` & Co. von ECC bleiben wie sie sind.

## Installation am PC (einmalig, ~2 Minuten)

1. PowerShell öffnen (Windows-Taste → „PowerShell" → Enter)
2. `claude` eintippen → Enter
3. In Claude Code eingeben:

   ```
   /plugin install superpowers@claude-plugins-official
   ```

   Kommt die Meldung `Marketplace "claude-plugins-official" not found`, vorher
   einmal `/plugin marketplace add anthropics/claude-plugins-official` ausführen.

4. Steht in der Meldung „Run /reload-plugins to activate", dann `/reload-plugins`
   eingeben — sonst ist es schon aktiv.
5. Test: `/plugin list` → `superpowers@claude-plugins-official … enabled`

## Was drin ist (14 Skills)

| Skill | Wofür |
|---|---|
| `brainstorming` | Idee vor dem Bauen durchdenken, Varianten abwägen |
| `writing-plans` / `executing-plans` | Schrittplan schreiben und Schritt für Schritt abarbeiten |
| `test-driven-development` | Erst Test, dann Code — Fehler fallen vor dem Deploy auf |
| `systematic-debugging` | Fehler geordnet eingrenzen statt raten |
| `verification-before-completion` | Vor „fertig" nachweisen, dass es wirklich läuft |
| `requesting-code-review` / `receiving-code-review` | Review anfordern und Rückmeldungen sauber einarbeiten |
| `subagent-driven-development` | Größere Aufgaben auf Helfer-Agenten verteilen |
| `dispatching-parallel-agents` | Mehrere Teilaufgaben gleichzeitig laufen lassen |
| `using-git-worktrees` | Parallele Zweige ohne Durcheinander im Projektordner |
| `finishing-a-development-branch` | Branch sauber abschließen (Aufräumen, PR) |
| `using-superpowers` | Einstieg: welcher Skill passt gerade |
| `writing-skills` | Eigene Skills bauen (z. B. wie `.claude/skills/rechnung`) |

Dazu ein `SessionStart`-Hook (läuft im Hintergrund, kostet keinen Platz im Gespräch).

## Bedienung

Nichts auswendig lernen — normal auf Deutsch beschreiben, was Du willst.
Claude zieht den passenden Skill selbst. Beispiele:

- „Bevor Du das änderst, mach mir erst einen Plan."
- „Der Upload wirft seit gestern einen 500er — such den Fehler systematisch."
- „Schreib zuerst einen Test dafür, dann den Code."

## Was es kostet

Rund 688 Tokens sind in jeder Sitzung dauerhaft belegt (Beschreibung der
Skills). Erst wenn ein Skill wirklich anspringt, kommt sein Inhalt dazu
(je nach Skill 0,8k–12k Tokens). Kein Geld, nur Platz im Gesprächsspeicher.

## Wieder loswerden

Am PC: `/plugin uninstall superpowers@claude-plugins-official`.
Für das Repository: den Eintrag `superpowers@claude-plugins-official` aus
`.claude/settings.json` löschen.

## Cloud-Sitzungen (Web, Handy, Slack-Bot) — läuft

Am 26.08.2026 stand hier noch ein offener Punkt: Der Verdacht war, dass ein
frisch gestarteter Cloud-Container den Anthropic-Marktplatz nicht kennt und
`.claude/settings.json` deshalb zusätzlich einen `extraKnownMarketplaces`-Block
bräuchte.

**Gegenprobe am 01.09.2026 in einem Container, der zwei Minuten alt war:
nicht nötig.** `claude plugin list` meldete `superpowers@claude-plugins-official`
als installiert und aktiv (Scope: project), die 14 Skills standen in der
Skill-Liste der Sitzung. Der `enabledPlugins`-Eintrag allein genügt also —
die Cloud-Umgebung holt das Plugin beim Start selbst.

(Die frühere Gegenprobe lief mit der nackten Kommandozeile und einer leeren
Nutzerkonfiguration. Die bildet den Start einer Cloud-Sitzung nicht ab und
hat in die Irre geführt.)
