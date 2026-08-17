"""Gemeinsame Fixtures fuer die GENESIS-Tests.

Der Kern (dwg_core) laesst sich vollstaendig ohne LibreDWG pruefen: Alle Tests
arbeiten auf DXF-Dateien, die ezdxf direkt erzeugt. dwg2dxf/dxf2dwg werden nur
fuer echte DWG-Ein- und Ausgabe gebraucht und sind hier nicht noetig.
"""
import os
import sys

import ezdxf
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def leere_zeichnung(tmp_path):
    """Pfad zu einer gueltigen, leeren DXF-Datei."""
    doc = ezdxf.new("R2010")
    pfad = tmp_path / "leer.dxf"
    doc.saveas(pfad)
    return str(pfad)


@pytest.fixture
def zeichnung(tmp_path):
    """DXF mit bekanntem Inhalt.

    Layer "LUEFTUNG":  Kreis  @ (100, 100), Text "AL-01" @ (100, 100)
    Layer "SANITAER":  Kreis  @ (900, 900)
    Layer "0":         Linie  von (0, 0) nach (50, 0)
    """
    doc = ezdxf.new("R2010")
    doc.layers.add("LUEFTUNG")
    doc.layers.add("SANITAER")
    msp = doc.modelspace()

    msp.add_circle((100, 100), 20, dxfattribs={"layer": "LUEFTUNG"})
    text = msp.add_text("AL-01", dxfattribs={"layer": "LUEFTUNG", "height": 25})
    text.set_placement((100, 100))
    msp.add_circle((900, 900), 20, dxfattribs={"layer": "SANITAER"})
    msp.add_line((0, 0), (50, 0), dxfattribs={"layer": "0"})

    pfad = tmp_path / "plan.dxf"
    doc.saveas(pfad)
    return str(pfad)


def lade(pfad):
    """Liest eine DXF-Datei und liefert (doc, modelspace)."""
    doc = ezdxf.readfile(pfad)
    return doc, doc.modelspace()
