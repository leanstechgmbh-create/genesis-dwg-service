#!/usr/bin/env python3
"""Legt eine Mail als Entwurf im IONOS-Postfach sr@ ab — direkt, ohne Deploy.

Zum Aufruf muessen IONOS_MAIL_USER und IONOS_MAIL_PASSWORT gesetzt sein
(z. B. in der .env oder als Umgebungsvariablen der Shell).

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
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mailer import ionos  # noqa: E402


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

    if not ionos.ionos_bereit():
        print("Fehler: IONOS_MAIL_USER / IONOS_MAIL_PASSWORT sind nicht gesetzt.",
              file=sys.stderr)
        return 3

    try:
        if a.senden:
            if not a.an:
                print("Fehler: --an ist beim Senden Pflicht.", file=sys.stderr)
                return 2
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
