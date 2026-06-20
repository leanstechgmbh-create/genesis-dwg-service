#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""E-Mail-Versand fuer LEANS-Angebote (mit PDF-Anhang).

send_angebot() verschickt eine Mail mit dem branded Angebot-PDF als Anhang
ueber SMTP. Gedacht fuer den Versand an Partner (z.B. Mita).

Anmeldung ueber ENV:
  - `SMTP_HOST`     (Default: smtp.gmail.com)
  - `SMTP_PORT`     (Default: 587, STARTTLS)
  - `SMTP_USER`     Absender-/Login-Adresse (z.B. info@leanstech-gmbh.de)
  - `SMTP_PASSWORD` App-Passwort (bei Gmail: App-Passwort, NICHT das normale PW)
  - `SMTP_FROM`     optional, Absenderadresse falls abweichend von SMTP_USER

Kontakte / Aliasse (siehe CLAUDE.md):
  - "mita" -> info@aam-handwerk-montage.de
"""
import os
import smtplib
import ssl
from email.message import EmailMessage

# Bekannte Empfaenger-Aliasse
ALIASES = {
    "mita": "info@aam-handwerk-montage.de",
}


def resolve(recipient):
    """Alias (z.B. 'mita') in echte E-Mail-Adresse aufloesen."""
    return ALIASES.get(recipient.strip().lower(), recipient.strip())


def send_angebot(to, subject, body, pdf_path, from_addr=None):
    """Mail mit PDF-Anhang versenden. Gibt dict mit Status zurueck."""
    host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    port = int(os.environ.get("SMTP_PORT", "587"))
    user = os.environ.get("SMTP_USER")
    pw = os.environ.get("SMTP_PASSWORD")
    sender = from_addr or os.environ.get("SMTP_FROM") or user
    if not (user and pw):
        raise RuntimeError(
            "Kein SMTP-Login. Setze SMTP_USER und SMTP_PASSWORD (Gmail: App-Passwort)."
        )
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(pdf_path)

    to_addr = resolve(to)
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = to_addr
    msg["Subject"] = subject
    msg.set_content(body)
    with open(pdf_path, "rb") as f:
        msg.add_attachment(
            f.read(), maintype="application", subtype="pdf",
            filename=os.path.basename(pdf_path),
        )

    ctx = ssl.create_default_context()
    with smtplib.SMTP(host, port, timeout=30) as s:
        s.starttls(context=ctx)
        s.login(user, pw)
        s.send_message(msg)
    return {"ok": True, "to": to_addr, "subject": subject,
            "attachment": os.path.basename(pdf_path)}


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: mail_send.py <empfaenger|alias> <pdf-pfad> [betreff]")
        raise SystemExit(2)
    rcpt = sys.argv[1]
    pdf = sys.argv[2]
    subj = sys.argv[3] if len(sys.argv) > 3 else "Angebot LEANS Tech GmbH"
    res = send_angebot(rcpt,
                       subj,
                       "Anbei unser Angebot. Viele Grüße\nLEANS Tech GmbH",
                       pdf)
    print("SENT ->", res)
