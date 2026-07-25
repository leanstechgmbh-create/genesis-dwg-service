# Vault-Struktur — LEANS Tech GmbH

Aufbau so gewählt, dass der Graph von selbst Cluster bildet: wenige
Ordner, viel Verlinkung.

```
LEANS-Vault/
├─ 00-Start.md                 ← Einstiegsseite, verlinkt alles
├─ 10-Projekte/                ← ein Ordner je Bauvorhaben
│   └─ Mehringdamm 44-46.md
├─ 20-Kunden/
│   └─ SP Construct.md
├─ 30-Rechnungen/
│   └─ 2026-40 - 2. AR SP Construct.md
├─ 40-Angebote/
│   └─ Angebot 301 - Mehringdamm.md
├─ 50-Wartung/
│   └─ Wartungsvertrag <Kunde>.md
├─ 60-Notizen/                 ← Baustellenberichte, Telefonate, Ideen
├─ 90-Vorlagen/                ← Inhalt aus vorlagen/ hierher kopieren
└─ .obsidian/snippets/leans-kosmos.css
```

## Tags

Sparsam einsetzen, sonst wird der Graph unlesbar:

- `#offen` — offener Punkt, muss noch erledigt werden
- `#gestellt` — Rechnung raus, Geld steht aus
- `#bezahlt` — erledigt
- `#klima` `#heizung` `#lueftung` `#sanitaer` — Gewerk
- `#13b` — Reverse Charge (Bauleistung)

## Verlinkungsregeln (wichtig für den Graph)

1. Jede Rechnung verlinkt **Projekt** und **Kunde**:
   `Betrifft: [[Mehringdamm 44-46]] · [[SP Construct]]`
2. Jedes Projekt verlinkt seinen Kunden und listet Rechnungen/Angebote.
3. Kundenkarte verlinkt alle Projekte.
4. Baustellennotizen verlinken das Projekt.

Erst dadurch entstehen die Linien zwischen den Punkten — genau das, was
im Video den Netz-Effekt macht.

## Bezug zu Google Drive

Der Vault ersetzt die Ablage nicht. Ablage bleibt Google Drive
(„GBrain", Projektordner, „03 Rechnungen LEANS"). Die Obsidian-Notiz ist
die Übersichtskarte und verweist per Link auf die Datei im Drive —
Freigabe-Workflow und Namenskonvention bleiben unverändert.
