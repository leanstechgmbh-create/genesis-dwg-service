"""GENESIS Service v4 — LEANS Tech GmbH.
DWG rein -> kleine Aenderungen (verschieben / ergaenzen / loeschen) -> DWG raus.
DWG<->DXF via LibreDWG (dwg2dxf / dxf2dwg). DXF direkt wird auch akzeptiert.
Aenderungen sind bewusst naeherungsweise (kleine Anpassungen, keine Neukonstruktion).
Kernlogik in dwg_core.py, Slack-Bot in slack_bot.py.
"""
import base64, os, traceback
from pathlib import Path
from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.responses import Response, JSONResponse, FileResponse
from dwg_core import have, modify_drawing
from slack_bot import router as slack_router, slack_ready
from mailer.core import versende, mail_bereit

app = FastAPI(title="GENESIS Service", version="4.0")
app.include_router(slack_router)
API_KEY = os.environ.get("GENESIS_API_KEY", "")

@app.get("/")
def health(request: Request):
    # Ueber die Website-Domain (profihaustechnik.de) liefert "/" direkt den Katalog.
    host = request.headers.get("host", "").lower()
    if "profihaustechnik" in host:
        return katalog()
    return {"service": "GENESIS", "status": "ok", "version": "4.0",
            "dwg_read": have("dwg2dxf"), "dwg_write": have("dxf2dwg"),
            "slack": slack_ready(), "mail_ready": mail_bereit()}

WEBSITE = Path(__file__).parent / "website"

def _website_datei(name: str, media: str):
    pfad = WEBSITE / name
    if not pfad.is_file():
        raise HTTPException(404, f"{name} nicht gefunden")
    return FileResponse(pfad, media_type=media)

@app.get("/katalog")
def katalog():
    """Materialkatalog-Webseite: Lueftung, Sanitaer, Heizung, Klima/Kaelte."""
    return _website_datei("index.html", "text/html")

@app.get("/artikel.json")
@app.get("/katalog/artikel.json")
def artikel_daten():
    """Komplette Artikeldatenbank (alle Varianten mit Artikelnummern)."""
    return _website_datei("artikel.json", "application/json")

@app.get("/bilder.json")
@app.get("/katalog/bilder.json")
def bilder_daten():
    """Produktfoto-URLs je Gewerk|Kategorie."""
    return _website_datei("bilder.json", "application/json")

@app.get("/amazon-export.csv")
@app.get("/katalog/amazon-export.csv")
def amazon_export():
    """Amazon-Flatfile-Basis: eine Zeile je SKU."""
    return _website_datei("amazon-export.csv", "text/csv")

_ARTIKEL_INDEX = None

def _artikel_index():
    """nr -> (Bezeichnung, Preis in Cent, Einheit). Preise IMMER serverseitig."""
    global _ARTIKEL_INDEX
    if _ARTIKEL_INDEX is None:
        import json
        daten = json.loads((WEBSITE / "artikel.json").read_text(encoding="utf-8"))
        _ARTIKEL_INDEX = {}
        for p in daten:
            for ausf, nr, cent in p["v"]:
                name = p["n"] if ausf == "Standard" else f"{p['n']} — {ausf}"
                _ARTIKEL_INDEX[nr] = (name, int(cent), p["e"])
    return _ARTIKEL_INDEX

@app.post("/kasse")
@app.post("/katalog/kasse")
async def kasse(request: Request):
    """Stripe-Checkout: Karte, Apple/Google Pay, Klarna, SEPA."""
    key = os.environ.get("STRIPE_SECRET_KEY", "")
    if not key:
        raise HTTPException(503, "Online-Zahlung noch nicht freigeschaltet — bitte 'Auf Rechnung bestellen' nutzen.")
    import stripe
    stripe.api_key = key
    b = await request.json()
    idx = _artikel_index()
    posten = []
    for e in (b.get("artikel") or [])[:100]:
        info = idx.get(str(e.get("nr", "")))
        menge = int(e.get("menge", 0))
        if not info or menge < 1:
            continue
        name, cent, _einheit = info
        posten.append({"quantity": min(menge, 999),
                       "price_data": {"currency": "eur", "unit_amount": cent,
                                      "product_data": {"name": f"{name} [{e['nr']}]"}}})
    if not posten:
        raise HTTPException(400, "Keine gueltigen Artikel im Warenkorb")
    proto = request.headers.get("x-forwarded-proto", "https")
    host = request.headers.get("host", "profihaustechnik.de")
    basis = f"{proto}://{host}"
    sitzung = stripe.checkout.Session.create(
        mode="payment", line_items=posten,
        shipping_address_collection={"allowed_countries": ["DE", "AT", "CH"]},
        success_url=basis + "/katalog?bestellt=1",
        cancel_url=basis + "/katalog")
    return {"url": sitzung.url}

@app.post("/bestellung")
@app.post("/katalog/bestellung")
async def bestellung(request: Request):
    """Kauf auf Rechnung: Bestellung per Gmail-SMTP an uns senden."""
    user = os.environ.get("GMAIL_USER", "")
    pw = os.environ.get("GMAIL_APP_PASSWORD", "")
    if not (user and pw):
        raise HTTPException(503, "Mailversand nicht konfiguriert (GMAIL_APP_PASSWORD fehlt)")
    b = await request.json()
    kunde = b.get("kunde") or {}
    if not (str(kunde.get("name", "")).strip() and str(kunde.get("adresse", "")).strip()):
        raise HTTPException(400, "Name und Lieferadresse sind Pflicht")
    idx = _artikel_index()
    zeilen, summe = [], 0
    for e in (b.get("artikel") or [])[:200]:
        info = idx.get(str(e.get("nr", "")))
        menge = int(e.get("menge", 0))
        if not info or menge < 1:
            continue
        name, cent, einheit = info
        summe += cent * menge
        zeilen.append(f"{menge} {einheit}  {e['nr']}  {name}  a {cent/100:.2f} EUR")
    if not zeilen:
        raise HTTPException(400, "Keine gueltigen Artikel im Warenkorb")
    text = ("Neue Bestellung (Kauf auf Rechnung) ueber profihaustechnik.de\n\n"
            + "\n".join(zeilen)
            + f"\n\nSumme: {summe/100:.2f} EUR inkl. MwSt., zzgl. Versand\n\n"
            + f"Kunde:  {kunde.get('name', '')}\nE-Mail: {kunde.get('mail', '')}\n"
            + f"Telefon: {kunde.get('tel', '')}\nLieferadresse: {kunde.get('adresse', '')}\n")
    import smtplib
    from email.message import EmailMessage
    m = EmailMessage()
    m["Subject"] = f"Bestellung profihaustechnik.de — {kunde.get('name', '')} — {summe/100:.2f} EUR"
    m["From"] = user
    m["To"] = user
    if kunde.get("mail"):
        m["Reply-To"] = str(kunde["mail"])
    m.set_content(text)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=20) as s:
        s.login(user, pw)
        s.send_message(m)
    return {"ok": True}

@app.post("/send-mails")
async def send_mails(request: Request, x_genesis_key: str = Header(default="")):
    """Verschickt die Klima-Anschreiben server-seitig per Gmail-SMTP.

    Body (JSON, alle Felder optional):
      send           bool   -> true = wirklich senden (Default false = Vorschau)
      limit          int    -> hoechstens N Mails (0 = alle)
      delay          float  -> Sekunden Pause zwischen Mails (Default 2)
      only_confirmed bool   -> nur Status 'bestaetigt'
      status         list   -> erlaubte Status, z.B. ["bestaetigt","zentral"]
      resend         bool   -> Sende-Protokoll ignorieren
    """
    if API_KEY and x_genesis_key != API_KEY:
        raise HTTPException(401, "Ungueltiger Key")
    try:
        b = await request.json()
    except Exception:
        b = {}
    status_filter = None
    if b.get("only_confirmed"):
        status_filter = {"bestaetigt"}
    elif b.get("status"):
        status_filter = {str(s).strip().lower() for s in b["status"]}
    try:
        return versende(
            send=bool(b.get("send", False)),
            limit=int(b.get("limit", 0)),
            delay=float(b.get("delay", 2.0)),
            status_filter=status_filter,
            resend=bool(b.get("resend", False)))
    except RuntimeError as e:
        raise HTTPException(400, str(e))

@app.post("/modify-dwg")
async def modify(request: Request, x_genesis_key: str = Header(default="")):
    if API_KEY and x_genesis_key != API_KEY:
        raise HTTPException(401, "Ungueltiger Key")
    try:
        b = await request.json()
        name = b.get("filename", "plan_bearbeitet")
        base = name.rsplit(".", 1)[0]
        is_dwg = bool(b.get("dwg_base64"))
        raw = b.get("dwg_base64") or b.get("dxf_base64")
        if not raw:
            raise HTTPException(400, "dwg_base64/dxf_base64 fehlt")
        if is_dwg and not have("dwg2dxf"):
            raise HTTPException(500, "DWG-Leser nicht verfuegbar")
        data, fname, media, fmt, log = modify_drawing(
            base64.b64decode(raw), is_dwg, base, b.get("elements", []))
        return Response(content=data, media_type=media,
            headers={"Content-Disposition": f'attachment; filename="{fname}"',
                     "X-Genesis-Log": " | ".join(log)[:500],
                     "X-Genesis-Format": fmt})
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e), "trace": traceback.format_exc()[-500:]})
