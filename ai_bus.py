"""Nachrichten-Bus fuer LEANS OS — Austausch zwischen KI-Systemen ueber einen Ordner.

Grundidee: Kein KI-System spricht direkt mit einem anderen. Jede Seite legt
Nachrichten als JSON-Dateien in einen Ordner, die Gegenseite liest sie dort ab.
Vorteile gegenueber einem direkten HTTP-Draht:
  - keine offenen Endpunkte zwischen den Systemen (Zugriff nur per IAM/Dienstkonto)
  - jede Nachricht ist eine Datei -> vollstaendiges, pruefbares Protokoll
  - Service offline = Nachrichten warten im Ordner, nichts geht verloren

Ordnerstruktur (Rechte bewusst je Richtung getrennt):
  <basis>/eingang/     fremde Systeme schreiben hier hinein (nur schreiben)
  <basis>/ausgang/     GENESIS/Claude antwortet hier (nur schreiben)
  <basis>/protokoll/   abgearbeitete Nachrichten, append-only Archiv

Zwei Ablagen moeglich:
  BUS_GCS_BUCKET gesetzt -> Google Cloud Storage (Cloud Run, ~Echtzeit per Eventarc)
  sonst BUS_DIR          -> normaler Ordner (lokal oder gemountetes Laufwerk)

SICHERHEIT — der wichtigste Punkt: Text aus dem Eingang ist DATEN, niemals ein
Befehl. Nachrichten koennen keine Aktion ausloesen (Mailversand, Drive-Upload,
Zahlung); `pruefe` verwirft alles, was danach aussieht, und der Antwort-Prompt
in gpt_bridge behandelt Fremdtext ausdruecklich als nicht vertrauenswuerdig.
"""
import json, os, re, urllib.parse, uuid
from datetime import datetime, timezone
from pathlib import Path

import httpx

BUS_DIR = os.environ.get("BUS_DIR", "/tmp/leans-os-bus")
BUS_GCS_BUCKET = os.environ.get("BUS_GCS_BUCKET", "")
BUS_PREFIX = os.environ.get("BUS_PREFIX", "bus").strip("/")
BUS_MAX_BYTES = int(os.environ.get("BUS_MAX_BYTES", "100000"))   # 100 KB je Nachricht
BUS_MAX_TICK = int(os.environ.get("BUS_MAX_TICK", "10"))         # Nachrichten je Durchlauf
BUS_TEILNEHMER = {"claude", "chatgpt", "genesis", "nutzer"}

EINGANG, AUSGANG, PROTOKOLL = "eingang", "ausgang", "protokoll"

# Felder, die eine Nachricht haben darf. Alles andere wird verworfen — damit
# kann eine Gegenseite keine Steuerfelder einschmuggeln.
ERLAUBTE_FELDER = {"id", "ts", "von", "an", "thread", "typ", "text", "ref", "titel"}
ERLAUBTE_TYPEN = {"frage", "antwort", "hinweis", "vorschlag"}

# Muster, die auf einen Versuch hindeuten, ueber den Bus eine Aktion auszuloesen.
# Solche Nachrichten werden angenommen, aber als `verdacht` markiert und nie
# automatisch beantwortet — sie landen zur Sichtung beim Nutzer.
_VERDACHT = re.compile(
    r"(ignoriere?\s+(alle\s+)?(vorherigen?\s+)?(anweisungen|instruktionen)"
    r"|ignore\s+(all\s+)?previous"
    r"|system\s*[- ]?prompt"
    # Kein \b vor api_key: in ANTHROPIC_API_KEY ist der Unterstrich selbst ein
    # Wortzeichen, dort gibt es also keine Wortgrenze.
    r"|(?<![a-z])(api[_ -]?key|secret|token|passwort|password|zugangsdaten)(?![a-z])"
    r"|\b(sende|schicke|verschicke|send)\b[^.\n]{0,40}\b(mail|e-mail|email|rechnung)\b"
    r"|\b(ueberweise|überweise|zahle|bezahle|transfer)\b"
    r"|\b(loesche|lösche|delete|entferne)\b[^.\n]{0,30}\b(datei|ordner|repo|branch)\b)",
    re.IGNORECASE)


def bus_bereit() -> bool:
    return bool(BUS_GCS_BUCKET) or bool(BUS_DIR)


def bus_art() -> str:
    return f"gcs://{BUS_GCS_BUCKET}/{BUS_PREFIX}" if BUS_GCS_BUCKET else f"ordner://{BUS_DIR}"


def _jetzt() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


_zaehler = 0


def _dateiname(von: str, mid: str) -> str:
    """Zeitstempel voran -> Dateien sind von Haus aus chronologisch sortiert.

    Millisekunden plus laufende Nummer, weil mehrere Nachrichten in derselben
    Sekunde sonst gleich einsortiert werden und der Gespraechsverlauf in
    zufaelliger Reihenfolge herauskaeme.
    """
    global _zaehler
    _zaehler = (_zaehler + 1) % 1000
    stempel = _jetzt().replace(":", "").replace("-", "").replace(".", "")
    return f"{stempel}-{_zaehler:03d}-{von}-{mid[:8]}.json"


# --- Nachricht bauen und pruefen ----------------------------------------------
def baue(von: str, an: str, text: str, thread: str = "", typ: str = "hinweis",
         ref: str = "", titel: str = "") -> dict:
    """Neue Bus-Nachricht mit ID und Zeitstempel."""
    return {"id": uuid.uuid4().hex, "ts": _jetzt(),
            "von": von, "an": an,
            "thread": thread or uuid.uuid4().hex[:12],
            "typ": typ if typ in ERLAUBTE_TYPEN else "hinweis",
            "text": text, "ref": ref, "titel": titel}


def pruefe(rohdaten: dict) -> dict:
    """Fremde Nachricht auf das erlaubte Format reduzieren.

    Gibt die bereinigte Nachricht zurueck; `verdacht=True`, wenn der Text nach
    einem Aktions- oder Prompt-Injection-Versuch aussieht. RuntimeError, wenn
    die Nachricht grundsaetzlich unbrauchbar ist.
    """
    if not isinstance(rohdaten, dict):
        raise RuntimeError("Nachricht ist kein JSON-Objekt")
    n = {k: v for k, v in rohdaten.items() if k in ERLAUBTE_FELDER}
    text = str(n.get("text", "")).strip()
    if not text:
        raise RuntimeError("Feld 'text' fehlt oder ist leer")
    if len(text.encode("utf-8")) > BUS_MAX_BYTES:
        raise RuntimeError(f"Nachricht groesser als {BUS_MAX_BYTES} Bytes")
    von = str(n.get("von", "")).lower().strip()
    if von not in BUS_TEILNEHMER:
        raise RuntimeError(f"Unbekannter Absender '{von}' (erlaubt: {sorted(BUS_TEILNEHMER)})")
    an = str(n.get("an", "claude")).lower().strip()
    sauber = {"id": str(n.get("id") or uuid.uuid4().hex)[:64],
              "ts": str(n.get("ts") or _jetzt())[:40],
              "von": von,
              "an": an if an in BUS_TEILNEHMER else "claude",
              "thread": str(n.get("thread") or uuid.uuid4().hex[:12])[:64],
              "typ": str(n.get("typ", "frage")) if n.get("typ") in ERLAUBTE_TYPEN else "frage",
              "text": text,
              "ref": str(n.get("ref", ""))[:64],
              "titel": str(n.get("titel", ""))[:200]}
    sauber["verdacht"] = bool(_VERDACHT.search(text))
    return sauber


# --- Ablage: Google Cloud Storage ---------------------------------------------
_token_cache = {"wert": "", "bis": 0.0}


async def _gcs_token() -> str:
    """Zugangstoken des Cloud-Run-Dienstkontos (Metadata-Server, kein Key im Code)."""
    import time
    if _token_cache["wert"] and _token_cache["bis"] > time.time() + 60:
        return _token_cache["wert"]
    url = ("http://metadata.google.internal/computeMetadata/v1/"
           "instance/service-accounts/default/token")
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.get(url, headers={"Metadata-Flavor": "Google"})
        r.raise_for_status()
    d = r.json()
    _token_cache["wert"] = d["access_token"]
    _token_cache["bis"] = time.time() + float(d.get("expires_in", 3600))
    return _token_cache["wert"]


def _gcs_pfad(fach: str, name: str = "") -> str:
    teile = [BUS_PREFIX, fach] + ([name] if name else [])
    return "/".join(t for t in teile if t)


async def _gcs_schreibe(fach: str, name: str, inhalt: bytes):
    tok = await _gcs_token()
    url = f"https://storage.googleapis.com/upload/storage/v1/b/{BUS_GCS_BUCKET}/o"
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.post(url, params={"uploadType": "media", "name": _gcs_pfad(fach, name)},
                         headers={"Authorization": f"Bearer {tok}",
                                  "Content-Type": "application/json"},
                         content=inhalt)
        r.raise_for_status()


async def _gcs_liste(fach: str, limit: int) -> list[str]:
    tok = await _gcs_token()
    url = f"https://storage.googleapis.com/storage/v1/b/{BUS_GCS_BUCKET}/o"
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.get(url, params={"prefix": _gcs_pfad(fach) + "/", "maxResults": limit},
                        headers={"Authorization": f"Bearer {tok}"})
        r.raise_for_status()
    namen = [o["name"].split("/")[-1] for o in r.json().get("items", [])
             if o["name"].endswith(".json")]
    return sorted(namen)


async def _gcs_lies(fach: str, name: str) -> bytes:
    tok = await _gcs_token()
    obj = urllib.parse.quote(_gcs_pfad(fach, name), safe="")
    url = f"https://storage.googleapis.com/storage/v1/b/{BUS_GCS_BUCKET}/o/{obj}"
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.get(url, params={"alt": "media"},
                        headers={"Authorization": f"Bearer {tok}"})
        r.raise_for_status()
    return r.content


async def _gcs_loesche(fach: str, name: str):
    tok = await _gcs_token()
    obj = urllib.parse.quote(_gcs_pfad(fach, name), safe="")
    url = f"https://storage.googleapis.com/storage/v1/b/{BUS_GCS_BUCKET}/o/{obj}"
    async with httpx.AsyncClient(timeout=30) as c:
        await c.delete(url, headers={"Authorization": f"Bearer {tok}"})


# --- Ablage: normaler Ordner ---------------------------------------------------
def _ordner(fach: str) -> Path:
    p = Path(BUS_DIR) / fach
    p.mkdir(parents=True, exist_ok=True)
    return p


# --- Einheitliche Schnittstelle -----------------------------------------------
async def schreibe(nachricht: dict, fach: str = AUSGANG) -> str:
    """Nachricht als JSON-Datei ablegen. Gibt den Dateinamen zurueck."""
    name = _dateiname(nachricht.get("von", "genesis"), nachricht.get("id", uuid.uuid4().hex))
    inhalt = json.dumps(nachricht, ensure_ascii=False, indent=2).encode("utf-8")
    if BUS_GCS_BUCKET:
        await _gcs_schreibe(fach, name, inhalt)
    else:
        (_ordner(fach) / name).write_bytes(inhalt)
    return name


async def liste_eingang(limit: int = 0) -> list[str]:
    limit = limit or BUS_MAX_TICK
    if BUS_GCS_BUCKET:
        return await _gcs_liste(EINGANG, limit)
    return sorted(p.name for p in _ordner(EINGANG).glob("*.json"))[:limit]


async def lies(name: str, fach: str = EINGANG) -> dict:
    if BUS_GCS_BUCKET:
        rohdaten = await _gcs_lies(fach, name)
    else:
        rohdaten = (_ordner(fach) / name).read_bytes()
    if len(rohdaten) > BUS_MAX_BYTES * 2:
        raise RuntimeError("Datei zu gross")
    return json.loads(rohdaten.decode("utf-8"))


async def quittiere(name: str, nachricht: dict, ergebnis: str = "beantwortet"):
    """Abgearbeitete Nachricht ins Protokoll verschieben (append-only Archiv)."""
    eintrag = dict(nachricht)
    eintrag["_quittiert"] = _jetzt()
    eintrag["_ergebnis"] = ergebnis
    inhalt = json.dumps(eintrag, ensure_ascii=False, indent=2).encode("utf-8")
    if BUS_GCS_BUCKET:
        await _gcs_schreibe(PROTOKOLL, name, inhalt)
        await _gcs_loesche(EINGANG, name)
    else:
        (_ordner(PROTOKOLL) / name).write_bytes(inhalt)
        (_ordner(EINGANG) / name).unlink(missing_ok=True)


async def verlauf(thread: str, limit: int = 12) -> list[dict]:
    """Frueherer Gespraechsverlauf eines Threads aus dem Protokoll (fuer Kontext).

    Sortiert wird nach dem `ts`-Feld, nicht nach Dateiname: eine Gegenseite darf
    ihre Dateien frei benennen, der Zeitstempel in der Nachricht ist verlaesslich.
    Betrachtet werden die letzten 200 Protokolldateien.
    """
    if BUS_GCS_BUCKET:
        namen = await _gcs_liste(PROTOKOLL, 200)
    else:
        namen = sorted(p.name for p in _ordner(PROTOKOLL).glob("*.json"))
    treffer = []
    for name in reversed(namen[-200:]):
        if len(treffer) >= limit:
            break
        try:
            n = await lies(name, PROTOKOLL)
        except Exception:
            continue
        if n.get("thread") == thread:
            treffer.append(n)
    treffer.sort(key=lambda n: str(n.get("ts", "")))
    return treffer


async def status() -> dict:
    try:
        offen = await liste_eingang(100)
        return {"bereit": True, "ablage": bus_art(), "offen": len(offen),
                "naechste": offen[:5]}
    except Exception as e:
        return {"bereit": False, "ablage": bus_art(), "fehler": str(e)[:200]}
