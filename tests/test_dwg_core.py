"""Tests fuer die Kernlogik in dwg_core.py.

Abgedeckt: Koordinaten-Parser, Naehe-Erkennung, die vier Aktionen von
apply_changes (loeschen / verschieben / hinzufuegen / text) sowie der
DXF-Weg durch modify_drawing. Alles ohne LibreDWG.
"""
import ezdxf
import pytest

from conftest import lade
from dwg_core import _near, _pt, apply_changes, modify_drawing


# --------------------------------------------------------------------------
# _pt -- Koordinaten aus Nutzereingaben lesen
# --------------------------------------------------------------------------

@pytest.mark.parametrize("eingabe,erwartet", [
    ("10,20", (10.0, 20.0)),
    ("10;20", (10.0, 20.0)),
    ("10.5,20.5", (10.5, 20.5)),
    ("-10,-20", (-10.0, -20.0)),
    ("10,20,30", (10.0, 20.0)),
    (" 10 , 20 ", (10.0, 20.0)),
], ids=["komma", "semikolon", "dezimal", "negativ", "dritter-wert-ignoriert",
        "leerzeichen"])
def test_pt_liest_gueltige_koordinaten(eingabe, erwartet):
    assert _pt(eingabe) == erwartet


@pytest.mark.parametrize("eingabe", ["", "abc", None, "10", ",", "10,abc"],
                         ids=["leer", "text", "none", "nur-ein-wert", "nur-komma",
                              "zweiter-wert-text"])
def test_pt_faellt_bei_unbrauchbarer_eingabe_auf_standard_zurueck(eingabe):
    assert _pt(eingabe) == (0.0, 0.0)


def test_pt_nutzt_eigenen_standardwert():
    assert _pt("kaputt", d=(5.0, 7.0)) == (5.0, 7.0)


# --------------------------------------------------------------------------
# _near -- liegt ein Element im Radius?
# --------------------------------------------------------------------------

def test_near_erkennt_kreis_im_radius(zeichnung):
    _, msp = lade(zeichnung)
    kreis = msp.query("CIRCLE")[0]
    assert _near(kreis, 100, 100, 10) is True


def test_near_schliesst_entferntes_element_aus(zeichnung):
    _, msp = lade(zeichnung)
    kreis = msp.query("CIRCLE")[0]
    assert _near(kreis, 5000, 5000, 10) is False


def test_near_ist_bei_unbekanntem_typ_false(zeichnung):
    doc, msp = lade(zeichnung)
    punkt = msp.add_point((100, 100))
    assert _near(punkt, 100, 100, 50) is False


# --------------------------------------------------------------------------
# apply_changes -- LOESCHEN
# --------------------------------------------------------------------------

def test_loeschen_per_layer_entfernt_nur_diesen_layer(zeichnung):
    log = apply_changes(zeichnung, [{"aktion": "loeschen", "layer": "SANITAER"}])

    _, msp = lade(zeichnung)
    layer_danach = {e.dxf.layer for e in msp}
    assert "SANITAER" not in layer_danach
    assert "LUEFTUNG" in layer_danach
    assert "geloescht: 1" in log[0]


def test_loeschen_per_position_trifft_nur_den_radius(zeichnung):
    log = apply_changes(zeichnung, [
        {"aktion": "loeschen", "position": "100,100", "radius": 50},
    ])

    _, msp = lade(zeichnung)
    assert len(msp.query("CIRCLE")) == 1          # nur der bei (900,900) bleibt
    assert msp.query("CIRCLE")[0].dxf.center[0] == 900
    assert "geloescht: 2" in log[0]               # Kreis + Text bei (100,100)


def test_loeschen_akzeptiert_deutsche_und_englische_schreibweisen(zeichnung):
    for wort in ("löschen", "delete", "entfernen", "rausstreichen"):
        log = apply_changes(zeichnung, [{"aktion": wort, "layer": "SANITAER"}])
        assert "unbekannt" not in log[0]


# --------------------------------------------------------------------------
# apply_changes -- VERSCHIEBEN
# --------------------------------------------------------------------------

def test_verschieben_per_layer_versetzt_um_die_differenz(zeichnung):
    log = apply_changes(zeichnung, [{
        "aktion": "verschieben",
        "layer": "SANITAER",
        "von": "900,900",
        "position": "1000,950",
    }])

    _, msp = lade(zeichnung)
    kreis = [c for c in msp.query("CIRCLE") if c.dxf.layer == "SANITAER"][0]
    assert kreis.dxf.center[0] == pytest.approx(1000)
    assert kreis.dxf.center[1] == pytest.approx(950)
    assert "verschoben: 1" in log[0]


def test_verschieben_mit_offset_hat_vorrang_vor_von_nach(zeichnung):
    apply_changes(zeichnung, [{
        "aktion": "verschieben",
        "layer": "SANITAER",
        "von": "900,900",
        "position": "1000,950",
        "offset": "10,20",
    }])

    _, msp = lade(zeichnung)
    kreis = [c for c in msp.query("CIRCLE") if c.dxf.layer == "SANITAER"][0]
    assert kreis.dxf.center[0] == pytest.approx(910)
    assert kreis.dxf.center[1] == pytest.approx(920)


def test_verschieben_per_position_greift_im_radius(zeichnung):
    log = apply_changes(zeichnung, [{
        "aktion": "verschieben",
        "von": "100,100",
        "position": "200,100",
        "radius": 50,
    }])

    _, msp = lade(zeichnung)
    kreis = [c for c in msp.query("CIRCLE") if c.dxf.layer == "LUEFTUNG"][0]
    assert kreis.dxf.center[0] == pytest.approx(200)
    assert "verschoben: 2" in log[0]               # Kreis + Text


# --------------------------------------------------------------------------
# apply_changes -- HINZUFUEGEN
# --------------------------------------------------------------------------

def test_hinzufuegen_legt_kreis_text_und_layer_an(leere_zeichnung):
    log = apply_changes(leere_zeichnung, [{
        "aktion": "hinzufuegen",
        "element": "Auslass",
        "position": "500,500",
        "masse": "200x200",
    }])

    doc, msp = lade(leere_zeichnung)
    assert "GENESIS_NEU" in doc.layers

    kreis = msp.query("CIRCLE")[0]
    assert kreis.dxf.center[0] == pytest.approx(500)
    assert kreis.dxf.layer == "GENESIS_NEU"

    text = msp.query("TEXT")[0]
    assert "Auslass" in text.dxf.text
    assert "200x200" in text.dxf.text
    assert "ergaenzt" in log[0]


def test_hinzufuegen_waehlt_zuluft_layer_anhand_des_typs(leere_zeichnung):
    apply_changes(leere_zeichnung, [{
        "aktion": "hinzufuegen",
        "typ": "Zuluft",
        "position": "0,0",
    }])

    doc, _ = lade(leere_zeichnung)
    assert "Zuluft_NEU" in doc.layers


def test_hinzufuegen_respektiert_vorgegebenen_layer(leere_zeichnung):
    apply_changes(leere_zeichnung, [{
        "aktion": "hinzufuegen",
        "layer": "MEIN_LAYER",
        "position": "0,0",
    }])

    doc, _ = lade(leere_zeichnung)
    assert "MEIN_LAYER" in doc.layers


# --------------------------------------------------------------------------
# apply_changes -- TEXT
# --------------------------------------------------------------------------

def test_text_ersetzt_treffer(zeichnung):
    log = apply_changes(zeichnung, [{
        "aktion": "text",
        "element": "AL-01",
        "wert": "AL-99",
    }])

    _, msp = lade(zeichnung)
    assert msp.query("TEXT")[0].dxf.text == "AL-99"
    assert "AL-99" in log[0]


def test_text_meldet_wenn_nichts_passt(zeichnung):
    log = apply_changes(zeichnung, [{
        "aktion": "text",
        "element": "GIBTESNICHT",
        "wert": "egal",
    }])

    assert "n/a" in log[0]
    _, msp = lade(zeichnung)
    assert msp.query("TEXT")[0].dxf.text == "AL-01"


def test_text_ignoriert_leerzeichen_im_suchbegriff(zeichnung):
    apply_changes(zeichnung, [{
        "aktion": "text",
        "element": "AL - 01",
        "wert": "AL-99",
    }])

    _, msp = lade(zeichnung)
    assert msp.query("TEXT")[0].dxf.text == "AL-99"


def test_text_ignoriert_leerzeichen_in_der_zeichnung(leere_zeichnung):
    doc = ezdxf.readfile(leere_zeichnung)
    doc.modelspace().add_text("AL 01", dxfattribs={"height": 25})
    doc.saveas(leere_zeichnung)

    apply_changes(leere_zeichnung, [{
        "aktion": "text",
        "element": "AL01",
        "wert": "AL-99",
    }])

    _, msp = lade(leere_zeichnung)
    assert msp.query("TEXT")[0].dxf.text == "AL-99"


# --------------------------------------------------------------------------
# apply_changes -- Robustheit
# --------------------------------------------------------------------------

def test_unbekannte_aktion_wird_protokolliert_ohne_abbruch(zeichnung):
    log = apply_changes(zeichnung, [{"aktion": "tanzen", "nr": 1}])

    assert "unbekannt" in log[0]
    _, msp = lade(zeichnung)
    assert len(list(msp)) == 4                     # nichts veraendert


def test_fehlerhaftes_element_stoppt_die_uebrigen_nicht(zeichnung):
    log = apply_changes(zeichnung, [
        {"aktion": "verschieben", "nr": 1, "layer": "SANITAER",
         "radius": "keine-zahl"},                  # loest ValueError aus
        {"aktion": "loeschen", "nr": 2, "layer": "SANITAER"},
    ])

    assert len(log) == 2
    assert "FEHLER" in log[0]
    assert "geloescht: 1" in log[1]                # zweites Element lief trotzdem


def test_leere_elementliste_aendert_nichts(zeichnung):
    log = apply_changes(zeichnung, [])

    assert log == []
    _, msp = lade(zeichnung)
    assert len(list(msp)) == 4


def test_mehrere_aktionen_laufen_nacheinander(zeichnung):
    log = apply_changes(zeichnung, [
        {"aktion": "loeschen", "nr": 1, "layer": "SANITAER"},
        {"aktion": "text", "nr": 2, "element": "AL-01", "wert": "AL-42"},
    ])

    assert len(log) == 2
    _, msp = lade(zeichnung)
    assert not [e for e in msp if e.dxf.layer == "SANITAER"]
    assert msp.query("TEXT")[0].dxf.text == "AL-42"


# --------------------------------------------------------------------------
# modify_drawing -- der Weg, den die HTTP-API nimmt
# --------------------------------------------------------------------------

def test_modify_drawing_liefert_dxf_zurueck(zeichnung):
    roh = open(zeichnung, "rb").read()

    daten, name, media, format_, log = modify_drawing(
        roh, is_dwg=False, base="plan",
        elements=[{"aktion": "loeschen", "layer": "SANITAER"}],
    )

    assert name == "plan.dxf"
    assert media == "application/dxf"
    assert format_ == "dxf"
    assert "geloescht: 1" in log[0]
    assert daten.startswith(b"  0")                # DXF-Kopf
    assert len(daten) > 0


def test_modify_drawing_ergebnis_ist_wieder_lesbar(tmp_path, zeichnung):
    roh = open(zeichnung, "rb").read()

    daten, _, _, _, _ = modify_drawing(
        roh, is_dwg=False, base="plan",
        elements=[{"aktion": "hinzufuegen", "element": "Auslass",
                   "position": "300,300"}],
    )

    ergebnis = tmp_path / "ergebnis.dxf"
    ergebnis.write_bytes(daten)
    doc = ezdxf.readfile(str(ergebnis))            # wirft bei kaputter Datei
    assert "GENESIS_NEU" in doc.layers


def test_modify_drawing_verlangt_libredwg_fuer_dwg_eingabe(monkeypatch, zeichnung):
    monkeypatch.setattr("dwg_core.have", lambda cmd: False)
    roh = open(zeichnung, "rb").read()

    with pytest.raises(RuntimeError, match="DWG-Leser nicht verfuegbar"):
        modify_drawing(roh, is_dwg=True, base="plan", elements=[])
