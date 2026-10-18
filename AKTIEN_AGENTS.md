# Aktien-Agents (Depot, Recherche, Watchlist)

Drei Skills für die eigenen Geldanlagen — als Ersatz für die Prompt-Pakete,
die auf Instagram als „Anthropic Finance Agents" beworben werden. Die
offiziellen Finance-Agents von Anthropic (Mai 2026) richten sich an Banken
und Asset-Manager und hängen an Bezahl-Datenquellen wie FactSet oder S&P
Capital IQ; für ein privates Depot ist das die falsche Größenordnung.

**Keines dieser Skills ist Anlageberatung.** Sie rechnen und tragen zusammen,
sie empfehlen nicht. Kein Skill braucht Broker-Zugänge, und keines soll
welche bekommen.

## Was drin ist

| Skill | Wofür | Aufruf |
|---|---|---|
| `depot-check` | Depot durchrechnen: Gewichtung, Klumpenrisiko, Streuung, Kosten, Rebalancing | „Prüf mal mein Depot" |
| `aktien-recherche` | Einzelner Wert: Geschäftsmodell, Zahlen, Nachrichten, Pro/Contra | „Was steckt hinter Siemens?" |
| `watchlist-report` | Überblick über die beobachteten Werte | „Mach mir den Wochenbericht" |

## Depot-Check von Hand

```bash
python3 tools/depot_check.py depot.csv          # lesbare Auswertung
python3 tools/depot_check.py depot.csv --json   # zum Weiterverarbeiten
```

Format der CSV: `vorlagen/depot-muster.csv`. Pflichtspalten sind `Wert`,
`Stueck` und `Kurs`; `ISIN`, `Typ`, `Kaufkurs`, `Waehrung`, `Region`,
`Branche`, `TER` und `Ziel` sind optional und schalten jeweils einen Block
der Auswertung frei. Deutsche Zahlen mit Komma funktionieren, Semikolon und
Komma als Trennzeichen ebenfalls.

Zwei Kennzahlen, die nicht selbsterklärend sind:

- **Effektive Positionen** (1/Herfindahl): Wie viele gleich große Positionen
  das Depot in seiner Wirkung hat. Sieben Werte, von denen zwei fast die
  Hälfte ausmachen, wirken wie knapp sechs — die Streuung ist also geringer,
  als die Anzahl vermuten lässt.
- **TER gewichtet**: Die Kostenquote über das gesamte Depot, nicht nur über
  den Fondsanteil. Aktien und Tagesgeld gehen mit 0 ein und drücken den Wert.

## Daten bleiben lokal

Echte Depot- und Watchlist-Dateien fängt die `.gitignore` ab (`depot*.csv`,
`watchlist.txt`). Im Repo liegen nur die Muster mit erfundenen Zahlen.
