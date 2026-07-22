# Automatik-Deploy einrichten (einmalig, nur Klicken — kein Terminal)

Danach deployt sich der Service bei jeder Code-Änderung selbst.
Funktioniert am Handy oder PC im normalen Browser (kein Cloud Shell nötig).

## Schritt 1: Schlüssel in der Google-Konsole erzeugen (~5 Min)

1. Öffne https://console.cloud.google.com/iam-admin/serviceaccounts
   (mit leanstechgmbh@gmail.com; falls oben eine Projektauswahl kommt: das Projekt anklicken)
2. Oben **„+ Dienstkonto erstellen"**
3. Name: `github-deploy` → **„Erstellen und fortfahren"**
4. Bei „Rolle auswählen" nacheinander diese ZWEI Rollen hinzufügen:
   - **Bearbeiter** (unter „Einfach/Basic")
   - **Dienstkontonutzer** (Suchfeld: „Dienstkontonutzer" / „Service Account User")
   → **„Weiter"** → **„Fertig"**
5. In der Liste beim neuen Konto rechts auf **⋮ → „Schlüssel verwalten"**
6. **„Schlüssel hinzufügen" → „Neuen Schlüssel erstellen" → JSON → „Erstellen"**
   → eine Datei wird heruntergeladen (z. B. `projektname-abc123.json`)
7. Notiere außerdem die **Projekt-ID** (steht in der Projektauswahl oben,
   z. B. `leanstech-genesis-123456` — die ID, nicht der Anzeigename)

## Schritt 2: Beide Werte bei GitHub einfügen (~3 Min)

1. Öffne https://github.com/leanstechgmbh-create/genesis-dwg-service/settings/secrets/actions
2. **„New repository secret"**:
   - Name: `GCP_SA_KEY`
   - Secret: den **kompletten Inhalt** der heruntergeladenen JSON-Datei einfügen
     (Datei mit Editor/Notizen öffnen → alles markieren → kopieren → einfügen)
   - **„Add secret"**
3. Nochmal **„New repository secret"**:
   - Name: `GCP_PROJECT`
   - Secret: die Projekt-ID aus Schritt 1.7
   - **„Add secret"**

## Schritt 3: Bescheid sagen

Sag Claude „Secrets sind drin" — Claude startet den Deploy, prüft das Ergebnis
und meldet die fertige Service-Adresse. Ab dann deployt jede Änderung automatisch.

**Danach noch (für das Posten):** Die 5 Schlüssel aus `SOCIAL_SETUP.md` einmal
als Cloud-Run-Umgebungsvariablen eintragen — sie bleiben bei allen künftigen
Deploys automatisch erhalten.

**Wichtig:** Die JSON-Datei ist ein Generalschlüssel fürs Google-Projekt.
Nur bei GitHub-Secrets einfügen, niemals in den Chat, niemals ins Repository.
