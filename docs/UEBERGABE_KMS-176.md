# Übergabe — Karl-Marx-Str. 176, Berlin (Heizen/Kühlen/Warmwasser)

Stand: 20.08.2026 · erstellt in einer Cloud-Sitzung von Claude Code
Zweck: nahtlose Fortsetzung in einem neuen Chat (insbesondere auf dem PC des Nutzers)

---

## 0. Was in dieser Sitzung passiert ist (Kurzverlauf)

1. **Hydraulikschema** als DXF gebaut und mehrfach korrigiert (`tools/hydraulikschema_wp.py`, PR #40, Draft).
   Zuerst mit falschen Annahmen (12 × 16 kW), dann anhand der Typenschild-Fotos auf die echten
   Geräte umgestellt, zuletzt auf **Systemtrennung über Wärmetauscher** und **20 Verbraucher**.
   Das Schema ist noch nicht final — es fehlen die offenen Punkte aus Abschnitt 7.
2. **Fachliche Klärung** zu Kühlbetrieb, Kaltwassertemperatur, Kondensat, Dämmung und
   Kaskadenschaltung — Ergebnisse in den Abschnitten 4 bis 6.
3. **KONVEKA-Katalog** (DF2/DF4 2025) ausgewertet → belegte Leistungsdaten der Fancoils.
4. **Ausführungsplan** `KMS_AP_GESAMT_04.03.26` (8 Blätter) ausgelesen und mit Raster versehen.
5. **Drive-Projektordner** „Karl-Marx-Straße 176" angelegt (Struktur siehe Abschnitt 8).
6. **Neue Dauerregel in CLAUDE.md:** Pläne immer mit beschriftetem Gitternetz ausgeben.
7. **Nicht möglich in der Cloud-Sitzung:** Paint auf dem Rechner des Nutzers öffnen — deshalb diese Übergabe.

---

## 1. Projekt

| | |
|---|---|
| Bauvorhaben | Instandsetzung, Erweiterung und Umnutzung, **Karl-Marx-Str. 176, 12043 Berlin** |
| Bauherr | **Colak VVI GmbH**, vertr. durch Ètienne Colak, Rudolf-Diesel-Str. 33, 56220 Urmitz |
| Architekt | GKM architektur studio, Nützenberger Str. 61, 42115 Wuppertal — M.Sc. Dipl.-Ing. M. Groß |
| Planstand | Ausführungsplanung, Zeich.-Nr. 0424_VVI_LPH1_4_A-22.x, Index I vom 04.03.2026, M 1:50 |
| Planblätter | 8 Stück: KG, EG, 1.–5. OG, Blatt 8 |
| Gebäudeteile | Vorderhaus · Remise Seitenflügel · Remise Querhaus |
| Bauphysik | Außenwand 365–380 mm Mauerwerk + **60 mm Calciumsilikat-Innendämmung**, Calciumsilikat in allen Fensterleibungen, EG-Boden 6 cm Mineraldämmplatten |

**Hinweis:** Der Bauherr sitzt unter derselben Adresse wie SP Construct GmbH (Projekt Mehringdamm 44–46) — Rudolf-Diesel-Str. 33, Urmitz.

**Auftrag des Nutzers:** Angebot erstellen für Rohre, Umbau und **Dämmung**. Es wird nicht neu geplant — die Anlage existiert, es geht um Mengen und Kalkulation.

---

## 2. Anlagenaufbau (laut Nutzer + Eintragungen auf Blatt 1 KG)

Rasterfelder beziehen sich auf `KMS-176_Plaene_RASTER.pdf` (Blatt 1: A–E × 1–3).

- **9 Wärmepumpen** Midea MHC-V10W/D2N8-BER90, Aufstellung **außen** an der Grundstücksgrenze (**D2–D3**)
  - **6 Stück** für Heizen **und** Kühlen (Change-Over, reversibel)
  - **3 Stück** separat für Warmwasser
- Sammelleitung **DN54 Verbundrohr** (Vor- und Rücklauf) in den **Hausanschlussraum (C3, 17,94 m²)**
- Dort **3 Speicher** — Zuordnung noch offen; einer davon ist der Pufferspeicher **Austria Email PSM 800, 800 l**
- Von dort **DN54-Doppelleitung** ins **Seitenhaus** (Abgang bei **A1/B1**, handschriftlich „hier zum Seitenhaus")
- Im zweiten Heizungsraum: **PSM 500, 500 l**, von dort Verteilung ins Haus
- **Verbraucher: 20 × KONVEKA DF2 51**, Kanal-Gebläsekonvektoren (Ducted Fan Coils), **2-Leiter-Ausführung**
- **Stränge: Ø35, Ø28, Ø22**

---

## 3. Gerätedaten (belegt)

### Wärmepumpe Midea MHC-V10W/D2N8-BER90 (vom Typenschild)

| Parameter | Wert |
|---|---|
| Kühlen @ A35/W18 | **9,90 kW · EER 4,55** |
| Heizen @ A7/W35 | **10,00 kW · COP 4,95** |
| Leistungsaufnahme | 3.700 W (+ 9.000 W Heizstab IBH) |
| Spannung | 380–415 V 3N~ 50 Hz |
| Kältemittel | R32, 1.400 g · GWP 675 · 0,95 t CO₂-Äq. |
| Wasserdruck | 0,1–0,3 MPa · max. zul. 4,3 MPa (HD 4,3 / ND 2,6) |
| Gewicht / Schutzart | 110 kg · IP24 |
| Seriennummer (Beispielgerät) | 541N97654024402010052 |

### Pufferspeicher Austria Email PSM 800 (vom Typenschild)

| Parameter | Wert |
|---|---|
| Nenninhalt | 800 l |
| Zul. Betriebsüberdruck / Prüfdruck | 0,4 / 0,6 MPa |
| Zul. Betriebstemperatur | 95 °C |
| Max. Wärmeleistung | 150 kW |
| Wärmeverlust | 108 W (Eco Skin Vliesisolierung 100 mm) |
| Herstellnummer | 25100328A016 |
| **Achtung** | **Nicht für Trinkwasser geeignet. Eco-Skin-Vlies ist NICHT dampfdiffusionsdicht → im Kühlbetrieb kritisch.** |

### KONVEKA DF2 51 (Katalog „Ducted Fan Coils DF" 2025, S. 5 und 6)

Kühlen, Raum 27 °C, Drehzahl Maximum:

| Wassertemperatur | total | sensibel | Volumenstrom | Δp |
|---|---|---|---|---|
| 7/12 °C | 2.998 W | 2.099 W | 516 l/h | 15,4 kPa |
| 17/22 °C | 1.516 W | 1.061 W | 261 l/h | 11,9 kPa |

Heizen, Raum 20 °C, Maximum:

| Wassertemperatur | Leistung | Volumenstrom | Δp |
|---|---|---|---|
| 35/30 °C | 1.593 W | 274 l/h | 12,0 kPa |
| 45/40 °C | 3.024 W | 520 l/h | 15,5 kPa |

Weiteres: Luftmenge max. 550 m³/h · Schalldruck 39–44 dB(A) · Anschluss **G ¾"** · **Kondensat DN20** · max. Betriebsdruck 1,6 MPa · Maße 814 × 510 × 234 mm · 13 kg · Leistungsaufnahme AC 52–66 W, DC 30–38 W

---

## 4. Getroffene Entscheidungen

### Systemtrennung über Plattenwärmetauscher — vom Nutzer bestätigt

- **Primärkreis** (Wärmepumpen + Außenstrecke bis zum Wärmetauscher): Wasser/Glykol **ca. 30 %**
- **Sekundärkreis** (gesamtes Gebäude): **reines Heizungswasser nach VDI 2035, kein Glykol**
- Begründung: statt über 600 l nur rund **50–75 l Glykol**; Gebäudeseite bleibt glykolfrei
- Preis dafür: Grädigkeit 2–4 K → rund **7 % schlechterer COP bzw. EER**
- **Wärmetauscher auf den KÜHLFALL auslegen**, nicht auf den Heizfall (kleinere treibende Temperaturdifferenz)
- Zwei Wärmetauscher: einer für Heizen/Kühlen, einer für Warmwasser

---

## 5. Rechenergebnisse

### Kälteleistung der 20 Fancoils (Raum 27 °C, Stufe max)

Zwischen den Katalogpunkten interpoliert:

| Wasser | total je Gerät | sensibel je Gerät | 20 Geräte total | **20 Geräte sensibel** | l/h je Gerät |
|---|---|---|---|---|---|
| 17/22 °C | 1.516 W | 1.061 W | 30,3 kW | **21,2 kW** | 261 |
| 14/19 °C | 1.961 W | 1.372 W | 39,2 kW | **27,4 kW** | 338 |
| 10/15 °C | 2.553 W | 1.788 W | 51,1 kW | **35,8 kW** | 439 |
| 7/12 °C | 2.998 W | 2.099 W | 60,0 kW | **42,0 kW** | 516 |

**Für die Auslegung die sensible Spalte verwenden** — nur die senkt die Raumtemperatur.

### Leistungsabfall mit sinkender Raumtemperatur (bei 14/19 °C Wasser)

| Raumtemperatur | sensibel je Gerät | 20 Geräte |
|---|---|---|
| 27 °C | 1.372 W | 27,4 kW |
| 26 °C | 1.241 W | 24,8 kW |
| 25 °C | 1.111 W | 22,2 kW |
| 24 °C | 980 W | 19,6 kW |
| 23 °C | 849 W | 17,0 kW |

Mit 17 °C Vorlauf pendelt sich der Raum bei 35 °C außen realistisch bei **25–26 °C** ein; für 23–24 °C braucht es **14 °C**.

### Wärmepumpenseite

- 6 × 9,90 kW = **59,4 kW** Kälteleistung bei A35/W18
- mit Systemtrennung real **~55 kW**, EER ~4,2, Stromaufnahme ~13 kW
- **Die Wärmepumpen sind nicht der Engpass — die Fancoils sind es.**

### Taupunkt und Kondensat

Taupunkt bei Raum 27 °C: 40 % rF → 12,0 °C · 45 % → 13,9 °C · 50 % → 15,7 °C · 55 % → 17,4 °C · 60 % → 18,6 °C

Bei **14 °C Vorlauf** liegt die kälteste Lamellenstelle um 15 °C — bis ca. 45 % rF trocken, ab 50 % fällt Kondensat an. **Die Kondensatableitung muss voll gebaut werden.**

- Katalogpunkt (~46 % rF): **0,87 l/h je Gerät → 17 l/h** bei 20 Geräten
- Schwüler Tag (55 % rF): **~1,1 l/h je Gerät → ~21 l/h**
- Über 8 Betriebsstunden: 140–170 Liter am Tag

DN20 ist für die Menge weit überdimensioniert — kritisch sind **durchgängiges Gefälle, Siphon je Gerät und gedämmte Kondensatleitungen**.

### Dämmstärken (maßgebend ist der jeweils höhere Wert)

| Rohr | Innen-Ø | GEG Anl. 8 (Heizen) | Tauwasser 14 °C | Tauwasser 10 °C | maßgebend 14 °C | maßgebend 10 °C |
|---|---|---|---|---|---|---|
| Ø22×1,0 | 20 mm | 20 mm | 19 mm | 25 mm | **20 mm** | **25 mm** |
| Ø28×1,5 | 25 mm | 30 mm | 19 mm | 25 mm | **30 mm** | **30 mm** |
| Ø35×1,5 | 32 mm | 30 mm | 25 mm | 32 mm | **30 mm** | **32 mm** |

Tauwasser gerechnet für 30 °C / 80 % rF (Technikraum, Schacht), λ = 0,036, μ ≥ 7.000.

**Wichtig: Nicht die Kühlung treibt die Dicke, sondern das GEG für den Heizbetrieb** — das Material muss aber trotzdem geschlossenzellig und diffusionsdicht sein (Armaflex AF, Kaiflex ST), weil derselbe Strang auch kühlt.

**Praktische Empfehlung mit handelsüblichen Dicken (19/25/32 mm):**
**Ø22 → 25 mm · Ø28 → 32 mm · Ø35 → 32 mm.** Deckt GEG und Tauwasserschutz bis hinunter zu 10 °C in einer Ausführung ab.

Außendurchmesser mit Dämmung (Platzbedarf prüfen): Ø22+20 → 62 mm · Ø28+30 → 88 mm · Ø35+30 → 95 mm

### Strangbelegung (max. 0,8 m/s)

| Strang | bei 17 °C | bei 14 °C | bei 10 °C |
|---|---|---|---|
| Ø22 | 3 Geräte | **2 Geräte** | 2 Geräte |
| Ø28 | 5 Geräte | **4 Geräte** | 3 Geräte |
| Ø35 | 8 Geräte | **6 Geräte** | 5 Geräte |

**Das ist der kritische Punkt:** Von 17 auf 14 °C steigt der Volumenstrom um 30 %, auf 10 °C um 68 %. Die vorhandenen Stränge können die Kaltwassertemperatur nach unten begrenzen.

### Kaskade und Taktverhalten

- 6 WP à 10 kW, Modulation bis ca. 25–30 % → **~3 kW Mindestleistung je Gerät**
- PSM 800 fasst bei 5 K Spreizung 4,6 kWh → bei 3 kW Überschuss 1,5 h Ladezeit → **kein Takten**
- Im Winter läuft die Anlage ohnehin nahe Volllast; das Taktproblem liegt in der Übergangszeit und im Kühlbetrieb

**Zwingend einzuplanen:**
1. **Kaskadenregler** mit Führungsgeräte-Rotation nach Betriebsstunden, Hysterese, Mindestlaufzeit ~10 min, Mindeststillstand
2. **Je Wärmepumpe ein motorisches Zonenventil im Rücklauf** (6 Stück, DN32/40 + Verkabelung) — ohne das strömt bei einem laufenden Gerät das Wasser über die fünf stehenden zurück (Kurzschlussströmung), das laufende Gerät erreicht seinen Mindestvolumenstrom nicht und geht auf Störung. **Wird häufig vergessen.**

---

## 6. Empfehlung für das Angebot

**Auslegen auf 14 °C, im Regelbetrieb 16–17 °C fahren, gleitend nach Taupunkt.**

Dämmung, Kondensatableitung und Rohrquerschnitte für 14 °C bauen — das ist der teure Teil und wird nur einmal gemacht. Im Normalbetrieb läuft die Anlage bei 16–17 °C trocken und effizient; bei Hitze geht der Regler auf 14 °C und liefert 27 kW statt 21 kW sensibel.

**In die Mengenermittlung gehören:**
- Laufende Meter je Dimension, **getrennt nach VL und RL** (doppelte Länge)
- **25–40 % Aufschlag** für Bögen, T-Stücke, Armaturen, Verschraubungen (Dämmkappen/Formteile als Stückpositionen)
- **Kälteschellen** (Druckfest-Dämmschalen) — ca. 1 Stück je 1,5–2 m waagerecht, je Geschoss senkrecht
- Kleber ca. 1 l je 25–30 m² Dämmoberfläche, Stöße durchgehend kaltverklebt
- **Die 20 Anbindeleitungen** (G ¾") inkl. Ventile und Verschraubungen am Gerät
- **Kondensatleitungen gedämmt**, mit Gefälle; wo kein Gefälle möglich ist, Kondensatpumpe
- Ggf. Einhausung oder Umfahrung des PSM 800 im Kühlbetrieb (Eco-Skin nicht diffusionsdicht)

---

## 7. Offene Punkte

1. **Die drei Speicher in C3** — welcher ist der PSM 800, was sind die beiden anderen (TWW-Speicher?), wie viele Liter?
2. **Wärmepumpen in D2–D3** — stehen alle neun dort nebeneinander?
3. **Zweiter Heizungsraum im Seitenhaus** — was steht dort außer dem PSM 500?
4. **Die 20 Fancoils** — auf welchen Geschossen, wie viele je Strang?
5. **Meter je Dimension** (Ø22 / Ø28 / Ø35) für die Mengenermittlung
6. **Mail von Andrea + Anhang** — in leanstechgmbh@gmail.com nicht auffindbar (geprüft: „Karl-Marx-Straße 176" in allen Schreibweisen, „Karl-Marx", from/to/cc:andrea inkl. Papierkorb, alle Anhänge der letzten 3 Wochen, „176" der letzten 60 Tage, Drive-Volltext). Vermutlich an **sr@ (IONOS)** gegangen — dieses Postfach ist nicht angebunden.

---

## 8. Ablage und Dateien

**Google Drive:** `Projekte/Karl-Marx-Straße 176`
https://drive.google.com/drive/folders/1wCmuoqOWEoedISfJXdnWDOtSwl9n0tBR

Unterordner: `00 Projekt allgemein` · `01 E-Mail-Verlauf` · `02 Pläne und Zeichnungen` · `03 Angebote` · `04 Technische Unterlagen`

**Erzeugte Dateien (im Chat der Cloud-Sitzung, noch nicht im Drive):**
- `KMS-176_Plaene_RASTER.pdf` — alle 8 Blätter mit Vektor-Raster
- `KMS-176_RASTER_S1_KG.png` … `_S8_Blatt8.png` — Einzelblätter, 130 dpi

**Repository `genesis-dwg-service`, Branch `claude/hydraulikschema-wärmepumpen-tg232s`:**
- `tools/plan_raster.py` — legt beschriftetes Gitternetz über Pläne
- `tools/hydraulikschema_wp.py` — erzeugt das Hydraulikschema als DXF
- `zeichnungen/hydraulikschema-waermepumpen.dxf` / `.png`
- PR #40 (Draft) — Hydraulikschema mit Systemtrennung

---

## 9. Aufgabe für den Claude auf dem PC

Der Nutzer möchte die gerasterten Pläne **in Paint geöffnet** bekommen, um hineinzuzeichnen. Eine Cloud-Sitzung kann das nicht (kein Zugriff auf den Rechner) — ein lokal laufender Claude kann es.

Ablauf danach: Nutzer zeichnet Fancoils, Steigstränge und Leitungsführung ein und benennt die Stellen über die Rasterfelder → daraus saubere Zeichnung + Mengenermittlung → Angebot nach `vorlagen/angebot-muster.html` (Muster: Angebot 301).

**Verbindliche Regel (steht in CLAUDE.md):** Pläne werden immer mit beschriftetem Gitternetz ausgegeben — Spalten A, B, C…, Zeilen 1, 2, 3…, Beschriftung an allen vier Rändern. Werkzeug: `python3 tools/plan_raster.py <plan.pdf> [ordner] [--zelle=100] [--dpi=130]`.
