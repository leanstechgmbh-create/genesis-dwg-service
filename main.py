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
def health():
    return {"service": "GENESIS", "status": "ok", "version": "4.0",
            "dwg_read": have("dwg2dxf"), "dwg_write": have("dxf2dwg"),
            "slack": slack_ready(), "mail_ready": mail_bereit()}

@app.get("/katalog")
def katalog():
    """Materialkatalog-Webseite: Lueftung, Sanitaer, Heizung, Klima/Kaelte."""
    seite = Path(__file__).parent / "website" / "index.html"
    if not seite.is_file():
        raise HTTPException(404, "Katalog nicht gefunden")
    return FileResponse(seite, media_type="text/html")

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
