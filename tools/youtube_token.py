"""Einmalig LOKAL am eigenen PC ausfuehren: holt das YouTube-Refresh-Token.

Aufruf:
    python tools/youtube_token.py CLIENT_ID CLIENT_SECRET

Der Browser oeffnet sich, du meldest dich mit dem YouTube-Konto an und stimmst zu.
Danach druckt das Skript die Zeile  YT_REFRESH_TOKEN=...  zum Kopieren.
Braucht nur Python-Standardbibliothek (keine Installation noetig).
"""
import json, sys, urllib.parse, urllib.request, webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = 8765
REDIRECT = f"http://localhost:{PORT}"
SCOPE = "https://www.googleapis.com/auth/youtube.upload"

def main():
    if len(sys.argv) != 3:
        print("Aufruf: python tools/youtube_token.py CLIENT_ID CLIENT_SECRET")
        sys.exit(1)
    cid, csec = sys.argv[1], sys.argv[2]
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode({
        "client_id": cid, "redirect_uri": REDIRECT, "response_type": "code",
        "scope": SCOPE, "access_type": "offline", "prompt": "consent"})
    print("Browser oeffnet sich — mit dem YouTube-Konto anmelden und zustimmen ...")
    webbrowser.open(url)

    ergebnis = {}
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            ergebnis["code"] = (q.get("code") or [""])[0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("<h2>Fertig! Fenster schliessen und zurueck ins Terminal.</h2>".encode())
        def log_message(self, *a):  # keine Log-Ausgabe
            pass
    HTTPServer(("localhost", PORT), Handler).handle_request()

    if not ergebnis.get("code"):
        print("FEHLER: keine Freigabe erhalten — bitte nochmal versuchen.")
        sys.exit(1)
    daten = urllib.parse.urlencode({
        "code": ergebnis["code"], "client_id": cid, "client_secret": csec,
        "redirect_uri": REDIRECT, "grant_type": "authorization_code"}).encode()
    with urllib.request.urlopen("https://oauth2.googleapis.com/token", daten) as r:
        tok = json.loads(r.read())
    if "refresh_token" not in tok:
        print("FEHLER: kein Refresh-Token in der Antwort:", tok)
        sys.exit(1)
    print("\nGeschafft! Diese 3 Zeilen als Umgebungsvariablen in Cloud Run eintragen:\n")
    print(f"YT_CLIENT_ID={cid}")
    print(f"YT_CLIENT_SECRET={csec}")
    print(f"YT_REFRESH_TOKEN={tok['refresh_token']}")

if __name__ == "__main__":
    main()
