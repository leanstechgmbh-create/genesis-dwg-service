# Domain-Aufschaltung: profihaustechnik.de

Die Domain liegt bei **INWX**, das DNS soll wie bei den anderen beiden Webseiten
über **Cloudflare** laufen. Der Service läuft auf **Google Cloud Run**
(siehe `START_HIER.md`). Die Webseite wird unter `/` (über die Domain) bzw.
`/katalog` ausgeliefert.

## 1. Cloudflare: Site anlegen

1. Cloudflare-Dashboard → **Add a site** → `profihaustechnik.de` → Free-Plan.
2. Cloudflare zeigt **zwei Nameserver** an (z. B. `xxx.ns.cloudflare.com` und
   `yyy.ns.cloudflare.com`) — notieren.

## 2. INWX: Nameserver umstellen

1. INWX-Login → **Domains** → `profihaustechnik.de` → **Nameserver**.
2. Die INWX-Standard-Nameserver durch die beiden Cloudflare-Nameserver aus
   Schritt 1 ersetzen (genau wie bei den anderen beiden Domains).
3. Speichern. Umstellung dauert meist wenige Minuten bis einige Stunden.

## 3. Google Cloud Run: Domain-Mapping

```bash
gcloud beta run domain-mappings create \
  --service genesis-dwg-service \
  --domain profihaustechnik.de \
  --region europe-west1
```

- Google verlangt ggf. eine **Domain-Verifizierung**: den angezeigten
  `google-site-verification`-TXT-Record in Cloudflare unter **DNS → Records**
  anlegen.
- Nach dem Mapping zeigt Google die nötigen DNS-Einträge an (in der Regel
  CNAME auf `ghs.googlehosted.com`).

## 4. Cloudflare: DNS-Records anlegen

| Typ   | Name | Ziel                   | Proxy      |
|-------|------|------------------------|------------|
| CNAME | `@`  | `ghs.googlehosted.com` | Proxied ✅ |
| CNAME | `www`| `ghs.googlehosted.com` | Proxied ✅ |

(Cloudflare löst den CNAME auf der Zone-Spitze per CNAME-Flattening auf.)

## 5. Cloudflare: SSL & Regeln

1. **SSL/TLS → Overview**: Modus **Full (strict)**.
2. **SSL/TLS → Edge Certificates**: **Always Use HTTPS** aktivieren.
3. Optional (Redirect Rule): `www.profihaustechnik.de/*` →
   `https://profihaustechnik.de/$1` (301).

## 6. Prüfen

```bash
curl -I https://profihaustechnik.de          # → 200, HTML-Katalog
curl -s https://profihaustechnik.de/katalog | head -5
```

Der Health-Check (`{"service": "GENESIS", ...}`) bleibt über die
`*.run.app`-URL des Services erreichbar; über die Domain liefert `/`
direkt die Webseite (Host-Weiche in `main.py`).

## Hinweis Automatisierung

Mit einem **Cloudflare-API-Token** (Zone.DNS Edit) und den **INWX-API-Zugangsdaten**
lassen sich Schritt 2 und 4 automatisieren — Zugangsdaten dafür bitte als
Umgebungsvariablen bereitstellen (`CLOUDFLARE_API_TOKEN`, `INWX_USER`, `INWX_PASS`),
niemals ins Repository committen.
