"""Phase 26.1: full sidebar + legend separation by mode."""
import pathlib

import pytest

from app.server import app as flask_app

ROOT = pathlib.Path(__file__).resolve().parent.parent
HTML = (ROOT / "app" / "templates" / "live.html").read_text(encoding="utf-8")
JS = (ROOT / "app" / "static" / "js" / "live.js").read_text(encoding="utf-8")


@pytest.fixture()
def client():
    flask_app.config["TESTING"] = True
    return flask_app.test_client()


WX_ONLY = ["card-wxhaz", "card-avail-wx", "legend-states", "legend-weather", "sections-wx"]
TRAF_ONLY = ["card-hazards", "card-avail-traf", "legend-flow", "legend-inc",
             "legend-haz", "sections-traf"]


def test_mode_specific_ids_exist():
    for el in WX_ONLY + TRAF_ONLY:
        assert f'id="{el}"' in HTML, f"missing #{el}"


def test_traffic_sections_hidden_by_default():
    for el in ["card-hazards", "card-avail-traf", "legend-flow", "legend-inc", "legend-haz"]:
        seg = HTML.split(f'id="{el}"')[0][-120:]
        assert "hidden" in seg, f"#{el} not hidden by default"


def test_all_mode_panels_toggled_by_single_function():
    assert "function applyModePanels" in JS
    body = JS.split("function applyModePanels")[1].split("\n}\n")[0]
    for el in (WX_ONLY + TRAF_ONLY + ["card-weather", "card-traffic", "card-nearme",
               "live-kpis", "live-kpis-traffic", "kpi-note-weather", "kpi-note-traffic",
               "lbl-lyr-weather", "lbl-lyr-traffic", "lbl-lyr-incidents",
               "badge-weather", "badge-traffic"]):
        assert el in body, f"#{el} not driven by applyModePanels"


def test_hazards_split_by_source():
    assert "hazards-wx" in JS
    wx = JS.split("hazards-wx")[1].split("const box")[0]
    assert "TomTom" not in wx  # weather hazards card: no TomTom content
    assert "Open-Meteo" in wx


def test_availability_split_by_mode():
    assert "WX_AVAIL" in JS and "TRAF_AVAIL" in JS
    assert "availability-wx" in JS and "availability-traf" in JS
    assert 'getElementById(\'availability\')' not in JS  # combined card gone


def test_served_page_has_split_panels(client):
    html = client.get("/live").data.decode()
    assert "Weather Alerts" in html
    assert "Traffic Service Availability" in html
    assert "Weather &amp; Research Availability" in html or "Weather & Research Availability" in html
    assert "LIVE DATA AVAILABILITY" not in html
    assert "v=ph261" in html


def test_availability_endpoint_layers_unchanged(client):
    layers = {l["layer"] for l in client.get("/api/live/status").get_json()["layers"]}
    assert {"Weather", "Traffic", "Reported incidents", "Official accident records",
            "Hazards", "Government data watch"} <= layers
