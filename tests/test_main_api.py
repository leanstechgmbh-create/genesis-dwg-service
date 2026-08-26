"""Tests fuer die HTTP-Schnittstelle in main.py.

Schwerpunkt: /modify-dwg (der Weg, den n8n und der Slack-Bot nehmen) und der
Schluesselschutz. Externe Dienste (OpenAI, Slack, Stripe, Mail) werden nicht
angesprochen — die Tests bleiben vor der Stelle stehen, an der sie gebraucht
wuerden, oder ersetzen sie durch einen Platzhalter.
"""
import base64

import pytest
from fastapi.testclient import TestClient

import main

SCHLUESSEL = "Testschluessel-123"


@pytest.fixture
def client():
    return TestClient(main.app)


@pytest.fixture
def mit_schluessel(monkeypatch):
    """Setzt einen bekannten GENESIS_API_KEY fuer die Dauer eines Tests."""
    monkeypatch.setattr(main, "API_KEY", SCHLUESSEL)
    return SCHLUESSEL


@pytest.fixture
def ohne_schluessel(monkeypatch):
    """Kein GENESIS_API_KEY gesetzt — wie in einer frischen Umgebung."""
    monkeypatch.setattr(main, "API_KEY", "")


@pytest.fixture
def dxf_base64(zeichnung):
    """Die Test-DXF aus conftest, base64-kodiert wie im HTTP-Body."""
    return base64.b64encode(open(zeichnung, "rb").read()).decode()


# --------------------------------------------------------------------------
# Health
# --------------------------------------------------------------------------

def test_health_meldet_dienst_und_modulzustand(client):
    antwort = client.get("/")

    assert antwort.status_code == 200
    daten = antwort.json()
    assert daten["service"] == "GENESIS"
    assert daten["status"] == "ok"
    for feld in ("dwg_read", "dwg_write", "slack", "mail_ready", "chatgpt"):
        assert feld in daten


def test_health_liefert_unter_der_website_domain_den_katalog(client, monkeypatch):
    monkeypatch.setattr(main, "katalog", lambda: {"katalog": "da"})

    antwort = client.get("/", headers={"host": "profihaustechnik.de"})

    assert antwort.json() == {"katalog": "da"}


# --------------------------------------------------------------------------
# /modify-dwg -- Schluesselschutz
# --------------------------------------------------------------------------

def test_modify_weist_falschen_schluessel_ab(client, mit_schluessel, dxf_base64):
    antwort = client.post("/modify-dwg",
                          headers={"x-genesis-key": "falsch"},
                          json={"dxf_base64": dxf_base64, "elements": []})

    assert antwort.status_code == 401


def test_modify_weist_fehlenden_schluessel_ab(client, mit_schluessel, dxf_base64):
    antwort = client.post("/modify-dwg",
                          json={"dxf_base64": dxf_base64, "elements": []})

    assert antwort.status_code == 401


def test_modify_ist_ohne_gesetzten_schluessel_offen(client, ohne_schluessel, dxf_base64):
    """Dokumentiert das aktuelle Verhalten: ist GENESIS_API_KEY leer, laesst
    /modify-dwg jeden durch (`if API_KEY and ...`). In Cloud Run ist der
    Schluessel gesetzt, dort greift der Schutz. Siehe die Bus-Endpunkte
    weiter unten — die sind stattdessen hart verriegelt."""
    antwort = client.post("/modify-dwg",
                          json={"dxf_base64": dxf_base64, "elements": []})

    assert antwort.status_code == 200


# --------------------------------------------------------------------------
# /modify-dwg -- Erfolgsfall und Fehlerfaelle
# --------------------------------------------------------------------------

def test_modify_liefert_bearbeitete_dxf_mit_protokoll(client, mit_schluessel, dxf_base64):
    antwort = client.post("/modify-dwg",
                          headers={"x-genesis-key": SCHLUESSEL},
                          json={"filename": "plan.dxf",
                                "dxf_base64": dxf_base64,
                                "elements": [{"aktion": "loeschen",
                                              "layer": "SANITAER"}]})

    assert antwort.status_code == 200
    assert antwort.headers["x-genesis-format"] == "dxf"
    assert "plan.dxf" in antwort.headers["content-disposition"]
    assert "geloescht: 1" in antwort.headers["x-genesis-log"]
    assert antwort.content.startswith(b"  0")


def test_modify_leitet_den_dateinamen_aus_dem_feld_filename_ab(client, mit_schluessel,
                                                               dxf_base64):
    antwort = client.post("/modify-dwg",
                          headers={"x-genesis-key": SCHLUESSEL},
                          json={"filename": "Mehringdamm_LG.dxf",
                                "dxf_base64": dxf_base64, "elements": []})

    assert "Mehringdamm_LG.dxf" in antwort.headers["content-disposition"]


def test_modify_meldet_fehlende_zeichnung(client, mit_schluessel):
    antwort = client.post("/modify-dwg",
                          headers={"x-genesis-key": SCHLUESSEL},
                          json={"elements": []})

    assert antwort.status_code == 400
    assert "fehlt" in antwort.json()["detail"]


def test_modify_meldet_fehlenden_dwg_leser(client, mit_schluessel, dxf_base64,
                                           monkeypatch):
    monkeypatch.setattr(main, "have", lambda cmd: False)

    antwort = client.post("/modify-dwg",
                          headers={"x-genesis-key": SCHLUESSEL},
                          json={"dwg_base64": dxf_base64, "elements": []})

    assert antwort.status_code == 500
    assert "DWG-Leser" in antwort.json()["detail"]


def test_modify_faengt_kaputte_daten_ab_statt_abzustuerzen(client, mit_schluessel):
    antwort = client.post("/modify-dwg",
                          headers={"x-genesis-key": SCHLUESSEL},
                          json={"dxf_base64": "das-ist-kein-base64-dxf",
                                "elements": []})

    assert antwort.status_code == 500
    assert "error" in antwort.json()          # JSON-Fehler, kein Absturz


def test_modify_protokolliert_unbekannte_aktion_ohne_fehler(client, mit_schluessel,
                                                            dxf_base64):
    antwort = client.post("/modify-dwg",
                          headers={"x-genesis-key": SCHLUESSEL},
                          json={"dxf_base64": dxf_base64,
                                "elements": [{"aktion": "tanzen", "nr": 1}]})

    assert antwort.status_code == 200
    assert "unbekannt" in antwort.headers["x-genesis-log"]


# --------------------------------------------------------------------------
# Bus- und KI-Endpunkte -- harter Schluesselschutz
# --------------------------------------------------------------------------

GESCHUETZT_GET = ["/bus/status"]
GESCHUETZT_POST = ["/bus/tick", "/bus/senden", "/ai/ask", "/gpt/ask", "/gpt/dialog"]


@pytest.mark.parametrize("pfad", GESCHUETZT_GET)
def test_bus_get_ohne_schluessel_401(client, mit_schluessel, pfad):
    assert client.get(pfad).status_code == 401


@pytest.mark.parametrize("pfad", GESCHUETZT_POST)
def test_bus_post_ohne_schluessel_401(client, mit_schluessel, pfad):
    assert client.post(pfad, json={}).status_code == 401


@pytest.mark.parametrize("pfad", GESCHUETZT_GET)
def test_bus_bleibt_geschlossen_wenn_kein_schluessel_gesetzt_ist(client,
                                                                 ohne_schluessel, pfad):
    """Anders als /modify-dwg: ohne GENESIS_API_KEY verriegelt der Bus ganz."""
    antwort = client.get(pfad)

    assert antwort.status_code == 503
    assert "nicht gesetzt" in antwort.json()["detail"]


def test_bus_akzeptiert_schluessel_auch_als_query_parameter(client, mit_schluessel,
                                                            monkeypatch):
    """Pub/Sub und Cloud Scheduler koennen keine Header setzen."""
    async def status_platzhalter():
        return {"ablage": "test", "offen": 0}
    monkeypatch.setattr(main.ai_bus, "status", status_platzhalter)

    antwort = client.get(f"/bus/status?key={SCHLUESSEL}")

    assert antwort.status_code == 200
    assert antwort.json()["offen"] == 0


def test_bus_akzeptiert_schluessel_im_header(client, mit_schluessel, monkeypatch):
    async def status_platzhalter():
        return {"ablage": "test", "offen": 3}
    monkeypatch.setattr(main.ai_bus, "status", status_platzhalter)

    antwort = client.get("/bus/status", headers={"x-genesis-key": SCHLUESSEL})

    assert antwort.status_code == 200
    assert antwort.json()["offen"] == 3
