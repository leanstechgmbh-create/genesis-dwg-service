"""GENESIS Kernlogik — DWG/DXF rein -> kleine Aenderungen -> DWG/DXF raus.
Geteilt von der HTTP-API (main.py) und dem Slack-Bot (slack_bot.py).
DWG<->DXF via LibreDWG (dwg2dxf / dxf2dwg). DXF direkt wird auch akzeptiert.
"""
import os, subprocess, tempfile, math
import ezdxf

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

def modify_drawing(raw: bytes, is_dwg: bool, base: str, elements: list):
    """Wendet die Aenderungen an. Liefert (data, filename, media_type, format, log).
    Bei DWG-Eingabe wird, wenn moeglich, wieder DWG ausgegeben (sonst DXF-Fallback)."""
    with tempfile.TemporaryDirectory() as t:
        dxf = os.path.join(t, "w.dxf")
        if is_dwg:
            if not have("dwg2dxf"):
                raise RuntimeError("DWG-Leser nicht verfuegbar")
            din = os.path.join(t, "in.dwg")
            open(din, "wb").write(raw)
            dwg_to_dxf(din, dxf)
        else:
            open(dxf, "wb").write(raw)
        log = apply_changes(dxf, elements)
        if is_dwg and have("dxf2dwg"):
            try:
                dout = os.path.join(t, "out.dwg")
                dxf_to_dwg(dxf, dout)
                return open(dout, "rb").read(), f"{base}.dwg", "image/vnd.dwg", "dwg", log
            except Exception as e:
                log.append(f"DWG-Schreiben fehlgeschlagen, DXF-Fallback: {str(e)[:40]}")
        return open(dxf, "rb").read(), f"{base}.dxf", "application/dxf", "dxf", log
