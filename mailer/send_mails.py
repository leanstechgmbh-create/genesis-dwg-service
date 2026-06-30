#!/usr/bin/env python3
"""Klima-Anschreiben-Versender — LEANS Tech GmbH.

Verschickt das Klimaanlagen-Anschreiben per Gmail-SMTP an die Pflegeeinrichtungen
aus recipients.csv. Nutzt nur die Python-Standardbibliothek (keine Extra-Pakete).

Sicherheits-Defaults:
  * Ohne --send laeuft alles als DRY-RUN (es wird NICHTS verschickt, nur angezeigt).
  * Ein Sende-Protokoll (sent_log.csv) verhindert versehentlichen Doppelversand.
  * --delay drosselt den Versand (Standard 20s), damit Gmail nicht als Spam wertet.

Voraussetzung zum echten Versenden:
  Gmail-App-Passwort (16-stellig) bei aktivierter 2-Faktor-Anmeldung.
  Konto -> Sicherheit -> 2-Schritt-Bestaetigung -> App-Passwoerter.
  Dann als Umgebungsvariable setzen: GMAIL_APP_PASSWORD="xxxxxxxxxxxxxxxx"

Beispiele:
  # 1) Vorschau (verschickt nichts):
  python3 send_mails.py

  # 2) Testmail an die eigene Adresse:
  GMAIL_APP_PASSWORD=... python3 send_mails.py --test deine@adresse.de

  # 3) Erste 10 wirklich senden, 30s Abstand:
  GMAIL_APP_PASSWORD=... python3 send_mails.py --send --limit 10 --delay 30

  # 4) Nur die bestaetigten Adressen senden:
  GMAIL_APP_PASSWORD=... python3 send_mails.py --send --only-confirmed
"""
import argparse
import csv
import os
import smtplib
import ssl
import sys
import time
from datetime import datetime, timezone
from email.message import EmailMessage
from email.utils import formataddr, parseaddr
from pathlib import Path

HIER = Path(__file__).resolve().parent
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587

SUBJECT_TEMPLATE = "Hitzeschutz für {einrichtung} – Klimalösungen für Pflegeräume"

# Absender-Daten (per Umgebungsvariable ueberschreibbar)
GMAIL_USER = os.environ.get("GMAIL_USER", "leanstechgmbh@gmail.com")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")
ABSENDER = os.environ.get("MAIL_ABSENDER", "Semir Redzic")
FIRMA = os.environ.get("MAIL_FIRMA", "LeansTech GmbH")
WEBSITE = os.environ.get("MAIL_WEBSITE", "www.leanstech-klima.de")


def lade_vorlage(pfad: Path) -> str:
    """Liest die Text-Vorlage und fuellt die Absender-Platzhalter."""
    text = pfad.read_text(encoding="utf-8")
    return text.format(absender=ABSENDER, firma=FIRMA,
                       website=WEBSITE, gmail_user=GMAIL_USER)


def lade_empfaenger(pfad: Path, status_filter: set | None) -> list[dict]:
    """Liest recipients.csv und filtert optional nach Status."""
    zeilen = []
    with pfad.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            email = (row.get("email") or "").strip()
            name = (row.get("einrichtung") or "").strip()
            status = (row.get("status") or "").strip().lower()
            if not email or "@" not in email:
                continue
            if status_filter and status not in status_filter:
                continue
            zeilen.append({"einrichtung": name, "email": email, "status": status})
    return zeilen


def lade_versendete(log_pfad: Path) -> set:
    """Liest bereits versendete Adressen aus dem Protokoll (Doppelversand-Schutz)."""
    if not log_pfad.exists():
        return set()
    versendet = set()
    with log_pfad.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if row.get("status") == "OK":
                versendet.add((row.get("email") or "").strip().lower())
    return versendet


def protokolliere(log_pfad: Path, email: str, einrichtung: str, status: str, info: str):
    """Haengt eine Zeile ans Sende-Protokoll an."""
    neu = not log_pfad.exists()
    with log_pfad.open("a", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        if neu:
            w.writerow(["zeitpunkt", "email", "einrichtung", "status", "info"])
        w.writerow([datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    email, einrichtung, status, info])


def baue_mail(einrichtung: str, empfaenger: str, body: str) -> EmailMessage:
    """Baut eine fertige EmailMessage mit korrekten Headern."""
    msg = EmailMessage()
    msg["From"] = formataddr((f"{ABSENDER} – {FIRMA}", GMAIL_USER))
    msg["To"] = empfaenger
    msg["Reply-To"] = GMAIL_USER
    msg["Subject"] = SUBJECT_TEMPLATE.format(einrichtung=einrichtung)
    msg.set_content(body)
    return msg


def smtp_verbinden() -> smtplib.SMTP:
    """Oeffnet eine authentifizierte SMTP-Verbindung zu Gmail."""
    if not GMAIL_APP_PASSWORD:
        raise SystemExit(
            "FEHLER: GMAIL_APP_PASSWORD ist nicht gesetzt.\n"
            "Erstelle ein Gmail-App-Passwort (2-Faktor noetig) und setze es:\n"
            '  export GMAIL_APP_PASSWORD="xxxxxxxxxxxxxxxx"')
    ctx = ssl.create_default_context()
    server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30)
    server.starttls(context=ctx)
    server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
    return server


def main() -> int:
    p = argparse.ArgumentParser(description="Klima-Anschreiben per Gmail-SMTP versenden.")
    p.add_argument("--csv", default=str(HIER / "recipients.csv"),
                   help="Pfad zur Empfaenger-CSV (Standard: recipients.csv)")
    p.add_argument("--template", default=str(HIER / "email_vorlage.txt"),
                   help="Pfad zur Text-Vorlage (Standard: email_vorlage.txt)")
    p.add_argument("--log", default=str(HIER / "sent_log.csv"),
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

    body = lade_vorlage(Path(args.template))

    # --- Testmodus: eine Mail an die angegebene Adresse ---
    if args.test:
        ziel = parseaddr(args.test)[1]
        if "@" not in ziel:
            print(f"Ungueltige Test-Adresse: {args.test}")
            return 1
        msg = baue_mail("Ihre Pflegeeinrichtung (TEST)", ziel, body)
        print(f"Sende Testmail an {ziel} ...")
        with smtp_verbinden() as server:
            server.send_message(msg)
        print("Testmail verschickt. Bitte Posteingang pruefen.")
        return 0

    # --- Empfaenger laden + filtern ---
    status_filter = None
    if args.only_confirmed:
        status_filter = {"bestaetigt"}
    elif args.status:
        status_filter = {s.strip().lower() for s in args.status.split(",") if s.strip()}

    empfaenger = lade_empfaenger(Path(args.csv), status_filter)
    log_pfad = Path(args.log)
    versendet = set() if args.resend else lade_versendete(log_pfad)

    offen = [e for e in empfaenger if e["email"].lower() not in versendet]
    uebersprungen = len(empfaenger) - len(offen)
    if args.limit > 0:
        offen = offen[:args.limit]

    modus = "ECHTER VERSAND" if args.send else "DRY-RUN (Vorschau, nichts wird gesendet)"
    print("=" * 64)
    print(f"Modus      : {modus}")
    print(f"Absender   : {ABSENDER} <{GMAIL_USER}>")
    print(f"Empfaenger : {len(offen)} offen, {uebersprungen} bereits versendet uebersprungen")
    print(f"Delay      : {args.delay:.0f}s zwischen den Mails")
    print("=" * 64)

    if not offen:
        print("Keine offenen Empfaenger. Nichts zu tun.")
        return 0

    for i, e in enumerate(offen, 1):
        betreff = SUBJECT_TEMPLATE.format(einrichtung=e["einrichtung"])
        print(f"[{i:>2}/{len(offen)}] {e['email']:<42} | {betreff}")

    if not args.send:
        print("\nDRY-RUN beendet. Zum echten Versand das Flag --send setzen.")
        return 0

    # --- Sicherheitsabfrage vor echtem Versand ---
    if not args.yes and sys.stdin.isatty():
        antwort = input(f"\n{len(offen)} Mails wirklich von {GMAIL_USER} senden? [j/N] ")
        if antwort.strip().lower() not in ("j", "ja", "y", "yes"):
            print("Abgebrochen.")
            return 0

    # --- Echter Versand ---
    print()
    ok, fehler = 0, 0
    server = smtp_verbinden()
    try:
        for i, e in enumerate(offen, 1):
            msg = baue_mail(e["einrichtung"], e["email"], body)
            try:
                server.send_message(msg)
                ok += 1
                protokolliere(log_pfad, e["email"], e["einrichtung"], "OK", "")
                print(f"[{i:>2}/{len(offen)}] OK      -> {e['email']}")
            except smtplib.SMTPServerDisconnected:
                # Verbindung neu aufbauen und einmal erneut versuchen
                server = smtp_verbinden()
                server.send_message(msg)
                ok += 1
                protokolliere(log_pfad, e["email"], e["einrichtung"], "OK", "reconnect")
                print(f"[{i:>2}/{len(offen)}] OK*     -> {e['email']}")
            except Exception as ex:
                fehler += 1
                protokolliere(log_pfad, e["email"], e["einrichtung"], "FEHLER", str(ex))
                print(f"[{i:>2}/{len(offen)}] FEHLER  -> {e['email']}: {ex}")
            if i < len(offen) and args.delay > 0:
                time.sleep(args.delay)
    finally:
        try:
            server.quit()
        except Exception:
            pass

    print("-" * 64)
    print(f"Fertig. Gesendet: {ok}, Fehler: {fehler}. Protokoll: {log_pfad}")
    return 0 if fehler == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
