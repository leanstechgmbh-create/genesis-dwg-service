"""GENESIS DXF Service — LEANS Tech GmbH — ezdxf, ohne LibreDWG (stabil)."""
import base64, os, tempfile, traceback
from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.responses import Response, JSONResponse
import ezdxf

app = FastAPI(title="GENESIS DXF Service", version="3.0")
API_KEY = os.environ.get("GENESIS_API_KEY", "")

def apply_changes(dxf_path, elements):
    doc = ezdxf.readfile(dxf_path); msp = doc.modelspace(); log = []
    for el in elements:
        a = (el.get("aktion") or "").lower(); nr = el.get("nr", "?")
        try:
            if a.startswith("text"):
                tg = (el.get("element") or "").replace(" ", "")
                neu = el.get("wert") or el.get("element") or ""
                f = False
                for t in msp.query("TEXT MTEXT"):
                    c = t.dxf.text if t.dxftype()=="TEXT" else t.text
                    if tg and tg in c.replace(" ", ""):
                        (setattr(t.dxf,"text",neu) if t.dxftype()=="TEXT" else setattr(t,"text",neu)); f=True
                log.append(f"#{nr} Text->'{neu}'" if f else f"#{nr} Text n/a")
            elif a.startswith(("loesch","l\u00f6sch","delete","entfern")):
                ly = el.get("layer",""); cnt=0
                for e in list(msp.query(f'*[layer=="{ly}"]')): msp.delete_entity(e); cnt+=1
                log.append(f"#{nr} del {cnt}@'{ly}'")
            elif a.startswith(("hinzu","add","neu")):
                ly = el.get("layer","GENESIS_NEU")
                if ly not in doc.layers: doc.layers.add(ly)
                try: x,y=[float(v) for v in str(el.get("position","0,0")).split(",")[:2]]
                except: x,y=0.0,0.0
                msp.add_circle((x,y),50,dxfattribs={"layer":ly})
                n=msp.add_text(f"NEU: {el.get('element','')} {el.get('masse','')}".strip(),
                               dxfattribs={"layer":ly,"height":25}); n.set_placement((x+60,y))
                log.append(f"#{nr} add '{el.get('element','')}'@{x},{y}")
        except Exception as e:
            log.append(f"#{nr} FEHLER:{str(e)[:60]}")
    doc.saveas(dxf_path); return log

@app.get("/")
def health(): return {"service":"GENESIS DXF","status":"ok","version":"3.0","engine":"ezdxf"}

@app.post("/modify-dwg")
async def modify(request: Request, x_genesis_key: str = Header(default="")):
    if API_KEY and x_genesis_key != API_KEY:
        raise HTTPException(401, "Ungueltiger Key")
    try:
        b = await request.json()
        filename = b.get("filename","plan_bearbeitet.dxf")
        raw = b.get("dxf_base64") or b.get("dwg_base64")
        if not raw: raise HTTPException(400,"dxf_base64/dwg_base64 fehlt")
        with tempfile.TemporaryDirectory() as t:
            dxf=os.path.join(t,"m.dxf")
            open(dxf,"wb").write(base64.b64decode(raw))
            try:
                log=apply_changes(dxf, b.get("elements",[]))
            except Exception:
                raise HTTPException(422,"Keine gueltige DXF. Plan in AutoCAD als DXF exportieren (Speichern unter -> DXF) und hochladen.")
            data=open(dxf,"rb").read()
        return Response(content=data, media_type="application/dxf",
            headers={"Content-Disposition":f'attachment; filename="{filename}"',
                     "X-Genesis-Log":" | ".join(log)[:500]})
    except HTTPException: raise
    except Exception as e:
        return JSONResponse(status_code=500, content={"error":str(e),"trace":traceback.format_exc()[-600:]})
