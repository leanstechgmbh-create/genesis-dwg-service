"""Slack-Integration fuer GENESIS Service — Claude-gestuetzter Bot.
@mention im Channel oder DM -> Claude antwortet im Thread.
Events-API-Endpoint mit HMAC-Signaturpruefung und Hintergrund-Verarbeitung,
damit Slack innerhalb von 3 Sekunden ein 200 erhaelt.
"""
import hashlib, hmac, json, os, re, time
import httpx
from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from anthropic import AsyncAnthropic

router = APIRouter()

SLACK_SIGNING_SECRET = os.environ.get("SLACK_SIGNING_SECRET", "")
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN", "")
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-opus-4-8")
CLAUDE_MAX_TOKENS = int(os.environ.get("CLAUDE_MAX_TOKENS", "4096"))
CLAUDE_SYSTEM = os.environ.get(
    "CLAUDE_SYSTEM_PROMPT",
    "Du bist der GENESIS-Assistent von LEANS Tech GmbH. Antworte praezise, "
    "freundlich und konkret. Sprich Deutsch, wenn nicht anders gewuenscht.",
)

_anthropic = AsyncAnthropic()  # liest ANTHROPIC_API_KEY aus der Umgebung
_seen_events: set[str] = set()  # Dedup gegen Slack-Retries

def slack_ready():
    return bool(SLACK_SIGNING_SECRET and SLACK_BOT_TOKEN)

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

async def _ask_claude(text: str) -> str:
    async with _anthropic.messages.stream(
        model=CLAUDE_MODEL,
        max_tokens=CLAUDE_MAX_TOKENS,
        system=CLAUDE_SYSTEM,
        messages=[{"role": "user", "content": text}],
    ) as stream:
        msg = await stream.get_final_message()
    answer = "".join(b.text for b in msg.content if b.type == "text").strip()
    return answer or "(keine Antwort erhalten)"

async def _post_message(channel: str, text: str, thread_ts):
    async with httpx.AsyncClient(timeout=30) as client:
        await client.post(
            "https://slack.com/api/chat.postMessage",
            headers={"Authorization": f"Bearer {SLACK_BOT_TOKEN}"},
            json={"channel": channel, "text": text, "thread_ts": thread_ts},
        )

async def _handle_event(event: dict):
    text = re.sub(r"<@[^>]+>", "", event.get("text", "")).strip()  # Bot-Mention entfernen
    channel = event.get("channel")
    thread_ts = event.get("thread_ts") or event.get("ts")
    if not text:
        answer = "Wie kann ich helfen?"
    else:
        try:
            answer = await _ask_claude(text)
        except Exception as e:
            answer = f"Fehler bei der Anfrage an Claude: {str(e)[:200]}"
    await _post_message(channel, answer, thread_ts)

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
        # Bot-eigene Nachrichten ignorieren -> keine Endlosschleifen
        if event.get("bot_id") or event.get("subtype"):
            return JSONResponse({"ok": True})
        # Retry-Dedup (Slack wiederholt bei Timeout)
        if event_id in _seen_events:
            return JSONResponse({"ok": True})
        if event_id:
            if len(_seen_events) > 5000:
                _seen_events.clear()
            _seen_events.add(event_id)
        etype = event.get("type")
        # Bei "message" nur DMs beantworten (sonst Doppelung mit app_mention)
        if etype == "app_mention" or (etype == "message" and event.get("channel_type") == "im"):
            background.add_task(_handle_event, event)

    return JSONResponse({"ok": True})
