# GENESIS Flow — Vollautomatik einrichten (ohne Installation)

**Ziel:** DWG + markierten Plan ins Formular → fertige DWG kommt automatisch.
Du installierst NICHTS. Alles im Browser. Einmal ~10 Min, dann läuft es für immer.

## Schritt 1 — Google Cloud Shell öffnen (Browser)
→ https://shell.cloud.google.com
(mit leanstechgmbh@gmail.com einloggen — Cloud Shell hat alles vorinstalliert)

## Schritt 2 — Diese Dateien hochladen
Im Cloud Shell oben rechts: **⋮ → Upload** → den Ordner `genesis-ezdxf-service` hochladen
(oder die ZIP, dann: `unzip genesis-ezdxf-service.zip -d genesis-ezdxf-service`)

## Schritt 3 — Diese 4 Zeilen reinkopieren
```bash
cd genesis-ezdxf-service
PROJECT=$(gcloud config get-value project)
gcloud services enable run.googleapis.com cloudbuild.googleapis.com
gcloud run deploy genesis-ezdxf --source . --region europe-west3 \
  --allow-unauthenticated --memory 1Gi --timeout 300
```
Cloud Build baut alles selbst (inkl. DWG-Konverter). Am Ende erscheint die **feste URL**.

## Schritt 4 — n8n verbinden
n8n → Settings → Variables:
```
EZDXF_SERVICE_URL = <die-URL-von-oben>/modify-dwg
```

## Fertig — ab jetzt vollautomatisch
**Formular:** https://semirredzic.app.n8n.cloud/form/genesis-flow
DWG + markierten Plan hochladen → fertige DWG landet im Drive. Kein Zeichnen. Nie wieder.

---
*Hinweis: Konverter ist Open-Source (libredwg). Bei komplexen Plänen Ergebnis kurz
sichten. Für 100% CAD-Fidelity kann später auf ODA-Converter umgestellt werden.*
