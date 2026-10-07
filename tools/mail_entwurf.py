#!/usr/bin/env python3
"""Legt eine Mail als Entwurf im IONOS-Postfach sr@ ab (oder verschickt sie).

Zwei Wege, automatisch gewaehlt:

  direkt        IONOS_MAIL_USER und IONOS_MAIL_PASSWORT sind gesetzt -> SMTP/IMAP
                direkt zu IONOS (z. B. am eigenen Rechner).
  ueber Dienst  nur GENESIS_API_KEY ist gesetzt -> die Mail geht ueber den
                eigenen Cloud-Run-Dienst (/mail/entwurf bzw. /mail/senden).
                Das ist der Weg fuer Claude-Cloud-Sitzungen: dort sind
                Mail-Ports gesperrt, HTTPS zum Dienst aber freischaltbar.
                Anhaenge werden aus den Dateien gelesen und kodiert — nichts
                muss von Hand abgetippt werden.

Optional: GENESIS_URL (Standard: die Cloud-Run-Adresse des Dienstes),
--ueber-dienst erzwingt den zweiten Weg.

Beispiel — Transparenzregister-Mail mit fuenf Anhaengen:

    python3 tools/mail_entwurf.py \
        --betreff "Nutzerkonto Transparenzregister - LEANS Tech GmbH" \
        --text-datei mailtext.txt \
        --an service@transparenzregister.de \
        --anhang Berechtigungsnachweis.pdf --anhang Gesellschafterliste.pdf

Ohne --an bleibt das Empfaengerfeld leer; die Adresse traegt man dann direkt
im Postfach ein. Mit --senden wird statt des Entwurfs sofort verschickt.
"""
import argparse
import base64
import json
import os
import ssl
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mailer import ionos  # noqa: E402

DIENST_URL = "https://genesis-dwg-service-24363325360.europe-west3.run.app"


def ueber_dienst(*, senden: bool, an: str, betreff: str, text: str,
                 anhaenge: list, cc: str, antwort_auf: str) -> dict:
    """Schickt die Mail ueber /mail/entwurf bzw. /mail/senden des Dienstes."""
    schluessel = os.environ.get("GENESIS_API_KEY", "")
    if not schluessel:
        raise RuntimeError("GENESIS_API_KEY ist nicht gesetzt.")
    basis = os.environ.get("GENESIS_URL", DIENST_URL).rstrip("/")
    body = {
        "betreff": betreff, "text": text, "an": an,
        "cc": cc or None, "antwort_auf": antwort_auf,
        "anhaenge": [
            {"dateiname": a["dateiname"],
             "inhalt_base64": base64.b64encode(Path(a["pfad"]).read_bytes()).decode()}
            for a in anhaenge],
    }
    anfrage = urllib.request.Request(
        f"{basis}/mail/{'senden' if senden else 'entwurf'}",
        data=json.dumps(body).encode(), method="POST",
        headers={"Content-Type": "application/json", "x-genesis-key": schluessel})
    ca = os.environ.get("SSL_CERT_FILE") or os.environ.get("REQUESTS_CA_BUNDLE")
    kontext = ssl.create_default_context(cafile=ca) if ca else None
    try:
        with urllib.request.urlopen(anfrage, timeout=120, context=kontext) as antwort:
            return json.loads(antwort.read() or b"{}")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Dienst antwortet {e.code}: {e.read().decode(errors='replace')}")


def main() -> int:
    p = argparse.ArgumentParser(description="Mail-Entwurf in sr@ ablegen")
    p.add_argument("--betreff", required=True)
    p.add_argument("--text", default="", help="Mailtext direkt als Argument")
    p.add_argument("--text-datei", default="", help="Datei mit dem Mailtext")
    p.add_argument("--an", default="", help="Empfaenger (Komma-getrennt)")
    p.add_argument("--cc", default="")
    p.add_argument("--antwort-auf", default="", help="Message-ID der Ursprungsmail")
    p.add_argument("--anhang", action="append", default=[],
                   help="Pfad zu einer Anhangsdatei (mehrfach moeglich)")
    p.add_argument("--senden", action="store_true",
                   help="Statt Entwurf sofort verschicken (nur nach Freigabe!)")
    p.add_argument("--ueber-dienst", action="store_true",
                   help="Ueber den Cloud-Run-Dienst statt direkt zu IONOS")
    a = p.parse_args()

    if a.text_datei:
        text = Path(a.text_datei).read_text(encoding="utf-8")
    elif a.text:
        text = a.text
    else:
        print("Fehler: --text oder --text-datei angeben.", file=sys.stderr)
        return 2

    anhaenge = []
    for pfad in a.anhang:
        datei = Path(pfad)
        if not datei.is_file():
            print(f"Fehler: Anhang nicht gefunden: {datei}", file=sys.stderr)
            return 2
        anhaenge.append({"pfad": str(datei), "dateiname": datei.name})

    dienst = a.ueber_dienst or (not ionos.ionos_bereit()
                                and bool(os.environ.get("GENESIS_API_KEY")))
    if not dienst and not ionos.ionos_bereit():
        print("Fehler: Weder IONOS_MAIL_USER / IONOS_MAIL_PASSWORT noch "
              "GENESIS_API_KEY sind gesetzt.", file=sys.stderr)
        return 3
    if a.senden and not a.an:
        print("Fehler: --an ist beim Senden Pflicht.", file=sys.stderr)
        return 2

    try:
        if dienst:
            ergebnis = ueber_dienst(senden=a.senden, an=a.an, betreff=a.betreff,
                                    text=text, anhaenge=anhaenge, cc=a.cc,
                                    antwort_auf=a.antwort_auf)
        elif a.senden:
            ergebnis = ionos.sende(an=a.an, betreff=a.betreff, text=text,
                                   anhaenge=anhaenge, cc=a.cc or None,
                                   antwort_auf=a.antwort_auf)
        else:
            ergebnis = ionos.entwurf(an=a.an, betreff=a.betreff, text=text,
                                     anhaenge=anhaenge, cc=a.cc or None,
                                     antwort_auf=a.antwort_auf)
    except Exception as e:
        print(f"Fehler: {e}", file=sys.stderr)
        return 1

    for schluessel, wert in ergebnis.items():
        print(f"{schluessel}: {wert}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
