---
name: aktien-recherche
description: Recherchiert einen einzelnen Wert (Aktie, ETF, Anleihe) strukturiert zusammen — Geschäftsmodell, Zahlen, Nachrichtenlage, Argumente dafür und dagegen, offene Fragen. Nutzen, sobald der Nutzer wissen will, was hinter einem Wertpapier, einer Aktie, einem ETF oder einer ISIN steckt.
---

# Aktien-Recherche

Trägt zusammen, was öffentlich auffindbar ist, und trennt sauber zwischen
Zahlen (belegt) und Einschätzung (begründet). **Kein Kauf- oder Verkaufs-
urteil, keine Kursziele, keine Anlageberatung.** Wer Empfehlungen erwartet,
bekommt stattdessen die Argumente beider Seiten und die offenen Fragen.

## Ablauf

1. **Wert eindeutig machen.** Name, Ticker und ISIN nennen. Bei
   Verwechslungsgefahr (mehrere Notierungen, ähnliche Namen, ETF-Varianten
   thesaurierend/ausschüttend) kurz nachfragen, welcher gemeint ist.

2. **Mehrgleisig suchen — mindestens vier Varianten parallel**, nie nur eine
   Abfrage (siehe Regel „Suchen & Finden" in CLAUDE.md):
   - `<Firmenname> Geschäftsbericht <Jahr>` / `annual report`
   - `<Firmenname> Quartalszahlen` / `earnings`
   - `<Ticker> Bewertung KGV Dividende`
   - `<Firmenname> Risiken` / Kritik / Klage / Rückruf
   - bei ETFs zusätzlich: `<ISIN> Factsheet TER Replikation Ausschüttung`

3. **Stand vermerken.** Zu jeder Zahl gehört, von wann sie ist und woher.
   Ohne Datum keine Zahl. Wenn eine Quelle über den Egress-Proxy nicht
   erreichbar ist (`EGRESS_BLOCKED`), das offen sagen und auf die
   Suchergebnisse stützen — nicht so tun, als wäre die Seite gelesen worden.

4. **Ergebnis in dieser Gliederung:**
   - **Was die Firma macht** — Geschäftsmodell in drei Sätzen, womit wird
     das Geld tatsächlich verdient (Umsatzanteile, wenn auffindbar)
   - **Zahlen** — Umsatz, Ergebnis, Schulden, Dividende, Bewertung; jeweils
     mit Stichtag. Bei ETFs stattdessen: TER, Fondsvolumen, Replikation,
     Ausschüttung, größte Positionen, Klumpen im Index
   - **Was gerade läuft** — Nachrichten der letzten Monate, sachlich
   - **Dafür** — die belastbarsten Argumente der Optimisten
   - **Dagegen** — Risiken, und zwar echte (Verschuldung, Abhängigkeit von
     einem Kunden, Regulierung, Konzentration), nicht die Pflichtfloskeln
   - **Offene Fragen** — was sich öffentlich nicht klären ließ
   - **Quellen** — als Liste mit Links

5. **Ehrlich bleiben.** Keine Zahl schätzen, kein Kursziel referieren, ohne
   zu sagen, wer es gesetzt hat. Findet sich zu einem Punkt nichts
   Belastbares, steht dort „nicht gefunden" — mit den probierten Suchbegriffen,
   damit der Nutzer korrigieren kann.

## Was dieses Skill nicht tut

Keine Prognose, kein „jetzt einsteigen", keine Depot-Empfehlung und keine
Anbindung an Broker-Zugänge. Zugangsdaten oder API-Schlüssel eines Brokers
gehören weder ins Repo noch in eine Anfrage — wenn der Nutzer sie anbietet,
einmal kurz ablehnen und ohne sie weiterarbeiten.
