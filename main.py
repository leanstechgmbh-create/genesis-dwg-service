"""GENESIS Service v4 — LEANS Tech GmbH.
DWG rein -> kleine Aenderungen (verschieben / ergaenzen / loeschen) -> DWG raus.
DWG<->DXF via LibreDWG (dwg2dxf / dxf2dwg). DXF direkt wird auch akzeptiert.
Aenderungen sind bewusst naeherungsweise (kleine Anpassungen, keine Neukonstruktion).
"""
import base64, os, subprocess, tempfile, traceback, math
from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.responses import Response, JSONResponse
import ezdxf
from slack_bot import router as slack_router, slack_ready

app = FastAPI(title="GENESIS Service", version="4.0")
app.include_router(slack_router)
API_KEY = os.environ.get("GENESIS_API_KEY", "")

def have(cmd):
    from shutil import which
    return which(cmd) is not None

def run(cmd, timeout=180):
    return subprocess.run(cmd, check=True, timeout=timeout, capture_output=True)

def dwg_to_dxf(dwg, dxf):
    run(["dwg2dxf", "-y", "-o", dxf, dwg])

def dxf_to_dwg(dxf, dwg):
    # LibreDWG dxf2dwg (experimentell) -> R2018
    run(["dxf2dwg", "-y", "-o", dwg, dxf])

def _pt(s, d=(0.0, 0.0)):
    try:
        v = [float(x) for x in str(s).replace(";", ",").split(",")[:2]]
        return (v[0], v[1])
    except Exception:
        return d

def _near(e, x, y, r):
    try:
        p = None
        t = e.dxftype()
        if t in ("TEXT", "MTEXT"):
            p = e.dxf.insert
        elif t == "CIRCLE":
            p = e.dxf.center
        elif t == "LINE":
            p = e.dxf.start
        elif t == "INSERT":
            p = e.dxf.insert
        if p is None:
            return False
        return math.hypot(p[0] - x, p[1] - y) <= r
    except Exception:
        return False

def apply_changes(dxf_path, elements):
    doc = ezdxf.readfile(dxf_path)
    msp = doc.modelspace()
    log = []
    for el in elements:
        a = (el.get("aktion") or "").lower()
        nr = el.get("nr", "?")
        ly = el.get("layer", "")
        try:
            # ----- LOESCHEN -----
            if a.startswith(("loesch", "lösch", "delete", "entfern", "rausstr")):
                cnt = 0
                if ly:
                    for e in list(msp.query(f'*[layer=="{ly}"]')):
                        msp.delete_entity(e); cnt += 1
                else:
                    x, y = _pt(el.get("position"))
                    r = float(el.get("radius", 150))
                    for e in list(msp):
                        if _near(e, x, y, r):
                            msp.delete_entity(e); cnt += 1
                log.append(f"#{nr} geloescht: {cnt}")
            # ----- VERSCHIEBEN -----
            elif a.startswith(("verschieb", "verschob", "move", "rueck", "rück")):
                vx, vy = _pt(el.get("von"))
                nx, ny = _pt(el.get("position") or el.get("nach"))
                dx, dy = (nx - vx, ny - vy)
                if el.get("offset"):
                    dx, dy = _pt(el.get("offset"))
                r = float(el.get("radius", 200))
                cnt = 0
                targets = []
                if ly:
                    targets = list(msp.query(f'*[layer=="{ly}"]'))
                else:
                    targets = [e for e in msp if _near(e, vx, vy, r)]
                for e in targets:
                    try:
                        e.translate(dx, dy, 0); cnt += 1
                    except Exception:
                        pass
                log.append(f"#{nr} verschoben: {cnt} um ({dx:.0f},{dy:.0f})")
            # ----- HINZUFUEGEN (in der Naehe) -----
            elif a.startswith(("hinzu", "add", "neu", "ergaenz", "ergänz")):
                nl = ly or ("Zuluft_NEU" if "zu" in (el.get("typ", "").lower()) else "GENESIS_NEU")
                if nl not in doc.layers:
                    doc.layers.add(nl)
                x, y = _pt(el.get("position"))
                groesse = el.get("masse") or el.get("groesse") or el.get("durchmesser") or ""
                msp.add_circle((x, y), float(el.get("radius", 50)), dxfattribs={"layer": nl})
                txt = f"NEU {el.get('element','')} {groesse}".strip()
                t = msp.add_text(txt, dxfattribs={"layer": nl, "height": 25})
                t.set_placement((x + 60, y))
                log.append(f"#{nr} ergaenzt '{el.get('element','')}' @{x:.0f},{y:.0f}")
            # ----- TEXT -----
            elif a.startswith("text"):
                tg = (el.get("element") or "").replace(" ", "")
                neu = el.get("wert") or el.get("element") or ""
                f = False
                for t in msp.query("TEXT MTEXT"):
                    c = t.dxf.text if t.dxftype() == "TEXT" else t.text
                    if tg and tg in c.replace(" ", ""):
                        (setattr(t.dxf, "text", neu) if t.dxftype() == "TEXT" else setattr(t, "text", neu)); f = True
                log.append(f"#{nr} Text->'{neu}'" if f else f"#{nr} Text n/a")
            else:
                log.append(f"#{nr} Aktion '{a}' unbekannt")
        except Exception as e:
            log.append(f"#{nr} FEHLER:{str(e)[:50]}")
    doc.saveas(dxf_path)
    return log

@app.get("/")
def health():
    return {"service": "GENESIS", "status": "ok", "version": "4.0",
            "dwg_read": have("dwg2dxf"), "dwg_write": have("dxf2dwg"),
            "slack": slack_ready()}

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
        with tempfile.TemporaryDirectory() as t:
            dxf = os.path.join(t, "w.dxf")
            if is_dwg:
                if not have("dwg2dxf"):
                    raise HTTPException(500, "DWG-Leser nicht verfuegbar")
                din = os.path.join(t, "in.dwg")
                open(din, "wb").write(base64.b64decode(raw))
                dwg_to_dxf(din, dxf)
            else:
                open(dxf, "wb").write(base64.b64decode(raw))
            log = apply_changes(dxf, b.get("elements", []))
            # Ausgabe
            if is_dwg and have("dxf2dwg"):
                try:
                    dout = os.path.join(t, "out.dwg")
                    dxf_to_dwg(dxf, dout)
                    data = open(dout, "rb").read()
                    return Response(content=data, media_type="image/vnd.dwg",
                        headers={"Content-Disposition": f'attachment; filename="{base}.dwg"',
                                 "X-Genesis-Log": " | ".join(log)[:500],
                                 "X-Genesis-Format": "dwg"})
                except Exception as e:
                    log.append(f"DWG-Schreiben fehlgeschlagen, DXF-Fallback: {str(e)[:40]}")
            data = open(dxf, "rb").read()
            return Response(content=data, media_type="application/dxf",
                headers={"Content-Disposition": f'attachment; filename="{base}.dxf"',
                         "X-Genesis-Log": " | ".join(log)[:500],
                         "X-Genesis-Format": "dxf"})
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e), "trace": traceback.format_exc()[-500:]})
