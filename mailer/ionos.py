"""Mailversand ueber das IONOS-Postfach sr@leanstech-gmbh.de — LEANS Tech GmbH.

Rechnungen, Angebote und Behoerdenpost gehen IMMER von sr@ raus, nie von der
Gmail-Adresse. Dieses Modul kann beides:

  entwurf(...)  legt die fertige Mail per IMAP im Ordner "Entwuerfe" ab —
                Semir sieht sie in seinem Postfach und schickt sie selbst los.
  sende(...)    verschickt direkt per SMTP und legt eine Kopie in "Gesendet".

Reine Standardbibliothek (smtplib / imaplib), keine zusaetzlichen Pakete.

Konfiguration ueber Umgebungsvariablen (in Cloud Run als Variablen setzen):
  IONOS_MAIL_USER      z. B. sr@leanstech-gmbh.de
  IONOS_MAIL_PASSWORT  Postfach-Passwort
  IONOS_MAIL_ABSENDER  Anzeigename, Standard "Semir Redzic - LEANS Tech GmbH"
  IONOS_SMTP_HOST/PORT Standard smtp.ionos.de / 465 (SSL)
  IONOS_IMAP_HOST/PORT Standard imap.ionos.de / 993 (SSL)
"""
import base64
import imaplib
import mimetypes
import os
import smtplib
import ssl
import time
from email.message import EmailMessage
from email.utils import formataddr, formatdate, make_msgid
from pathlib import Path

# IMAP-Ordner heissen je nach Postfach anders. Reihenfolge = Suchreihenfolge.
ENTWURF_NAMEN = ("drafts", "entwürfe", "entwuerfe", "entwurf")
GESENDET_NAMEN = ("sent", "sent items", "gesendet", "gesendete objekte",
                  "gesendete elemente")


def konfig() -> dict:
    """Liest die Postfach-Konfiguration aus den Umgebungsvariablen."""
    return {
        "user": os.environ.get("IONOS_MAIL_USER", ""),
        "passwort": os.environ.get("IONOS_MAIL_PASSWORT", ""),
        "absender": os.environ.get("IONOS_MAIL_ABSENDER",
                                   "Semir Redzic - LEANS Tech GmbH"),
        "smtp_host": os.environ.get("IONOS_SMTP_HOST", "smtp.ionos.de"),
        "smtp_port": int(os.environ.get("IONOS_SMTP_PORT", "465")),
        "imap_host": os.environ.get("IONOS_IMAP_HOST", "imap.ionos.de"),
        "imap_port": int(os.environ.get("IONOS_IMAP_PORT", "993")),
    }


def ionos_bereit() -> bool:
    """True, wenn Benutzer und Passwort fuer sr@ hinterlegt sind."""
    cfg = konfig()
    return bool(cfg["user"] and cfg["passwort"])


def _pruefe_konfig(cfg: dict):
    if not cfg["user"] or not cfg["passwort"]:
        raise RuntimeError(
            "IONOS-Postfach nicht konfiguriert — IONOS_MAIL_USER und "
            "IONOS_MAIL_PASSWORT muessen gesetzt sein.")


def _haenge_an(msg: EmailMessage, anhang: dict):
    """Haengt einen Anhang an: {dateiname, inhalt_base64} oder {pfad}."""
    if anhang.get("pfad"):
        pfad = Path(anhang["pfad"])
        daten = pfad.read_bytes()
        name = anhang.get("dateiname") or pfad.name
    else:
        inhalt = anhang.get("inhalt_base64") or anhang.get("inhalt") or ""
        daten = base64.b64decode(inhalt)
        name = anhang.get("dateiname") or "anhang.bin"

    typ = anhang.get("typ") or mimetypes.guess_type(name)[0] or "application/octet-stream"
    haupt, _, unter = typ.partition("/")
    msg.add_attachment(daten, maintype=haupt, subtype=unter or "octet-stream",
                       filename=name)


def baue_nachricht(*, an, betreff: str, text: str, anhaenge=None, cc=None,
                   antwort_auf: str = "", cfg: dict = None) -> EmailMessage:
    """Baut die fertige Mail mit Absender sr@, Text und Anhaengen.

    an / cc          str oder Liste von Adressen (leer erlaubt -> Entwurf ohne
                     Empfaenger, den Semir selbst eintraegt)
    antwort_auf      Message-ID der Mail, auf die geantwortet wird (optional)
    """
    cfg = cfg or konfig()
    if isinstance(an, str):
        an = [a.strip() for a in an.split(",") if a.strip()]
    if isinstance(cc, str):
        cc = [c.strip() for c in cc.split(",") if c.strip()]

    msg = EmailMessage()
    msg["From"] = formataddr((cfg["absender"], cfg["user"]))
    if an:
        msg["To"] = ", ".join(an)
    if cc:
        msg["Cc"] = ", ".join(cc)
    msg["Subject"] = betreff
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain=cfg["user"].split("@")[-1] or None)
    if antwort_auf:
        msg["In-Reply-To"] = antwort_auf
        msg["References"] = antwort_auf
    msg.set_content(text)

    for anhang in (anhaenge or []):
        _haenge_an(msg, anhang)
    return msg


def _imap_verbinden(cfg: dict) -> imaplib.IMAP4_SSL:
    ctx = ssl.create_default_context()
    imap = imaplib.IMAP4_SSL(cfg["imap_host"], cfg["imap_port"],
                             ssl_context=ctx, timeout=30)
    imap.login(cfg["user"], cfg["passwort"])
    return imap


def _dekodiere(name: str) -> str:
    """Wandelt einen IMAP-Ordnernamen (modifiziertes UTF-7) in Klartext.

    IMAP nutzt "&" als Umschaltzeichen statt "+" wie normales UTF-7, und "&-"
    steht fuer ein echtes "&" (z. B. "Entw&APw-rfe" -> "Entwuerfe" mit ue).
    """
    if "&" not in name:
        return name
    try:
        roh = name.replace("&-", "\x00").replace("&", "+")
        return roh.encode("latin-1").decode("utf-7").replace("\x00", "&")
    except Exception:
        return name


def finde_ordner(imap: imaplib.IMAP4_SSL, namen, sonderflag: str) -> str:
    """Sucht den passenden Postfach-Ordner (z. B. Entwuerfe).

    Zuerst ueber das SPECIAL-USE-Flag (\\Drafts / \\Sent), danach ueber die
    bekannten Ordnernamen. Gibt den Ordnernamen zurueck, wie ihn der Server
    erwartet, oder "" wenn nichts passt.
    """
    status, zeilen = imap.list()
    if status != "OK":
        return ""

    kandidaten = []
    for zeile in zeilen:
        roh = zeile.decode("latin-1") if isinstance(zeile, bytes) else str(zeile)
        # Format: (\HasNoChildren \Drafts) "/" "INBOX.Drafts"
        flags = roh[roh.find("(") + 1:roh.find(")")].lower() if "(" in roh else ""
        teile = roh.rsplit('"', 2)
        ordner = teile[-2] if len(teile) >= 3 else roh.split()[-1]
        kandidaten.append((flags, ordner))

    for flags, ordner in kandidaten:
        if sonderflag.lower() in flags:
            return ordner
    for flags, ordner in kandidaten:
        kurz = _dekodiere(ordner).split(".")[-1].split("/")[-1].strip().lower()
        if kurz in namen:
            return ordner
    return ""


def _ablegen(cfg: dict, msg: EmailMessage, namen, sonderflag: str,
             markierung: str) -> str:
    """Legt eine fertige Nachricht per IMAP in den passenden Ordner."""
    imap = _imap_verbinden(cfg)
    try:
        ordner = finde_ordner(imap, namen, sonderflag)
        if not ordner:
            raise RuntimeError(
                f"Kein Ordner fuer {sonderflag} im Postfach {cfg['user']} gefunden.")
        status, antwort = imap.append(
            f'"{ordner}"', markierung,
            imaplib.Time2Internaldate(time.time()), msg.as_bytes())
        if status != "OK":
            raise RuntimeError(f"IMAP-Ablage fehlgeschlagen: {antwort}")
        return _dekodiere(ordner)
    finally:
        try:
            imap.logout()
        except Exception:
            pass


def entwurf(*, an="", betreff: str, text: str, anhaenge=None, cc=None,
            antwort_auf: str = "") -> dict:
    """Legt die Mail als Entwurf in sr@ ab — es wird NICHTS verschickt.

    Genau der Weg fuer Rechnungen, Angebote und Behoerdenpost: Semir sieht den
    fertigen Entwurf samt Anhaengen im Postfach und schickt ihn selbst los.
    """
    cfg = konfig()
    _pruefe_konfig(cfg)
    msg = baue_nachricht(an=an, betreff=betreff, text=text, anhaenge=anhaenge,
                         cc=cc, antwort_auf=antwort_auf, cfg=cfg)
    ordner = _ablegen(cfg, msg, ENTWURF_NAMEN, "\\Drafts", r"(\Draft)")
    return {"status": "entwurf_abgelegt", "postfach": cfg["user"],
            "ordner": ordner, "betreff": betreff,
            "an": msg.get("To", ""), "anhaenge": len(anhaenge or [])}


def sende(*, an, betreff: str, text: str, anhaenge=None, cc=None,
          antwort_auf: str = "", kopie_ablegen: bool = True) -> dict:
    """Verschickt die Mail direkt von sr@ und legt eine Kopie in "Gesendet"."""
    cfg = konfig()
    _pruefe_konfig(cfg)
    if not an:
        raise ValueError("Empfaenger (an) fehlt — ohne Adresse kein Versand.")

    msg = baue_nachricht(an=an, betreff=betreff, text=text, anhaenge=anhaenge,
                         cc=cc, antwort_auf=antwort_auf, cfg=cfg)

    ctx = ssl.create_default_context()
    if cfg["smtp_port"] == 465:
        server = smtplib.SMTP_SSL(cfg["smtp_host"], cfg["smtp_port"],
                                  context=ctx, timeout=30)
    else:
        server = smtplib.SMTP(cfg["smtp_host"], cfg["smtp_port"], timeout=30)
        server.starttls(context=ctx)
    try:
        server.login(cfg["user"], cfg["passwort"])
        server.send_message(msg)
    finally:
        try:
            server.quit()
        except Exception:
            pass

    ordner = ""
    if kopie_ablegen:
        try:
            ordner = _ablegen(cfg, msg, GESENDET_NAMEN, "\\Sent", r"(\Seen)")
        except Exception:
            ordner = ""  # Versand ist erfolgt — die Kopie ist Kuer, kein Muss

    return {"status": "gesendet", "postfach": cfg["user"], "an": msg.get("To", ""),
            "betreff": betreff, "anhaenge": len(anhaenge or []),
            "kopie_in": ordner}
