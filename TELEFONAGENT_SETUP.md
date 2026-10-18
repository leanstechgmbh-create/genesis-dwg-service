# Telefonagent für LEANS Tech — Einrichten

Ein KI-Assistent, der ans Telefon geht, wenn du auf der Baustelle bist:
Anrufer begrüßen, Anliegen und Kontaktdaten aufnehmen, Notfälle erkennen und
sofort an dich durchstellen, alles andere als Notiz hinterlassen.

**Aufbau:** Vapi (Rahmen + Rufnummer) → Deepgram (Ohren) → Claude (Kopf) →
geklonte Stimme (Mund). Alles anklickbar, kein Terminal nötig.

---

## 0 — Zwei Entscheidungen vorab

**Welche Stimme?**

| Variante | Vorteil | Nachteil |
|---|---|---|
| **Neutrale Stimme** (Empfehlung) | Klar als Assistent erkennbar, keine falschen Erwartungen | Weniger „persönlich" |
| **Deine geklonte Stimme** | Wiedererkennung, Firmen-Klang | Anrufer, die dich kennen, fühlen sich getäuscht — und die Pflichtansage („Das ist ein KI-Assistent") nimmt dem Effekt sowieso die Wirkung |

Beides ist in Schritt 2 mit einem Klick tauschbar. Anhören und entscheiden.

**Wann geht der Agent ran?** Empfehlung: **nicht** als Hauptnummer, sondern
als Weiterleitung, wenn du nach 20 Sekunden nicht abnimmst oder besetzt bist.
So bleibt jeder Anruf, den du selbst annehmen kannst, bei dir.

---

## 1 — Vapi-Konto anlegen

1. → https://vapi.ai → **Sign Up** (Google-Login geht)
2. Oben rechts **Billing** → Zahlungsmittel hinterlegen (ohne Guthaben klingelt nichts)
3. Links **API Keys** → *Private Key* kopieren, wird für nichts Weiteres gebraucht,
   solange du alles im Dashboard klickst

## 2 — Stimme klonen

Bei **ElevenLabs**, weil Vapi das direkt eingebaut hat (Fish Audio nicht — siehe unten).

1. → https://elevenlabs.io → Konto anlegen, Tarif **Starter** (ca. 5 $/Monat,
   Voice-Cloning ist erst ab da freigeschaltet)
2. **Voices** → **Add Voice** → *Instant Voice Cloning*
3. **Aufnahme:** 2–3 Minuten deine Stimme, ruhiger Raum, Handy-Mikro reicht.
   Sprich normal, so wie du ans Telefon gehst — nicht vorlesen.
   Am besten nimmst du einfach ein echtes Kundengespräch nach (nur deine Seite).
4. ElevenLabs verlangt eine **Einverständnis-Aufnahme**: einen vorgegebenen Satz
   vorlesen, dass es deine eigene Stimme ist. Das ist Pflicht und dauert 20 Sekunden.
5. Sprache auf **Deutsch** stellen, Modell `eleven_multilingual_v2` oder
   `eleven_turbo_v2_5` (schneller, für Telefonie besser)
6. **Voice ID** kopieren (steht unter der fertigen Stimme)

> Vor dem Scharfschalten: Probesatz mit Fachbegriffen anhören —
> „Split-Klimagerät", „VRF-Anlage", „Kältemittelleitung", „Wärmepumpe".
> Geklonte Stimmen verschlucken deutsche Fachwörter gern.

## 3 — Rufnummer

Im Vapi-Dashboard → **Phone Numbers** → **Buy Number** → Land **Deutschland**.

Falls Vapi für Deutschland keine Nummer anbietet (kommt vor, deutsche Nummern
brauchen einen Adressnachweis): Nummer bei **Twilio** kaufen, dort Adresse
hinterlegen, dann in Vapi unter **Import Number** eintragen.

## 4 — Assistenten anlegen

**Assistants** → **Create Assistant** → oben rechts das `{}`-Symbol
(*Edit as JSON*) → Inhalt von `telefonagent/assistant-vapi.json` einfügen.

Danach im JSON nur noch drei Stellen anpassen:

| Feld | Was rein muss |
|---|---|
| `voice.voiceId` | Voice ID aus Schritt 2 |
| `model.messages[0].content` | schon fertig — nur lesen und ggf. anpassen |
| Notfall-Nummer | steht im System-Prompt, aktuell +491708280836 |

Dann **Phone Numbers** → deine Nummer → Assistent zuweisen.

## 5 — Weiterleitung von deinem Handy

Bei der Telekom/Vodafone/O2 im Kundenportal oder direkt am Handy:

- **Bei Nichtmelden** (nach 20 Sek.) → Vapi-Nummer
- **Bei Besetzt** → Vapi-Nummer

Am iPhone: *Einstellungen → Telefon → Anrufweiterleitung*. Am Android hängt es
vom Hersteller ab, meist *Telefon-App → Einstellungen → Anrufweiterleitung*.

## 6 — Testen

Ruf die Vapi-Nummer selbst an und spiel drei Fälle durch:

1. **Normal:** „Ich bräuchte ein Angebot für eine Klimaanlage in der Wohnung."
   → Agent nimmt Name, Nummer, Adresse, Gewerk auf, sagt Rückruf zu.
2. **Notfall:** „Bei uns läuft Wasser aus der Heizung."
   → Agent stellt sofort auf dein Handy durch.
3. **Preisfrage:** „Was kostet das denn?"
   → Agent nennt **keine** Preise, sondern verweist auf dein Angebot.

Unter **Call Logs** hörst du jedes Gespräch nach und siehst das Transkript.

---

## Pflicht: die Ansage am Anfang

Seit **2. August 2026** gilt Artikel 50 der EU-KI-Verordnung: Anrufer müssen zu
Beginn erfahren, dass sie mit einer KI sprechen. Das ist keine Kür — der
Bußgeldrahmen liegt bei bis zu 15 Mio. € bzw. 3 % vom Jahresumsatz.

Die Begrüßung im JSON erfüllt das bereits:

> „LEANS Tech GmbH, guten Tag. Sie sprechen mit dem digitalen Assistenten der
> Firma — Herr Redžić ist gerade im Einsatz. Ich nehme Ihr Anliegen auf und er
> meldet sich zurück. Worum geht es denn?"

**Diesen Satz nicht kürzen.** Wenn du deine geklonte Stimme nutzt, ist er umso
wichtiger, weil Anrufer sonst sicher glauben, dich am Apparat zu haben.

Zusätzlich: Hinweis auf die KI-Annahme in die Datenschutzerklärung auf
leanstech-klima.de, und Gesprächsaufzeichnungen nur mit Ansage.

---

## Kosten (Schätzung, Stand 08/2026)

| Posten | Preis |
|---|---|
| Rufnummer | ca. 2 €/Monat |
| ElevenLabs Starter (Stimme) | ca. 5 €/Monat |
| Gespräch (Vapi + Telefonie + Claude + Stimme) | ca. 0,10–0,15 €/Minute |

**Bei 100 Anrufen à 3 Minuten:** rund 300 Minuten → **ca. 40–55 € im Monat**
inklusive Grundgebühren. Zum Vergleich: ein verpasster Wartungsauftrag.

Vapi rechnet pro Minute ab — kein Abo, keine Mindestlaufzeit. Wenn es nichts
taugt, Weiterleitung aus und fertig.

---

## Warum nicht Fish Audio direkt?

**Fish Audio S2.1 Pro** ist gut (ca. 90 ms bis zum ersten Ton, eigenes
Voice-Cloning) — aber **Vapi unterstützt es nicht ab Werk**. Man müsste über
Vapis *Custom TTS* einen eigenen kleinen Server dazwischenhängen, der Fish
anspricht und das Audio im geforderten PCM-Format zurückgibt. Mehr Teile, mehr
Fehlerquellen, kein hörbarer Gewinn gegenüber ElevenLabs auf Deutsch.

**Wo Fish sich lohnt:** in **Pipecat**, denn dort ist es fest eingebaut. Also
falls der Agent später mal so viel telefoniert, dass die Minutenpreise wehtun
und wir auf Pipecat selbst hosten — dann Fish. Bis dahin: ElevenLabs.

Der zweite gute Einsatz für deine geklonte Stimme sind **Social-Media-Videos**
und Sprachnachrichten-Vorlagen — da stört keine KI-Pflichtansage.

---

*Vorlage für den Assistenten: `telefonagent/assistant-vapi.json`
(Begrüßung, Gesprächsleitfaden, Notfall-Weiterleitung, Datenaufnahme).*
