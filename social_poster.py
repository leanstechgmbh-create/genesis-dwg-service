"""Social-Poster — LEANS Tech GmbH.
Postet fertige Videos (per oeffentlicher URL) auf Instagram (Reel) und YouTube (Short).
Instagram: Meta Graph API — Meta laedt das Video selbst von der URL.
YouTube: Data API v3, Resumable Upload — wir laden das Video und reichen es hoch.
Einrichtung + Zugangsdaten (alles Umgebungsvariablen): siehe SOCIAL_SETUP.md.
"""
import os, time
import httpx

GRAPH = "https://graph.facebook.com/v21.0"

def insta_bereit() -> bool:
    return bool(os.environ.get("META_ACCESS_TOKEN") and os.environ.get("IG_USER_ID"))

def youtube_bereit() -> bool:
    return all(os.environ.get(k) for k in ("YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN"))

def _ok(r: httpx.Response, schritt: str) -> dict:
    if r.status_code >= 400:
        raise RuntimeError(f"{schritt} fehlgeschlagen (HTTP {r.status_code}): {r.text[:300]}")
    return r.json()

def post_instagram_reel(video_url: str, caption: str) -> dict:
    """Reel anmelden -> Meta-Verarbeitung abwarten -> veroeffentlichen."""
    if not insta_bereit():
        raise RuntimeError("Instagram nicht eingerichtet (META_ACCESS_TOKEN/IG_USER_ID fehlen — siehe SOCIAL_SETUP.md)")
    token, ig = os.environ["META_ACCESS_TOKEN"], os.environ["IG_USER_ID"]
    with httpx.Client(timeout=60) as c:
        j = _ok(c.post(f"{GRAPH}/{ig}/media", data={
            "media_type": "REELS", "video_url": video_url, "caption": caption[:2200],
            "share_to_feed": "true", "access_token": token}), "Instagram: Video anmelden")
        container = j["id"]
        for _ in range(48):  # Meta verarbeitet im Hintergrund, meist < 1 Minute
            time.sleep(5)
            s = _ok(c.get(f"{GRAPH}/{container}", params={
                "fields": "status_code,status", "access_token": token}), "Instagram: Status")
            if s.get("status_code") == "FINISHED":
                break
            if s.get("status_code") == "ERROR":
                raise RuntimeError(f"Instagram: Verarbeitung fehlgeschlagen: {str(s.get('status', ''))[:200]}")
        else:
            raise RuntimeError("Instagram: Verarbeitung nicht fertig geworden (Timeout)")
        j = _ok(c.post(f"{GRAPH}/{ig}/media_publish", data={
            "creation_id": container, "access_token": token}), "Instagram: Veroeffentlichen")
        media_id = j["id"]
        p = c.get(f"{GRAPH}/{media_id}", params={"fields": "permalink", "access_token": token})
        link = p.json().get("permalink", "") if p.status_code < 400 else ""
        return {"platform": "instagram", "id": media_id, "url": link}

def _yt_token() -> str:
    j = _ok(httpx.post("https://oauth2.googleapis.com/token", data={
        "client_id": os.environ["YT_CLIENT_ID"], "client_secret": os.environ["YT_CLIENT_SECRET"],
        "refresh_token": os.environ["YT_REFRESH_TOKEN"], "grant_type": "refresh_token"},
        timeout=30), "YouTube: Anmeldung")
    return j["access_token"]

def post_youtube(video_url: str, titel: str, beschreibung: str, privacy: str = "public") -> dict:
    """Video von der URL laden und hochladen (9:16 unter 3 Min wird automatisch ein Short)."""
    if not youtube_bereit():
        raise RuntimeError("YouTube nicht eingerichtet (YT_CLIENT_ID/SECRET/REFRESH_TOKEN fehlen — siehe SOCIAL_SETUP.md)")
    token = _yt_token()
    with httpx.Client(timeout=600, follow_redirects=True) as c:
        video = c.get(video_url).content  # die Clips sind klein (wenige MB)
        init = c.post("https://www.googleapis.com/upload/youtube/v3/videos",
            params={"uploadType": "resumable", "part": "snippet,status"},
            headers={"Authorization": f"Bearer {token}",
                     "X-Upload-Content-Type": "video/mp4",
                     "X-Upload-Content-Length": str(len(video))},
            json={"snippet": {"title": titel[:100], "description": beschreibung[:4500],
                              "categoryId": "22"},
                  "status": {"privacyStatus": privacy, "selfDeclaredMadeForKids": False}})
        if init.status_code >= 400 or "location" not in init.headers:
            raise RuntimeError(f"YouTube: Upload-Start fehlgeschlagen (HTTP {init.status_code}): {init.text[:300]}")
        j = _ok(c.put(init.headers["location"], content=video,
                      headers={"Content-Type": "video/mp4"}), "YouTube: Upload")
        return {"platform": "youtube", "id": j["id"], "url": f"https://youtu.be/{j['id']}"}
