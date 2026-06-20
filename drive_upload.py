#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Drive-Upload fuer LEANS-Angebote.

upsert_file() laedt eine lokale Datei (z.B. das branded Angebot-PDF) in einen
Drive-Ordner. Existiert dort bereits eine Datei mit gleichem Titel, wird ihr
Inhalt UEBERSCHRIEBEN (gleiche Datei-ID bleibt erhalten) — so bleibt bei
Iterationen am selben Angebot nur eine Datei.

Anmeldung ueber einen Google-Service-Account:
  - ENV `GOOGLE_SERVICE_ACCOUNT_JSON` = kompletter JSON-Key als String, ODER
  - ENV `GOOGLE_APPLICATION_CREDENTIALS` = Pfad zur JSON-Key-Datei.
Der Service-Account braucht Schreibrecht auf den Zielordner (Ordner in Drive
fuer die Service-Account-E-Mail freigeben).

Default-Ordner: „Cloud Angebote" (neue Angebote).
"""
import json
import os

SCOPES = ["https://www.googleapis.com/auth/drive"]

# Drive-Ordner (siehe CLAUDE.md)
CLOUD_ANGEBOTE = "1lS-n7kan-pwbgFDP_NYwyRtGI-JIMd6C"  # neue Angebote
BESTAND_ANGEBOTE = "1KDlM4-GnjG_9IcERuwYmuyKoEw2HHLov"  # alte Angebote


def _credentials():
    """Service-Account-Credentials aus ENV laden (oder None, wenn nicht gesetzt)."""
    from google.oauth2 import service_account

    raw = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    if raw:
        info = json.loads(raw)
        return service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
    path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if path and os.path.exists(path):
        return service_account.Credentials.from_service_account_file(path, scopes=SCOPES)
    return None


def _service():
    from googleapiclient.discovery import build

    creds = _credentials()
    if creds is None:
        raise RuntimeError(
            "Kein Service-Account gefunden. Setze GOOGLE_SERVICE_ACCOUNT_JSON "
            "(JSON-String) oder GOOGLE_APPLICATION_CREDENTIALS (Dateipfad)."
        )
    # cache_discovery=False vermeidet Warnungen ohne Cache-Verzeichnis
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def _find_existing(svc, title, folder_id):
    """Datei-ID einer gleichnamigen Datei im Ordner zurueckgeben (oder None)."""
    safe = title.replace("'", "\\'")
    q = f"name = '{safe}' and '{folder_id}' in parents and trashed = false"
    resp = svc.files().list(
        q=q, fields="files(id, name)", pageSize=1,
        supportsAllDrives=True, includeItemsFromAllDrives=True,
    ).execute()
    files = resp.get("files", [])
    return files[0]["id"] if files else None


def upsert_file(local_path, title=None, folder_id=CLOUD_ANGEBOTE,
                mime_type="application/pdf"):
    """Datei hochladen; bei gleichem Titel im Ordner Inhalt ueberschreiben.

    Gibt dict mit id, name, webViewLink und action ('updated'|'created') zurueck.
    """
    from googleapiclient.http import MediaFileUpload

    if not os.path.exists(local_path):
        raise FileNotFoundError(local_path)
    title = title or os.path.basename(local_path)

    svc = _service()
    media = MediaFileUpload(local_path, mimetype=mime_type, resumable=False)
    existing = _find_existing(svc, title, folder_id)

    if existing:
        f = svc.files().update(
            fileId=existing, media_body=media,
            fields="id, name, webViewLink", supportsAllDrives=True,
        ).execute()
        f["action"] = "updated"
        return f

    f = svc.files().create(
        body={"name": title, "parents": [folder_id]}, media_body=media,
        fields="id, name, webViewLink", supportsAllDrives=True,
    ).execute()
    f["action"] = "created"
    return f


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: drive_upload.py <pfad-zur-datei> [titel] [folder_id]")
        raise SystemExit(2)
    path = sys.argv[1]
    ttl = sys.argv[2] if len(sys.argv) > 2 else None
    fld = sys.argv[3] if len(sys.argv) > 3 else CLOUD_ANGEBOTE
    res = upsert_file(path, ttl, fld)
    print(f"{res['action'].upper()} -> {res['name']} ({res['id']})")
    print(res.get("webViewLink", ""))
