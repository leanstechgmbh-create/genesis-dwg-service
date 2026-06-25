"""GENESIS Service v4 — LEANS Tech GmbH.
DWG rein -> kleine Aenderungen (verschieben / ergaenzen / loeschen) -> DWG raus.
DWG<->DXF via LibreDWG (dwg2dxf / dxf2dwg). DXF direkt wird auch akzeptiert.
Aenderungen sind bewusst naeherungsweise (kleine Anpassungen, keine Neukonstruktion).
Kernlogik in dwg_core.py, Slack-Bot in slack_bot.py.
"""
import base64, os, traceback
from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.responses import Response, JSONResponse
from dwg_core import have, modify_drawing
from slack_bot import router as slack_router, slack_ready

app = FastAPI(title="GENESIS Service", version="4.0")
app.include_router(slack_router)
API_KEY = os.environ.get("GENESIS_API_KEY", "")

# Firmen- und Profildaten der LEANS Tech GmbH. Nach Marke gegliedert.
# Leere Werte werden in den Antworten automatisch ausgefiltert.
# Pflege zentral hier und in SOCIAL_MEDIA.md.
COMPANY = {
    "name":     "LEANS Tech GmbH",
    "website":  "https://www.leanstech-gmbh.de",
    "email":    "info@leanstech-gmbh.de",
    "phone":    "+49 170 8280836",
    "address":  "Berlepschstraße 165, 14165 Berlin",
    "github":   "https://github.com/leanstechgmbh-create",
}

# Profile je Marke. URLs aus dem offiziellen Impressum / Marketing-Material.
BRANDS = {
    "hkls": {  # LEANS HKLS — Heizung, Klima, Lueftung, Sanitaer
        "website":   "https://www.leanstechgmbh-hkls.de",
        "instagram": "https://www.instagram.com/leanstechhkls/",
        "youtube":   "",
        "facebook":  "",
        "whatsapp":  "",
    },
    "klima": {  # LEANS Klima — Klimatechnik
        "website":   "https://www.leanstech-klima.de",
        "instagram": "https://www.instagram.com/leansklima/",
        "youtube":   "https://www.youtube.com/@leansklima",
        "facebook":  "https://www.facebook.com/profile.php?id=61591323627434",
        "whatsapp":  "https://wa.me/4915216607036",
    },
}

def _clean_links(d: dict) -> dict:
    """Nur befuellte Eintraege (leere Platzhalter werden weggelassen)."""
    return {k: v for k, v in d.items() if v}

def _social() -> dict:
    return {"company": _clean_links(COMPANY),
            "brands": {name: _clean_links(links) for name, links in BRANDS.items()}}

@app.get("/")
def health():
    return {"service": "GENESIS", "status": "ok", "version": "4.0",
            "dwg_read": have("dwg2dxf"), "dwg_write": have("dxf2dwg"),
            "slack": slack_ready(), "company": COMPANY["name"],
            "social": _social()}

@app.get("/social")
def social():
    """Offizielle Web-/Social-Media-Profile der LEANS Tech GmbH (je Marke)."""
    return _social()

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
