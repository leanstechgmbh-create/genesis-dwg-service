"""Slack-Integration fuer GENESIS Service — Claude-gestuetzter Bot.

Zwei Faehigkeiten:
1. CHAT: @mention oder DM -> Claude antwortet im Thread (mit GENESIS-Wissen,
   Thread-Kontext).
2. PLAN-AENDERUNG: DWG/DXF-Datei in den Thread + Aenderung in normaler Sprache
   -> Claude erzeugt das GENESIS-`elements`-JSON -> dwg_core bearbeitet ->
   fertige Datei kommt zurueck in den Thread.

Events-API-Endpoint mit HMAC-Signaturpruefung; schwere Arbeit laeuft im
Hintergrund, damit Slack innerhalb von 3 Sekunden ein 200 erhaelt.
"""
import hashlib, hmac, json, os, re, time
import httpx
from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from anthropic import AsyncAnthropic

import dwg_core

router = APIRouter()

SLACK_SIGNING_SECRET = os.environ.get("SLACK_SIGNING_SECRET", "")
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN", "")
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-opus-4-8")
CLAUDE_MAX_TOKENS = int(os.environ.get("CLAUDE_MAX_TOKENS", "4096"))
CLAUDE_HISTORY = int(os.environ.get("CLAUDE_HISTORY", "20"))  # max. Thread-Nachrichten
AI_PROVIDER  = os.environ.get("AI_PROVIDER", "claude")   # "claude" oder "ollama"
OLLAMA_HOST  = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:7b")

# --- GENESIS-Wissen (Chat-System-Prompt) --------------------------------------
GENESIS_WISSEN = (
    "Du bist der GENESIS-Assistent von LEANS Tech GmbH. GENESIS bearbeitet "
    "Bauplaene (DWG/DXF) per kleiner, naeherungsweiser Aenderungen: Elemente "
    "verschieben, ergaenzen, loeschen oder Texte aendern — keine Neukonstruktion. "
    "Ablauf fuer Nutzer: DWG/DXF-Datei in diesen Thread hochladen und die "
    "gewuenschte Aenderung in normaler Sprache dazuschreiben (z.B. 'Zuluft-"
    "Auslass bei 1200,800 um 200mm nach rechts verschieben' oder 'neuen Zuluft-"
    "Auslass 250er bei 3000,1500 ergaenzen'). Ich erstelle dann automatisch die "
    "bearbeitete Datei. Ohne Datei beantworte ich Fragen rund um GENESIS und den "
    "Projektbau-Flow. Antworte praezise, freundlich und auf Deutsch, wenn nicht "
    "anders gewuenscht."
)
CLAUDE_SYSTEM = os.environ.get("CLAUDE_SYSTEM_PROMPT", GENESIS_WISSEN)

# --- Extraktion: natuerliche Sprache -> GENESIS-elements ----------------------
EXTRACT_SYSTEM = (
    "Du wandelst die in normaler Sprache beschriebenen Plan-Aenderungen in das "
    "GENESIS-`elements`-Format um und rufst dazu das Tool `dwg_aenderungen` auf. "
    "Koordinaten sind Zeichnungseinheiten als 'x,y'. Aktionen:\n"
    "- 'loeschen': per `layer` ODER `position`(+`radius`, Standard 150).\n"
    "- 'verschieben': `von` und `nach` (oder `offset` als 'dx,dy'); optional "
    "`layer`; Suchradius `radius` (Standard 200).\n"
    "- 'hinzufuegen': `position`, `element` (Bezeichnung), `masse`/`durchmesser`, "
    "optional `typ` ('zuluft'/'abluft'). Neue Geometrie kommt auf einen NEU-Layer.\n"
    "- 'text': `element` = Such-Text, `wert` = neuer Text.\n"
    "Vergib fortlaufende `nr`. Nur belegte Felder setzen. Wenn die Beschreibung "
    "fuer eine sichere Aenderung nicht ausreicht, gib eine leere Liste zurueck."
)
ELEMENTS_TOOL = {
    "name": "dwg_aenderungen",
    "description": "Strukturierte GENESIS-Plan-Aenderungen.",
    "input_schema": {
        "type": "object",
        "properties": {
            "elements": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "nr": {"type": "string"},
                        "aktion": {"type": "string",
                                   "description": "loeschen|verschieben|hinzufuegen|text"},
                        "layer": {"type": "string"},
                        "position": {"type": "string", "description": "x,y"},
                        "von": {"type": "string", "description": "x,y Ausgangspunkt"},
                        "nach": {"type": "string", "description": "x,y Zielpunkt"},
                        "offset": {"type": "string", "description": "dx,dy"},
                        "radius": {"type": "number"},
                        "element": {"type": "string"},
                        "wert": {"type": "string"},
                        "typ": {"type": "string"},
                        "masse": {"type": "string"},
                        "durchmesser": {"type": "string"},
                    },
                    "required": ["aktion"],
                },
            }
        },
        "required": ["elements"],
    },
}

try:
    _anthropic = AsyncAnthropic()  # liest ANTHROPIC_API_KEY aus der Umgebung
except Exception:
    _anthropic = None
_seen_events: set[str] = set()  # Dedup gegen Slack-Retries

def slack_ready():
    return bool(SLACK_SIGNING_SECRET and SLACK_BOT_TOKEN)

def _clean(text: str) -> str:
    return re.sub(r"<@[^>]+>", "", text or "").strip()  # Bot-Mention entfernen

def _verify_slack(body: bytes, timestamp: str, signature: str) -> bool:
    if not SLACK_SIGNING_SECRET:
        return False
    try:  # Replay-Schutz: Anfrage darf max. 5 Min alt sein
        if abs(time.time() - int(timestamp)) > 300:
            return False
    except (TypeError, ValueError):
        return False
    base = b"v0:" + timestamp.encode() + b":" + body
    mine = "v0=" + hmac.new(SLACK_SIGNING_SECRET.encode(), base, hashlib.sha256).hexdigest()
    return hmac.compare_digest(mine, signature or "")

# --- Slack-Helfer -------------------------------------------------------------
def _slack_auth():
    return {"Authorization": f"Bearer {SLACK_BOT_TOKEN}"}

async def _post_message(channel: str, text: str, thread_ts):
    async with httpx.AsyncClient(timeout=30) as client:
        await client.post("https://slack.com/api/chat.postMessage",
            headers=_slack_auth(),
            json={"channel": channel, "text": text, "thread_ts": thread_ts})

async def _fetch_thread(channel: str, thread_ts: str) -> list[dict]:
    """Thread-Verlauf als Claude-Nachrichtenliste (User/Assistant-Rollen)."""
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get("https://slack.com/api/conversations.replies",
            headers=_slack_auth(),
            params={"channel": channel, "ts": thread_ts, "limit": CLAUDE_HISTORY})
    msgs = r.json().get("messages", []) if r.is_success else []
    history = []
    for m in msgs:
        content = _clean(m.get("text", ""))
        if not content:
            continue
        history.append({"role": "assistant" if m.get("bot_id") else "user",
                        "content": content})
    while history and history[0]["role"] == "assistant":  # erster Turn muss user sein
        history.pop(0)
    return history

async def _download_slack_file(f: dict) -> bytes:
    url = f.get("url_private_download") or f.get("url_private")
    async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
        r = await client.get(url, headers=_slack_auth())
    return r.content

async def _upload_file(channel, thread_ts, filename, data, comment):
    """Datei in den Thread laden (files.getUploadURLExternal -> completeUploadExternal)."""
    async with httpx.AsyncClient(timeout=60) as client:
        g = await client.get("https://slack.com/api/files.getUploadURLExternal",
            headers=_slack_auth(),
            params={"filename": filename, "length": len(data)})
        gj = g.json()
        if not gj.get("ok"):
            await _post_message(channel, f"{comment}\n(Upload fehlgeschlagen: {gj.get('error')})", thread_ts)
            return
        await client.post(gj["upload_url"], content=data)
        await client.post("https://slack.com/api/files.completeUploadExternal",
            headers=_slack_auth(),
            json={"files": [{"id": gj["file_id"], "title": filename}],
                  "channel_id": channel, "thread_ts": thread_ts,
                  "initial_comment": comment})

# --- Ollama (lokal, kostenlos) ------------------------------------------------
async def _ask_ollama(messages: list[dict]) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [{"role": "system", "content": CLAUDE_SYSTEM}] + messages,
        "stream": False,
    }
    async with httpx.AsyncClient(base_url=OLLAMA_HOST, timeout=120) as c:
        r = await c.post("/api/chat", json=payload)
        r.raise_for_status()
    return r.json().get("message", {}).get("content", "").strip() or "(keine Antwort)"

async def _extract_elements_ollama(instruction: str) -> list[dict]:
    prompt = (
        EXTRACT_SYSTEM + "\n\n"
        "Eingabe: " + (instruction or "(keine Beschreibung)") + "\n\n"
        'Antworte NUR mit einem JSON-Objekt: {"elements": [{"nr":"1","aktion":"..."}]}'
    )
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "format": "json",
        "stream": False,
    }
    async with httpx.AsyncClient(base_url=OLLAMA_HOST, timeout=120) as c:
        r = await c.post("/api/chat", json=payload)
        r.raise_for_status()
    raw = r.json().get("message", {}).get("content", "")
    try:
        data = json.loads(raw) if isinstance(raw, str) else raw
        return data.get("elements", []) or []
    except Exception:
        return []

# --- Claude -------------------------------------------------------------------
async def _ask_claude(messages: list[dict]) -> str:
    if AI_PROVIDER == "ollama":
        return await _ask_ollama(messages)
    async with _anthropic.messages.stream(model=CLAUDE_MODEL, max_tokens=CLAUDE_MAX_TOKENS,
            system=CLAUDE_SYSTEM, messages=messages) as stream:
        msg = await stream.get_final_message()
    answer = "".join(b.text for b in msg.content if b.type == "text").strip()
    return answer or "(keine Antwort erhalten)"

async def _extract_elements(instruction: str) -> list[dict]:
    if AI_PROVIDER == "ollama":
        return await _extract_elements_ollama(instruction)
    resp = await _anthropic.messages.create(model=CLAUDE_MODEL, max_tokens=2048,
        system=EXTRACT_SYSTEM, tools=[ELEMENTS_TOOL],
        tool_choice={"type": "tool", "name": "dwg_aenderungen"},
        messages=[{"role": "user", "content": instruction or "(keine Beschreibung)"}])
    for b in resp.content:
        if b.type == "tool_use" and b.name == "dwg_aenderungen":
            return b.input.get("elements", []) or []
    return []

# --- Event-Verarbeitung -------------------------------------------------------
def _drawing_file(event: dict):
    for f in event.get("files", []) or []:
        name = (f.get("name") or "").lower()
        ftype = (f.get("filetype") or "").lower()
        if name.endswith((".dwg", ".dxf")) or ftype in ("dwg", "dxf"):
            return f
    return None

async def _handle_plan_change(event: dict, f: dict):
    channel = event.get("channel")
    thread_ts = event.get("thread_ts") or event.get("ts")
    instruction = _clean(event.get("text", ""))
    name = f.get("name") or "plan.dwg"
    base = name.rsplit(".", 1)[0]
    is_dwg = name.lower().endswith(".dwg") or (f.get("filetype") or "").lower() == "dwg"
    if is_dwg and not dwg_core.have("dwg2dxf"):
        await _post_message(channel, "DWG-Leser ist auf diesem Server nicht verfuegbar.", thread_ts)
        return
    await _post_message(channel, f"Verstanden — bearbeite *{name}* …", thread_ts)
    try:
        elements = await _extract_elements(instruction)
        if not elements:
            await _post_message(channel,
                "Ich konnte keine eindeutige Aenderung erkennen. Bitte praeziser "
                "beschreiben (Aktion, Position/Layer, ggf. Mass).", thread_ts)
            return
        raw = await _download_slack_file(f)
        data, fname, _media, fmt, log = dwg_core.modify_drawing(raw, is_dwg, base, elements)
        comment = f"Fertig ({fmt.upper()}). Aenderungen: " + " | ".join(log)
        await _upload_file(channel, thread_ts, fname, data, comment[:2900])
    except Exception as e:
        await _post_message(channel, f"Fehler bei der Bearbeitung: {str(e)[:300]}", thread_ts)

async def _handle_chat(event: dict):
    channel = event.get("channel")
    thread_ts = event.get("thread_ts") or event.get("ts")
    try:
        messages = await _fetch_thread(channel, thread_ts)
        if not messages:  # Fallback: nur die ausloesende Nachricht
            messages = [{"role": "user", "content": _clean(event.get("text", "")) or "Hallo"}]
        answer = await _ask_claude(messages)
    except Exception as e:
        answer = f"Fehler bei der Anfrage an Claude: {str(e)[:200]}"
    await _post_message(channel, answer, thread_ts)

async def _handle_event(event: dict):
    f = _drawing_file(event)
    if f:
        await _handle_plan_change(event, f)
    else:
        await _handle_chat(event)

@router.post("/slack/events")
async def slack_events(request: Request, background: BackgroundTasks):
    body = await request.body()
    payload = json.loads(body or "{}")

    # 1) URL-Verification (einmalig beim Einrichten der Events-API)
    if payload.get("type") == "url_verification":
        return PlainTextResponse(payload.get("challenge", ""))

    # 2) Signatur pruefen
    ts = request.headers.get("X-Slack-Request-Timestamp", "")
    sig = request.headers.get("X-Slack-Signature", "")
    if not _verify_slack(body, ts, sig):
        raise HTTPException(401, "Ungueltige Slack-Signatur")

    # 3) Event-Callback verarbeiten
    if payload.get("type") == "event_callback":
        event = payload.get("event", {})
        event_id = payload.get("event_id", "")
        subtype = event.get("subtype")
        # Bot-eigene Nachrichten ignorieren -> keine Endlosschleifen.
        # Subtypes ueberspringen, ausser Datei-Uploads (file_share).
        if event.get("bot_id") or (subtype and subtype != "file_share"):
            return JSONResponse({"ok": True})
        if event_id in _seen_events:  # Retry-Dedup
            return JSONResponse({"ok": True})
        if event_id:
            if len(_seen_events) > 5000:
                _seen_events.clear()
            _seen_events.add(event_id)
        etype = event.get("type")
        # app_mention im Channel, oder DM (message.im). Bei message: nur DMs.
        if etype == "app_mention" or (etype == "message" and event.get("channel_type") == "im"):
            background.add_task(_handle_event, event)

    return JSONResponse({"ok": True})
