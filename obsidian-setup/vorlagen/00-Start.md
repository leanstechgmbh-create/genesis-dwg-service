# LEANS Tech — Zentrale

> Startseite des Vaults. Von hier gehen alle Linien aus — je mehr hier
> verlinkt ist, desto dichter wird der Graph.

## Aktive Baustellen

- [[Beispielstr. 12]]

## Kunden

- [[Muster Bau GmbH]]

## Offene Punkte

```dataview
TASK
FROM #offen
WHERE !completed
GROUP BY file.link
```

## Rechnungen — noch offen

```dataview
TABLE nummer AS "Nr.", netto AS "Netto", faellig AS "Fällig"
FROM "30-Rechnungen"
WHERE status = "gestellt"
SORT faellig ASC
```

## Angebote in Prüfung

```dataview
TABLE nummer AS "Nr.", netto AS "Netto", gueltig_bis AS "Gültig bis"
FROM "40-Angebote"
WHERE status = "offen"
SORT gueltig_bis ASC
```

## Wartung — nächste Termine

```dataview
TABLE kunde, anlage, naechster_termin AS "Termin"
FROM "50-Wartung"
SORT naechster_termin ASC
```

---

Die Dataview-Blöcke brauchen das Plugin **Dataview**. Ohne das Plugin
werden sie als grauer Codeblock angezeigt — stört nicht, bleibt nur leer.
