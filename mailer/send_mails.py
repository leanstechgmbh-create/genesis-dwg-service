#!/usr/bin/env python3
"""Klima-Anschreiben-Versender (CLI) — LEANS Tech GmbH.

Duenne Kommandozeilen-Huelle um mailer/core.py. Verschickt das Klimaanlagen-
Anschreiben per Gmail-SMTP an die Pflegeeinrichtungen aus recipients.csv.

Sicherheits-Defaults:
  * Ohne --send laeuft alles als DRY-RUN (es wird NICHTS verschickt).
  * Ein Sende-Protokoll (sent_log.csv) verhindert versehentlichen Doppelversand.
  * --delay drosselt den Versand (Standard 20s), damit Gmail nicht als Spam wertet.

Voraussetzung zum echten Versenden:
  Gmail-App-Passwort (16-stellig) bei aktivierter 2-Faktor-Anmeldung als
  Umgebungsvariable: GMAIL_APP_PASSWORD="xxxxxxxxxxxxxxxx"

Beispiele:
  python3 send_mails.py                                   # Vorschau (sendet nichts)
  python3 send_mails.py --test deine@adresse.de           # Testmail an sich selbst
  python3 send_mails.py --send --limit 10 --delay 30      # 10 senden, 30s Abstand
  python3 send_mails.py --send --only-confirmed           # nur bestaetigte Adressen
"""
import argparse
import sys
from email.utils import parseaddr
from pathlib import Path

import core

HIER = Path(__file__).resolve().parent


def _fortschritt(i, gesamt, eintrag, status, info):
    marke = "OK     " if status == "OK" else "FEHLER "
    extra = f" ({info})" if info else ""
    print(f"[{i:>2}/{gesamt}] {marke} -> {eintrag['email']}{extra}")


def main() -> int:
    p = argparse.ArgumentParser(description="Klima-Anschreiben per Gmail-SMTP versenden.")
    p.add_argument("--csv", default=str(core.STANDARD_CSV),
                   help="Pfad zur Empfaenger-CSV (Standard: recipients.csv)")
    p.add_argument("--template", default=str(core.STANDARD_VORLAGE),
                   help="Pfad zur Text-Vorlage (Standard: email_vorlage.txt)")
    p.add_argument("--log", default=str(core.STANDARD_LOG),
                   help="Pfad zum Sende-Protokoll (Standard: sent_log.csv)")
    p.add_argument("--send", action="store_true",
                   help="WIRKLICH senden. Ohne dieses Flag nur Vorschau (Dry-Run).")
    p.add_argument("--test", metavar="EMAIL",
                   help="Eine einzelne Testmail an EMAIL senden und beenden.")
    p.add_argument("--limit", type=int, default=0,
                   help="Hoechstens N Mails pro Lauf (0 = alle).")
    p.add_argument("--delay", type=float, default=20.0,
                   help="Sekunden Pause zwischen zwei Mails (Standard: 20).")
    p.add_argument("--only-confirmed", action="store_true",
                   help="Nur Adressen mit Status 'bestaetigt'.")
    p.add_argument("--status", default="",
                   help="Komma-Liste der erlaubten Status (z.B. bestaetigt,zentral).")
    p.add_argument("--resend", action="store_true",
                   help="Sende-Protokoll ignorieren (auch bereits Versendete erneut).")
    p.add_argument("--yes", action="store_true",
                   help="Sicherheitsabfrage vor echtem Versand ueberspringen.")
    args = p.parse_args()

    cfg = core.konfig()

    # --- Testmodus: eine Mail an die angegebene Adresse ---
    if args.test:
        ziel = parseaddr(args.test)[1]
        if "@" not in ziel:
            print(f"Ungueltige Test-Adresse: {args.test}")
            return 1
        body = core.lade_vorlage(args.template, cfg)
        msg = core.baue_mail("Ihre Pflegeeinrichtung (TEST)", ziel, body, cfg)
        print(f"Sende Testmail an {ziel} ...")
        try:
            with core.smtp_verbinden(cfg) as server:
                server.send_message(msg)
        except RuntimeError as e:
            print(f"FEHLER: {e}\nApp-Passwort setzen: export GMAIL_APP_PASSWORD=\"...\"")
            return 1
        print("Testmail verschickt. Bitte Posteingang pruefen.")
        return 0

    # --- Status-Filter bestimmen ---
    status_filter = None
    if args.only_confirmed:
        status_filter = {"bestaetigt"}
    elif args.status:
        status_filter = {s.strip().lower() for s in args.status.split(",") if s.strip()}

    # --- Vorschau (Dry-Run) berechnen ---
    vorschau = core.versende(send=False, limit=args.limit, status_filter=status_filter,
                             resend=args.resend, csv_pfad=args.csv,
                             vorlage_pfad=args.template, log_pfad=args.log)

    modus = "ECHTER VERSAND" if args.send else "DRY-RUN (Vorschau, nichts wird gesendet)"
    print("=" * 64)
    print(f"Modus      : {modus}")
    print(f"Absender   : {cfg['absender']} <{cfg['user']}>")
    print(f"Empfaenger : {vorschau['offen']} offen, "
          f"{vorschau['uebersprungen']} bereits versendet uebersprungen")
    print(f"Delay      : {args.delay:.0f}s zwischen den Mails")
    print("=" * 64)

    if not vorschau["geplant"]:
        print("Keine offenen Empfaenger. Nichts zu tun.")
        return 0

    for i, g in enumerate(vorschau["geplant"], 1):
        print(f"[{i:>2}/{vorschau['offen']}] {g['email']:<42} | {g['betreff']}")

    if not args.send:
        print("\nDRY-RUN beendet. Zum echten Versand das Flag --send setzen.")
        return 0

    # --- Sicherheitsabfrage vor echtem Versand ---
    if not args.yes and sys.stdin.isatty():
        antwort = input(f"\n{vorschau['offen']} Mails wirklich von {cfg['user']} senden? [j/N] ")
        if antwort.strip().lower() not in ("j", "ja", "y", "yes"):
            print("Abgebrochen.")
            return 0

    # --- Echter Versand ---
    print()
    try:
        ergebnis = core.versende(send=True, limit=args.limit, delay=args.delay,
                                 status_filter=status_filter, resend=args.resend,
                                 csv_pfad=args.csv, vorlage_pfad=args.template,
                                 log_pfad=args.log, fortschritt=_fortschritt)
    except RuntimeError as e:
        print(f"FEHLER: {e}\nApp-Passwort setzen: export GMAIL_APP_PASSWORD=\"...\"")
        return 1

    print("-" * 64)
    print(f"Fertig. Gesendet: {ergebnis['gesendet']}, Fehler: {ergebnis['fehler']}. "
          f"Protokoll: {args.log}")
    return 0 if ergebnis["fehler"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
