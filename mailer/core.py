"""Kernlogik fuer den Klima-Anschreiben-Versand — LEANS Tech GmbH.

Wird sowohl vom CLI (send_mails.py) als auch vom HTTP-Endpunkt (/send-mails in
main.py) genutzt. Reine Python-Standardbibliothek (Gmail-SMTP).

Absender-Konfiguration kommt aus Umgebungsvariablen (in Cloud Run als Secret):
  GMAIL_USER, GMAIL_APP_PASSWORD, MAIL_ABSENDER, MAIL_FIRMA, MAIL_WEBSITE
"""
import csv
import os
import smtplib
import ssl
import time
from datetime import datetime, timezone
from email.message import EmailMessage
from email.utils import formataddr
from pathlib import Path

HIER = Path(__file__).resolve().parent
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SUBJECT_TEMPLATE = "Hitzeschutz für {einrichtung} – Klimalösungen für Pflegeräume"

STANDARD_CSV = HIER / "recipients.csv"
STANDARD_VORLAGE = HIER / "email_vorlage.txt"
STANDARD_LOG = HIER / "sent_log.csv"


def konfig() -> dict:
    """Liest die Absender-Konfiguration aus den Umgebungsvariablen."""
    return {
        "user": os.environ.get("GMAIL_USER", "leanstechgmbh@gmail.com"),
        "passwort": os.environ.get("GMAIL_APP_PASSWORD", ""),
        "absender": os.environ.get("MAIL_ABSENDER", "Semir Redzic"),
        "firma": os.environ.get("MAIL_FIRMA", "LeansTech GmbH"),
        "website": os.environ.get("MAIL_WEBSITE", "www.leanstech-klima.de"),
    }


def mail_bereit() -> bool:
    """True, wenn ein App-Passwort gesetzt ist (Versand moeglich)."""
    return bool(os.environ.get("GMAIL_APP_PASSWORD", ""))


def lade_vorlage(pfad, cfg: dict) -> str:
    """Liest die Text-Vorlage und fuellt die Absender-Platzhalter."""
    text = Path(pfad).read_text(encoding="utf-8")
    return text.format(absender=cfg["absender"], firma=cfg["firma"],
                       website=cfg["website"], gmail_user=cfg["user"])


def lade_empfaenger(pfad, status_filter=None) -> list[dict]:
    """Liest recipients.csv und filtert optional nach Status."""
    zeilen = []
    with Path(pfad).open(encoding="utf-8", newline="") as f:
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


def lade_versendete(log_pfad) -> set:
    """Liest bereits erfolgreich versendete Adressen aus dem Protokoll."""
    log_pfad = Path(log_pfad)
    if not log_pfad.exists():
        return set()
    versendet = set()
    with log_pfad.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if row.get("status") == "OK":
                versendet.add((row.get("email") or "").strip().lower())
    return versendet


def protokolliere(log_pfad, email: str, einrichtung: str, status: str, info: str):
    """Haengt eine Zeile ans Sende-Protokoll an."""
    log_pfad = Path(log_pfad)
    neu = not log_pfad.exists()
    with log_pfad.open("a", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        if neu:
            w.writerow(["zeitpunkt", "email", "einrichtung", "status", "info"])
        w.writerow([datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    email, einrichtung, status, info])


def baue_mail(einrichtung: str, empfaenger: str, body: str, cfg: dict) -> EmailMessage:
    """Baut eine fertige EmailMessage mit korrekten Headern."""
    msg = EmailMessage()
    msg["From"] = formataddr((f"{cfg['absender']} – {cfg['firma']}", cfg["user"]))
    msg["To"] = empfaenger
    msg["Reply-To"] = cfg["user"]
    msg["Subject"] = SUBJECT_TEMPLATE.format(einrichtung=einrichtung)
    msg.set_content(body)
    return msg


def smtp_verbinden(cfg: dict) -> smtplib.SMTP:
    """Oeffnet eine authentifizierte SMTP-Verbindung zu Gmail."""
    if not cfg["passwort"]:
        raise RuntimeError("GMAIL_APP_PASSWORD ist nicht gesetzt.")
    ctx = ssl.create_default_context()
    server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30)
    server.starttls(context=ctx)
    server.login(cfg["user"], cfg["passwort"])
    return server


def versende(*, send=False, limit=0, delay=2.0, status_filter=None, resend=False,
             csv_pfad=STANDARD_CSV, vorlage_pfad=STANDARD_VORLAGE,
             log_pfad=STANDARD_LOG, fortschritt=None) -> dict:
    """Plant bzw. fuehrt den Versand aus und liefert ein Ergebnis-Dict.

    send=False  -> Dry-Run: nur Vorschau, es wird NICHTS verschickt.
    send=True   -> echter Versand (benoetigt GMAIL_APP_PASSWORD).
    fortschritt -> optionaler Callback fortschritt(i, gesamt, eintrag, status, info).
    """
    cfg = konfig()
    body = lade_vorlage(vorlage_pfad, cfg)
    empfaenger = lade_empfaenger(csv_pfad, status_filter)
    versendet = set() if resend else lade_versendete(log_pfad)

    offen = [e for e in empfaenger if e["email"].lower() not in versendet]
    uebersprungen = len(empfaenger) - len(offen)
    if limit > 0:
        offen = offen[:limit]

    geplant = [{"einrichtung": e["einrichtung"], "email": e["email"],
                "betreff": SUBJECT_TEMPLATE.format(einrichtung=e["einrichtung"])}
               for e in offen]

    ergebnis = {
        "modus": "send" if send else "dry-run",
        "absender": cfg["user"],
        "offen": len(offen),
        "uebersprungen": uebersprungen,
        "geplant": geplant,
        "gesendet": 0,
        "fehler": 0,
        "details": [],
    }

    if not send:
        return ergebnis

    if not cfg["passwort"]:
        raise RuntimeError("GMAIL_APP_PASSWORD ist nicht gesetzt — Versand nicht moeglich.")

    server = smtp_verbinden(cfg)
    try:
        for i, e in enumerate(offen, 1):
            msg = baue_mail(e["einrichtung"], e["email"], body, cfg)
            status, info = "OK", ""
            try:
                server.send_message(msg)
            except smtplib.SMTPServerDisconnected:
                server = smtp_verbinden(cfg)
                server.send_message(msg)
                info = "reconnect"
            except Exception as ex:  # einzelne Mail darf den Lauf nicht abbrechen
                status, info = "FEHLER", str(ex)

            if status == "OK":
                ergebnis["gesendet"] += 1
            else:
                ergebnis["fehler"] += 1
            protokolliere(log_pfad, e["email"], e["einrichtung"], status, info)
            ergebnis["details"].append({"email": e["email"], "status": status, "info": info})
            if fortschritt:
                fortschritt(i, len(offen), e, status, info)

            if i < len(offen) and delay > 0:
                time.sleep(delay)
    finally:
        try:
            server.quit()
        except Exception:
            pass

    return ergebnis
