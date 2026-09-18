# Laptop wach halten (Standby ausschalten) — Klick-Anleitung ohne Terminal

Problem: Der Laptop geht nach ein paar Minuten in den Standby. Alles, was auf
dem Laptop läuft (Claude auf dem PC, lange Chats, Uploads, Downloads,
n8n-Tests), wird dabei angehalten oder abgebrochen.

Lösung: Standby, Bildschirm-Aus und „Deckel zu" so einstellen, dass nichts
mehr einschläft, solange der Laptop am Strom hängt.

> **Wichtig:** Der Claude in der Cloud (claude.ai/code, Handy, Slack-Bot)
> hat KEINEN Zugriff auf den Laptop — er kann ihn weder aufwecken noch
> Einstellungen ändern. Die folgenden Schritte macht der Nutzer einmal von
> Hand, danach ist Ruhe.

---

## Schritt 1 — Standby und Bildschirm-Aus abschalten (Windows 11)

1. **Windows-Taste** drücken, `Energie` tippen, **Energie, Ruhezustand und Akku**
   öffnen (Windows 10: **Netzbetrieb und Energiesparen**).
2. Den Punkt **Bildschirm und Ruhezustand** aufklappen.
3. Alle vier Zeilen auf **Nie** stellen:

   | Einstellung | Wert |
   |---|---|
   | Bildschirm ausschalten bei Akkubetrieb nach | Nie *(oder 15 Min.)* |
   | Bildschirm ausschalten bei Netzbetrieb nach | **Nie** |
   | Gerät bei Akkubetrieb in Ruhezustand versetzen nach | Nie *(oder 30 Min.)* |
   | Gerät bei Netzbetrieb in Ruhezustand versetzen nach | **Nie** |

4. Weiter oben auf derselben Seite **Energiesparmodus** aufklappen und
   **Energiesparmodus automatisch aktivieren: Nie** wählen.
5. Bei **Energiemodus** (ganz oben) **Beste Leistung** auswählen — dann drosselt
   Windows im Hintergrund nichts mehr weg.

Fertig — das allein reicht in den meisten Fällen schon.

## Schritt 2 — Deckel zuklappen darf nichts abschalten

Das steht NICHT in den neuen Einstellungen, sondern noch in der alten Systemsteuerung:

1. **Windows-Taste** drücken, `Systemsteuerung` tippen, öffnen.
2. Oben rechts bei „Anzeige" auf **Kleine Symbole** umstellen.
3. **Energieoptionen** anklicken.
4. Links **Auswählen, was beim Zuklappen des Deckels geschehen soll**.
5. In der Spalte **Netzbetrieb** überall **Nichts unternehmen** wählen:
   - Beim Drücken des Netzschalters: *Nichts unternehmen*
   - Beim Zuklappen: **Nichts unternehmen**
6. Unten **Änderungen speichern**.

Danach läuft der Laptop auch mit zugeklapptem Deckel weiter (am Strom!).

## Schritt 3 — Nicht bei jeder Pause neu anmelden müssen

1. **Windows-Taste**, `Anmeldeoptionen` tippen, öffnen.
2. Bei **Wenn Sie abwesend waren, wann soll Windows eine erneute Anmeldung
   verlangen?** auf **Nie** stellen.
3. **Windows-Taste**, `Bildschirmschoner` tippen → **Bildschirmschoner ändern**
   → auf **(Ohne)** stellen, Haken bei „Anmeldeseite bei Reaktivierung"
   entfernen → **OK**.

## Schritt 4 — Prüfen, ob es sitzt

- Laptop am Strom lassen, 20 Minuten nichts anfassen.
- Bildschirm muss noch an sein, laufende Programme müssen weiterlaufen.
- Geht er trotzdem aus: meist ist noch ein zweites Energieprofil aktiv —
  Systemsteuerung → Energieoptionen → beim aktiven Plan auf
  **Energiesparplaneinstellungen ändern** → dort ebenfalls überall **Nie**,
  dann **Erweiterte Energieeinstellungen ändern** → **Festplatte → Festplatte
  ausschalten nach → Nie** und **USB-Einstellungen → Selektives USB-Energiesparen
  → Deaktiviert**.

## Falls es ein MacBook ist

1. **Systemeinstellungen** → **Batterie** → rechts unten **Optionen…**
2. **Automatisches Ruhen des Geräts verhindern, wenn das Display ausgeschaltet
   ist** → **einschalten** (nur bei Netzteil).
3. **Systemeinstellungen** → **Sperrbildschirm** → **Bildschirm bei Inaktivität
   ausschalten (Netzteil)** → **Nie**.

---

## Sicherheitshinweis (einmal lesen, dann vergessen)

Ein Laptop, der nie sperrt, ist unterwegs ein offenes Buch — Kundendaten,
Rechnungen, Mailpostfach. Deshalb:

- Die Einstellungen oben nur für **Netzbetrieb** auf „Nie" setzen, für
  **Akkubetrieb** ruhig 15/30 Minuten stehen lassen.
- Beim Verlassen des Platzes **Windows-Taste + L** drücken (sperrt sofort,
  laufende Programme laufen weiter).

## Was das NICHT löst

Der Laptop muss weiterhin **eingeschaltet** sein. Soll etwas laufen, während
der Laptop aus ist oder im Auto liegt, gehört es in die Cloud — dieser Dienst
(`genesis-dwg-service` auf Google Cloud Run), der Slack-Bot oder eine Routine.
Cloud-Aufgaben laufen unabhängig vom Laptop weiter; Aufgaben im Ordner
`C:\Users\semir\…` (z. B. LEANS-OS) kann dagegen nur der Claude auf dem PC
erledigen — und der braucht einen wachen Laptop.
