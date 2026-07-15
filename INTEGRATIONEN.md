# Integrationen: Einkauf, Dropshipping & Amazon

Stand der Vorbereitung für Profihaustechnik.de. Der Katalog (über 10.000 Artikel
mit eigenen Artikelnummern `PHT-…`) wird von `tools/artikel_generator.py` erzeugt
und liegt als `website/artikel.json` (Webseite) und
`website/amazon-export.csv` (Amazon-Basis) vor.

## 1. Einkauf beim Großhandel + Dropshipping (nichts selbst verpacken)

So läuft es in der SHK-Branche — genau wie bei GC-Gruppe & Co.:

| Weg | Was es ist | Was gebraucht wird |
|-----|-----------|--------------------|
| **IDS-Connect** | Branchenstandard: Warenkorb aus unserer Software direkt zum Großhändler-Shop übergeben, Preise/Verfügbarkeit live | Fachkunden-Login beim Großhändler (z. B. GC Online Plus, Elmer, Pietsch) |
| **DATANORM** | Artikelstammdaten + **Einkaufspreise** als Datei vom Großhändler; damit können wir je Artikel den günstigsten Lieferanten bestimmen | DATANORM-Freischaltung im Fachkunden-Konto (kostenlos) |
| **UGL/OpenTrans** | Elektronische Bestellung/Lieferschein/Rechnung | dito |
| **Direktlieferung Baustelle/Kunde** | Großhändler liefert an eine Wunschadresse = faktisch Dropshipping, wir verpacken nichts | im Bestellprozess Lieferadresse des Kunden angeben |

**Preisvergleich „wo am günstigsten":** Sobald DATANORM-Dateien von 2–3
Großhändlern vorliegen, matchen wir sie per Skript gegen unsere `PHT-`-Artikel
und hinterlegen je Artikel den günstigsten Lieferanten. Der Generator ist dafür
vorbereitet (stabile Artikelnummern als Match-Schlüssel).

**Was ich dafür von euch brauche (einmalig):**
1. Fachkunden-Zugänge der Großhändler, bei denen ihr Konto habt
   (GC-Gruppe/„GC Online Plus", Elmer, Zander, Pietsch — mindestens einer)
2. Dort DATANORM-Export freischalten lassen (ein Anruf beim Innendienst genügt)
3. Die DATANORM-Datei hier ablegen oder mir den Download-Zugang geben

## 2. Amazon-Anbindung

**Schon fertig:** `website/amazon-export.csv` — eine Zeile je SKU
(Artikelnummer, Bezeichnung inkl. Ausführung, Kategorie, Gewerk, Einheit),
abrufbar unter `/amazon-export.csv`. Das ist die Basis für das
Amazon-Flatfile bzw. den API-Upload.

**Was für die echte Anbindung nötig ist:**
1. **Amazon-Seller-Central-Konto** (Verkäuferkonto, professioneller Tarif)
2. **SP-API-Zugang** (in Seller Central unter „Apps & Services" freischalten) —
   damit kann ich Listings, Bestände und Preise automatisch synchronisieren
3. **EAN/GTIN je Artikel**: Amazon verlangt für neue Listings EANs.
   Optionen: (a) EANs aus den DATANORM-Daten der Großhändler übernehmen
   (die meisten Artikel haben Hersteller-EANs — der saubere Weg), oder
   (b) GTIN-Befreiung für Eigenmarke „Profihaustechnik" beantragen
4. **Versand durch Amazon (FBA)** oder **Versand durch Großhändler**
   (Dropshipping): Amazon erlaubt Dropshipping nur, wenn wir als Verkäufer
   auftreten (Lieferschein/Rechnung auf uns) — mit der
   Großhändler-Direktlieferung aus Punkt 1 ist genau das machbar.

**Sobald ihr mir Seller-Central-/SP-API-Zugangsdaten gebt** (als
Umgebungsvariablen, nie ins Repo), baue ich den Sync: neue Artikel anlegen,
Bestände/Preise aktualisieren, Bestellungen abrufen → Bestellung automatisch
beim Großhändler auslösen (Lieferadresse = Endkunde).

## 3. Rechtliches (vor Verkaufsstart klären)

Für den echten Verkauf (eigener Shop oder Amazon) sind nötig: Impressum, AGB,
Widerrufsbelehrung, Datenschutzerklärung, Verpackungsgesetz-Registrierung
(LUCID), ggf. ElektroG/WEEE für Geräte. Das kann ich vorbereiten, sollte aber
einmal anwaltlich geprüft werden.

## Reihenfolge (empfohlen)

1. ✅ Katalog mit 10.000+ Artikeln (fertig)
2. ✅ Amazon-Export-CSV (fertig)
3. ⬜ DATANORM von 1–3 Großhändlern → Preise + EANs importieren
4. ⬜ Domain live schalten (siehe `DOMAIN_SETUP.md`)
5. ⬜ Amazon Seller Central + SP-API → Listings hochladen
6. ⬜ Bestell-Automatik: Amazon-Bestellung → Großhändler-Direktlieferung
