#!/usr/bin/env python3
"""Versand der beiden Klement-Mails von info@ mit PDF-Anhaengen — LEANS Tech GmbH.

Verschickt in einem Rutsch:
  1) Finales Angebot Nr. 301           (Anhang: Angebot-PDF)
  2) 1. Abschlagsrechnung Nr. 2026-39  (Anhang: Rechnung-PDF)
an Frau Klement (SP Construct GmbH), Absender info@leanstech-gmbh.de.

Sicherheits-Default: ohne --send nur VORSCHAU (Dry-Run, es wird NICHTS gesendet).

Voraussetzung fuer echten Versand:
  * GMAIL_APP_PASSWORD gesetzt (16-stelliges App-Passwort des Gmail-Kontos)
  * MAIL_FROM=info@leanstech-gmbh.de  (info@ muss im Konto als "Senden als"
    verifiziert sein, sonst ersetzt Gmail den Absender durch die Login-Adresse)

Beispiele:
  # Vorschau (sendet nichts):
  python3 mailer/send_klement.py --angebot Angebot_301.pdf --rechnung Rechnung_2026-39.pdf

  # Wirklich senden:
  MAIL_FROM=info@leanstech-gmbh.de GMAIL_APP_PASSWORD=xxxx \\
      python3 mailer/send_klement.py --angebot Angebot_301.pdf \\
      --rechnung Rechnung_2026-39.pdf --send
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core  # noqa: E402

EMPFAENGER = "AKlement@strateges.de"

ANGEBOT_BETREFF = ("Klimatisierung Dachgeschoss Mehringdamm 44–46 – "
                   "finales Angebot (Nr. 301)")
ANGEBOT_TEXT = """Sehr geehrte Frau Klement,

anbei erhalten Sie unser finales Angebot für die Klimatisierung des Dachgeschosses (Angebot Nr. 301).

Grundlage der Auslegung ist die Kühllast des gesamten Dachgeschosses: Bei rund 170 m² Wohnfläche je Wohneinheit (beide Einheiten zusammen rund 340 m²) – mit den großen Wohn-/Essbereichen von jeweils ca. 71 m² (Raumhöhe ca. 3,5 m und großen Glasflächen) – ergibt sich der entsprechende Leistungsbedarf. Diesen decken wir je Wohneinheit mit zwei verdeckten Kanalgeräten (5,0 kW) sowie drei Wandgeräten ab. Dabei haben wir ein zusätzliches, kleineres Innengerät ergänzt (nun drei statt zwei Wandgeräte) und im Gegenzug die beiden übrigen Wandgeräte in der Leistung reduziert – bedingt durch die Leitungslängen und die Leistungsverteilung. An der Kühlwirkung in den Räumen ändert das nichts.

Aufgrund der langen Kältemittel-Leitungsführung mussten wir zudem je Wohneinheit ein größeres Außengerät (LG MU5R40) einplanen. Wir haben dies noch einmal direkt mit dem Hersteller abgestimmt und konnten den Preis entsprechend verhandeln – dadurch schlägt das größere Außengerät mit lediglich 170 € Mehrpreis je Gerät zu Buche.

Damit wir sämtliche Gerätschaften verbindlich bestellen können, benötigen wir eine Anzahlung von 50–60 % der Auftragssumme. Nach Zahlungseingang beschaffen wir das komplette Material und führen die Installation zügig aus: Außengeräte, Kanalgeräte, Verrohrung, Kältemittel- und Kondensatleitungen sowie die Verkabelung werden vollständig montiert und die Anlage wird abgedrückt. Lediglich die sichtbaren Wandgeräte setzen wir ganz zum Schluss – erst nach Abschluss der Malerarbeiten. Bis dahin ist die restliche Anlage fertiggestellt und funktionsbereit; die Wandgeräte werden anschließend final montiert und die Anlage in Betrieb genommen.

Das Angebot finden Sie im Anhang. Für Rückfragen stehe ich Ihnen gerne zur Verfügung.

Mit freundlichen Grüßen
Semir Redzic
LEANS Tech GmbH
info@leanstech-gmbh.de · Tel. +49 170 828 0836
"""

RECHNUNG_BETREFF = ("1. Abschlagsrechnung Nr. 2026-39 – "
                    "Klimatisierung Mehringdamm 44–46 (Angebot 301)")
RECHNUNG_TEXT = """Sehr geehrte Frau Klement,

wie besprochen erhalten Sie anbei die 1. Abschlagsrechnung (Nr. 2026-39) zum Angebot Nr. 301.

Der Abschlag in Höhe von 50 % – 23.193,00 € (§ 13b, Steuerschuldnerschaft des Leistungsempfängers) – dient der Materialbeschaffung und dem Auftragsstart. Nach Zahlungseingang lösen wir die verbindliche Bestellung aus und beginnen mit der Ausführung.

Die Rechnung ist sofort zahlbar; unsere Bankverbindung entnehmen Sie bitte der beigefügten Rechnung.

Für Rückfragen bin ich gerne erreichbar.

Mit freundlichen Grüßen
Semir Redzic
LEANS Tech GmbH
info@leanstech-gmbh.de · Tel. +49 170 828 0836
"""


def main() -> int:
    p = argparse.ArgumentParser(
        description="Angebot 301 + Abschlagsrechnung 2026-39 von info@ an Frau Klement senden.")
    p.add_argument("--angebot", required=True, help="Pfad zum Angebot-PDF (Nr. 301).")
    p.add_argument("--rechnung", required=True, help="Pfad zum Rechnung-PDF (2026-39).")
    p.add_argument("--to", default=EMPFAENGER, help=f"Empfaenger (Standard: {EMPFAENGER}).")
    p.add_argument("--send", action="store_true",
                   help="WIRKLICH senden. Ohne dieses Flag nur Vorschau (Dry-Run).")
    p.add_argument("--yes", action="store_true",
                   help="Sicherheitsabfrage vor echtem Versand ueberspringen.")
    args = p.parse_args()

    cfg = core.konfig()
    angebot, rechnung = Path(args.angebot), Path(args.rechnung)
    for f in (angebot, rechnung):
        if not f.is_file():
            print(f"FEHLER: Datei nicht gefunden: {f}")
            return 1

    mails = [
        (ANGEBOT_BETREFF, ANGEBOT_TEXT, [str(angebot)]),
        (RECHNUNG_BETREFF, RECHNUNG_TEXT, [str(rechnung)]),
    ]

    modus = "ECHTER VERSAND" if args.send else "DRY-RUN (Vorschau, nichts wird gesendet)"
    print("=" * 64)
    print(f"Modus     : {modus}")
    print(f"Absender  : {cfg['from_addr']}  (Login/Auth: {cfg['user']})")
    print(f"Empfaenger: {args.to}")
    print("=" * 64)
    for betreff, _, anh in mails:
        print(f"- {betreff}")
        for a in anh:
            print(f"    Anhang: {Path(a).name}")

    if not args.send:
        print("\nDRY-RUN beendet. Zum echten Versand das Flag --send setzen.")
        return 0

    if cfg["from_addr"] == cfg["user"]:
        print(f"\nHINWEIS: MAIL_FROM ist nicht auf info@ gesetzt — es wird von "
              f"{cfg['user']} gesendet.")

    if not args.yes and sys.stdin.isatty():
        antwort = input(f"\n2 Mails wirklich von {cfg['from_addr']} an {args.to} senden? [j/N] ")
        if antwort.strip().lower() not in ("j", "ja", "y", "yes"):
            print("Abgebrochen.")
            return 0

    try:
        with core.smtp_verbinden(cfg) as server:
            for betreff, text, anh in mails:
                msg = core.baue_nachricht(args.to, betreff, text, cfg, anhaenge=anh)
                server.send_message(msg)
                print(f"OK  -> {betreff}")
    except RuntimeError as e:
        print(f"FEHLER: {e}\nApp-Passwort setzen: export GMAIL_APP_PASSWORD=\"...\"")
        return 1

    print("-" * 64)
    print("Fertig. Beide Mails wurden versendet.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
