"""GENESIS Service v4 — LEANS Tech GmbH.
DWG rein -> kleine Aenderungen (verschieben / ergaenzen / loeschen) -> DWG raus.
DWG<->DXF via LibreDWG (dwg2dxf / dxf2dwg). DXF direkt wird auch akzeptiert.
Aenderungen sind bewusst naeherungsweise (kleine Anpassungen, keine Neukonstruktion).
Kernlogik in dwg_core.py, Slack-Bot in slack_bot.py.
"""
import base64, os, traceback
from pathlib import Path
from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.responses import (Response, JSONResponse, FileResponse,
                               StreamingResponse, PlainTextResponse)
from dwg_core import have, modify_drawing
from slack_bot import router as slack_router, slack_ready
from mailer.core import versende, mail_bereit
from social_poster import (insta_bereit, youtube_bereit, post_instagram_reel,
                           post_youtube, post_nach_schluessel, lade_posts)
import ai_bus, gpt_bridge

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
            "slack": slack_ready(), "mail_ready": mail_bereit(),
            "instagram": insta_bereit(), "youtube": youtube_bereit(),
            "chatgpt": gpt_bridge.gpt_bereit(), "bus": ai_bus.bus_art()}

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

@app.post("/post-social")
def post_social(b: dict, x_genesis_key: str = Header(default="")):
    """Fertiges Video (per oeffentlicher URL) auf Instagram (Reel) und/oder YouTube (Short) posten.

    Body (JSON):
      video_url   str   -> Pflicht, oeffentliche https-URL der MP4-Datei
      caption     str   -> Text unter dem Instagram-Reel (+ YouTube-Beschreibung)
      title       str   -> YouTube-Titel (Default: erste Zeile der Caption)
      description str   -> eigene YouTube-Beschreibung (Default: caption)
      platforms   list  -> ["instagram","youtube"] (Default: beide)
      privacy     str   -> nur YouTube: "public"/"unlisted"/"private" (Default public)

    Antwort kann 1-3 Minuten dauern (Instagram verarbeitet das Video erst).
    """
    if API_KEY and x_genesis_key != API_KEY:
        raise HTTPException(401, "Ungueltiger Key")
    url = str(b.get("video_url", "")).strip()
    if not url.startswith("https://"):
        raise HTTPException(400, "video_url (https) fehlt")
    caption = str(b.get("caption", ""))
    titel = str(b.get("title") or caption.split("\n")[0][:95] or "Video")
    plattformen = [str(p).lower() for p in (b.get("platforms") or ["instagram", "youtube"])]
    fertig, fehler = [], []
    if "instagram" in plattformen:
        try:
            fertig.append(post_instagram_reel(url, caption))
        except Exception as e:
            fehler.append({"platform": "instagram", "error": str(e)})
    if "youtube" in plattformen:
        try:
            fertig.append(post_youtube(url, titel, str(b.get("description") or caption),
                                       str(b.get("privacy", "public"))))
        except Exception as e:
            fehler.append({"platform": "youtube", "error": str(e)})
    return {"ok": bool(fertig) and not fehler, "posted": fertig, "errors": fehler}

@app.get("/posts")
def posts_liste(x_genesis_key: str = Header(default="")):
    """Vorbereitete Posts aus posts.json auflisten (ohne zu posten)."""
    if API_KEY and x_genesis_key != API_KEY:
        raise HTTPException(401, "Ungueltiger Key")
    return {k: {"beschreibung": v.get("beschreibung", ""), "titel": v.get("titel", "")}
            for k, v in lade_posts().items()}

@app.post("/post-video")
def post_video(b: dict, x_genesis_key: str = Header(default="")):
    """Vorbereiteten Post aus posts.json veroeffentlichen.

    Body: {"video": 6}  oder  {"key": "video-6"}; optional platforms wie /post-social.
    Caption, Hashtags und Titel kommen fertig aus posts.json.
    """
    if API_KEY and x_genesis_key != API_KEY:
        raise HTTPException(401, "Ungueltiger Key")
    key = str(b.get("key") or "").strip()
    if not key and b.get("video") is not None:
        key = f"video-{int(b['video'])}"
    if not key:
        raise HTTPException(400, "key oder video (Nummer) fehlt")
    try:
        fertig, fehler = post_nach_schluessel(key, b.get("platforms"))
    except KeyError as e:
        raise HTTPException(404, str(e))
    return {"ok": bool(fertig) and not fehler, "key": key, "posted": fertig, "errors": fehler}

# --- LEANS OS: Nachrichten-Bus + ChatGPT-Bruecke ------------------------------
# Austausch mit anderen KI-Systemen laeuft ueber einen Ordner (ai_bus.py), nicht
# ueber einen direkten Draht. Diese Endpunkte sind die Bedienung dazu.
# Der Schluessel ist hier PFLICHT — ohne GENESIS_API_KEY bleiben sie geschlossen.

def _bus_key(header_key: str, query_key: str = ""):
    """Schluessel aus Header ODER Query pruefen.

    Query erlaubt, weil Pub/Sub-Push und Cloud Scheduler keine eigenen Header
    setzen koennen; die Push-URL gilt dann selbst als Geheimnis.
    """
    if not API_KEY:
        raise HTTPException(503, "GENESIS_API_KEY nicht gesetzt — Bus bleibt geschlossen")
    if header_key != API_KEY and query_key != API_KEY:
        raise HTTPException(401, "Ungueltiger Key")


@app.get("/bus/status")
async def bus_status(x_genesis_key: str = Header(default=""), key: str = ""):
    """Zustand des Nachrichtenordners: Ablage, offene Nachrichten."""
    _bus_key(x_genesis_key, key)
    return await ai_bus.status()


@app.post("/bus/tick")
async def bus_tick(request: Request, x_genesis_key: str = Header(default=""), key: str = ""):
    """Eingangsordner abarbeiten: lesen -> pruefen -> antworten -> quittieren.

    Aufrufbar per Cloud Scheduler (Poll, z.B. alle 30 s) oder per Pub/Sub-Push
    aus einem GCS-Ereignis (dann ~1-3 s nach Dateiablage = gefuehlte Echtzeit).
    Body wird nicht ausgewertet — der Ordner ist die Wahrheit, nicht der Trigger.
    """
    _bus_key(x_genesis_key, key)
    try:
        b = await request.json()
    except Exception:
        b = {}
    try:
        return await gpt_bridge.tick(int(b.get("limit", 0) or 0))
    except RuntimeError as e:
        raise HTTPException(400, str(e))


@app.post("/bus/senden")
async def bus_senden(b: dict, x_genesis_key: str = Header(default=""), key: str = ""):
    """Nachricht in den Ausgangsordner legen (von uns an ein anderes KI-System).

    Body: {"an": "chatgpt", "text": "...", "thread": "...", "typ": "frage"}
    """
    _bus_key(x_genesis_key, key)
    text = str(b.get("text", "")).strip()
    if not text:
        raise HTTPException(400, "text fehlt")
    n = ai_bus.baue(von="claude", an=str(b.get("an", "chatgpt")), text=text,
                    thread=str(b.get("thread", "")), typ=str(b.get("typ", "frage")),
                    titel=str(b.get("titel", "")))
    name = await ai_bus.schreibe(n, ai_bus.AUSGANG)
    return {"ok": True, "datei": name, "id": n["id"], "thread": n["thread"]}


@app.post("/ai/ask")
async def ai_ask(b: dict, x_genesis_key: str = Header(default=""), key: str = ""):
    """Gegenrichtung: ein anderes KI-System (z.B. ChatGPT-Action) fragt Claude.

    Body: {"text": "...", "von": "chatgpt", "thread": "..."}
    Antwort kommt synchron zurueck UND wird im Bus protokolliert.
    Aktionsaufforderungen werden erkannt und nicht ausgefuehrt, sondern zur
    Freigabe vorgelegt (siehe ai_bus.pruefe / gpt_bridge.BUS_SYSTEM).
    """
    _bus_key(x_genesis_key, key)
    try:
        n = ai_bus.pruefe({"von": str(b.get("von", "chatgpt")), "an": "claude",
                           "text": str(b.get("text", "")), "typ": "frage",
                           "thread": str(b.get("thread", ""))})
    except RuntimeError as e:
        raise HTTPException(400, str(e))
    antwort = await gpt_bridge.beantworte_bus(n)
    try:  # Protokoll ist Nebensache — eine Antwort darf daran nicht scheitern
        await ai_bus.quittiere(await ai_bus.schreibe(n, ai_bus.EINGANG), n,
                              "zur_freigabe" if n.get("verdacht") else "beantwortet")
        await ai_bus.schreibe(antwort, ai_bus.AUSGANG)
    except Exception:
        pass
    return {"ok": True, "thread": n["thread"], "zur_freigabe": bool(n.get("verdacht")),
            "antwort": antwort["text"]}


@app.get("/gpt/test")
async def gpt_test(key: str = "", frage: str = ""):
    """Browser-Test der ChatGPT-Bruecke — ohne Terminal bedienbar.

    Aufruf: /gpt/test?key=<GENESIS_API_KEY>            (Standard-Testfrage)
            /gpt/test?key=...&frage=eigene+Frage       (eigene Frage)
    Antwort kommt als einfacher Text direkt im Browserfenster.
    """
    _bus_key("", key)
    if not gpt_bridge.gpt_bereit():
        raise HTTPException(503, "OPENAI_API_KEY fehlt — ChatGPT-Bruecke nicht freigeschaltet")
    text = frage.strip() or ("Bestaetige in einem kurzen deutschen Satz, dass die "
                             "Verbindung zwischen GENESIS und dir funktioniert.")
    try:
        antwort = await gpt_bridge.frag_gpt([{"role": "user", "content": text[:2000]}])
    except RuntimeError as e:
        raise HTTPException(502, str(e))
    return PlainTextResponse(f"ChatGPT antwortet:\n\n{antwort}\n")


@app.post("/gpt/ask")
async def gpt_ask(b: dict, x_genesis_key: str = Header(default=""), key: str = ""):
    """Wir fragen ChatGPT. `stream: true` liefert die Antwort Stueck fuer Stueck."""
    _bus_key(x_genesis_key, key)
    text = str(b.get("text", "")).strip()
    if not text:
        raise HTTPException(400, "text fehlt")
    if not gpt_bridge.gpt_bereit():
        raise HTTPException(503, "OPENAI_API_KEY fehlt — ChatGPT-Bruecke nicht freigeschaltet")
    messages = [{"role": "user", "content": text}]
    if b.get("stream"):
        async def haeppchen():
            try:
                async for stueck in gpt_bridge.stream_gpt(messages):
                    yield stueck
            except RuntimeError as e:
                yield f"\n[Fehler: {e}]"
        return StreamingResponse(haeppchen(), media_type="text/plain; charset=utf-8")
    try:
        return {"ok": True, "antwort": await gpt_bridge.frag_gpt(messages)}
    except RuntimeError as e:
        raise HTTPException(502, str(e))


@app.post("/gpt/dialog")
async def gpt_dialog(b: dict, x_genesis_key: str = Header(default=""), key: str = ""):
    """Claude und ChatGPT diskutieren ein Thema; am Ende ein Fazit mit Empfehlung.

    Body: {"thema": "...", "runden": 3}
    """
    _bus_key(x_genesis_key, key)
    thema = str(b.get("thema", "")).strip()
    if not thema:
        raise HTTPException(400, "thema fehlt")
    try:
        beitraege = await gpt_bridge.dialog(thema, int(b.get("runden", 3)))
        return {"ok": True, "thema": thema, "beitraege": beitraege,
                "fazit": await gpt_bridge.fazit(thema, beitraege)}
    except RuntimeError as e:
        raise HTTPException(502, str(e))


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
