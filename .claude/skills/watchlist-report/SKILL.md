---
name: watchlist-report
description: Erstellt einen Überblick über die beobachteten Werte einer Watchlist — was sich seit dem letzten Bericht getan hat, gebündelt in einer lesbaren Übersicht. Nutzen, wenn der Nutzer einen Wochenbericht, Marktüberblick oder Report zu seiner Watchlist oder seinen beobachteten Aktien will.
---

# Watchlist-Report

Bündelt die Nachrichtenlage zu einer festen Liste von Werten, damit der
Nutzer nicht täglich Kurse schaut. **Keine Anlageberatung**, keine
Handlungsaufforderung — der Bericht sagt, was passiert ist, nicht, was zu
tun ist.

## Ablauf

1. **Watchlist lesen.** Standardliste: `vorlagen/watchlist-muster.txt`
   (eine Zeile je Wert: `Name;ISIN oder Ticker;Notiz`). Hat der Nutzer eine
   eigene Liste, diese nehmen — echte Listen nicht ins Repo committen.

2. **Je Wert kurz recherchieren**, alle Werte in einem Rutsch und die Suchen
   parallel absetzen, nicht nacheinander. Pro Wert reichen zwei bis drei
   Suchvarianten (Firmenname + Quartalszahlen, Firmenname + News, Ticker).
   Für einen einzelnen Wert in der Tiefe ist das Skill `aktien-recherche`
   zuständig — hier bleibt es bei drei bis fünf Sätzen je Position.

3. **Bericht aufbauen:**
   - **Kurzfassung oben** — die zwei, drei Dinge, die überhaupt der Rede
     wert sind. Ist nichts passiert, steht das genau so da: „Diese Woche
     nichts Wesentliches." Keine Meldung aufblasen, damit der Bericht
     voller aussieht.
   - **Je Wert** ein Block: was passiert ist, seit wann, Quelle
   - **Termine** — anstehende Quartalszahlen, Hauptversammlungen,
     Ex-Dividenden-Tage, soweit auffindbar
   - **Nicht gefunden** — zu welchen Werten es nichts gab

4. **Ausgeben.** Standard ist eine Antwort im Chat. Will der Nutzer es
   ansehnlich, den Bericht als Artifact veröffentlichen (vorher das Skill
   `artifact-design` laden) und ihm den Link geben.

5. **Wiederkehrend einrichten** — nur auf ausdrücklichen Wunsch: als Routine
   (`create_trigger`, z. B. montags 7:00 Berlin = `0 5 * * 1` in UTC) mit
   einer Anweisung, die für sich allein steht, weil jede Ausführung ohne
   Vorgeschichte startet.

## Regeln

- Jede Aussage mit Datum und Quelle. Kursbewegungen nur nennen, wenn eine
  Quelle sie belegt — keine Kurse aus dem Gedächtnis, die sind veraltet.
- Ist eine Quelle über den Egress-Proxy gesperrt (`EGRESS_BLOCKED`), das
  benennen statt zu raten.
- Keine Kauf-/Verkaufssignale, keine Prognosen, keine Kursziele ohne Angabe,
  wer sie aufgestellt hat.
