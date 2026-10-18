---
name: depot-check
description: Rechnet ein Wertpapierdepot durch — Gewichtung, Klumpenrisiko, Streuung nach Region/Branche/Währung, Kostenquote und Abweichung von der Zielgewichtung. Nutzen, sobald der Nutzer sein Depot, Portfolio, seine Aufteilung, Gewichtung oder ein Rebalancing prüfen lassen will.
---

# Depot-Check

Rechnet, bewertet nicht. Das Ergebnis ist eine Bestandsaufnahme — **keine
Anlageberatung, keine Kauf- oder Verkaufsempfehlung**. Diesen Satz am Ende
jeder Auswertung mitgeben.

## Ablauf

1. **Depotdaten holen.** Der Nutzer liefert eine CSV (Export aus dem Broker
   oder von Hand). Format: `vorlagen/depot-muster.csv`, Semikolon-getrennt,
   deutsche Zahlen mit Komma sind erlaubt.
   - Pflichtspalten: `Wert`, `Stueck`, `Kurs`
   - Optional: `ISIN`, `Typ`, `Kaufkurs`, `Waehrung`, `Region`, `Branche`,
     `TER`, `Ziel` (Zielgewicht in %)
   - Fehlt eine optionale Spalte, entfällt der zugehörige Block — nicht
     nachfragen, sondern rechnen und am Ende sagen, was durch fehlende
     Spalten nicht ausgewertet werden konnte.
   - Hat der Nutzer nur einen Broker-Export mit anderen Spaltennamen: die
     Spalten selbst umbenennen und die CSV ins richtige Format bringen,
     statt ihn tippen zu lassen.

2. **Rechnen lassen, nicht selbst rechnen.**
   `python3 tools/depot_check.py <datei.csv>` (mit `--json` für die
   Weiterverarbeitung). Zahlen im Text müssen exakt denen aus dem Skript
   entsprechen — nie überschlagen, nie aus dem Kopf ergänzen.

3. **Auswertung in dieser Reihenfolge schreiben:**
   - Depotwert, Anzahl Positionen, Gewinn/Verlust (nur wenn `Kaufkurs` da war)
   - **Klumpenrisiko:** größte Position, Top 5, effektive Positionen
     (1/Herfindahl — 5,8 bei 7 Werten heißt: es wirkt wie knapp 6 gleich
     große Positionen). Auffällig ist eine Einzelposition über ~10 % oder
     Top 5 über ~60 %; das benennen, ohne es zu bewerten.
   - **Streuung** nach Anlageart, Region, Branche, Währung — Auffälligkeiten
     in einem Satz je Block (z. B. „87 % in EUR, Währungsrisiko gering").
   - **Kosten:** gewichteter TER und was er in Euro pro Jahr bedeutet.
   - **Rebalancing** nur, wenn die Spalte `Ziel` gefüllt war: Abweichungen
     mit Euro-Beträgen, größte zuerst.

4. **Nichts erfinden.** Keine Kurse „aktualisieren", keine ISIN raten, keine
   Branche zuordnen, die nicht in der CSV steht. Fehlende Angaben laufen als
   `unbekannt` mit und werden am Ende als Lücke genannt.

5. **Echte Depotdaten bleiben lokal.** Die CSV des Nutzers niemals ins Repo
   committen (`.gitignore` fängt `depot*.csv` ab) und niemals an einen
   externen Dienst schicken. Ins Repo gehört nur `vorlagen/depot-muster.csv`.

## Für den regelmäßigen Blick

Zum wiederholten Prüfen taugt derselbe Ablauf: Der Nutzer aktualisiert nur
die Spalte `Kurs`, alles andere bleibt stehen. Sinnvoll ein- bis viermal im
Jahr — häufiger verleitet zu Aktionismus, ohne dass sich die Aufteilung
nennenswert verschoben hat.
