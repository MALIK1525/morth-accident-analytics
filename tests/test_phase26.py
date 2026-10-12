"""Phase 26: mode-aware dashboard — traffic incidents must never render in the weather card."""
import pathlib

import pytest

from app.server import app as flask_app

ROOT = pathlib.Path(__file__).resolve().parent.parent
HTML = (ROOT / "app" / "templates" / "live.html").read_text(encoding="utf-8")
JS = (ROOT / "app" / "static" / "js" / "live.js").read_text(encoding="utf-8")


def test_traffic_card_exists_and_hidden_by_default():
    assert 'id="card-traffic"' in HTML
    assert "Current Traffic" in HTML
    assert 'id="card-traffic"' in HTML and "hidden" in HTML.split('id="card-traffic"')[0][-200:]


def test_weather_card_has_stable_id():
    assert 'id="card-weather"' in HTML
    assert "Current Weather" in HTML


def test_incident_click_renders_into_traffic_card_not_weather():
    # The incident click handler must target #traffic-detail, never #weather-detail.
    idx = JS.find("reported traffic incident")
    assert idx != -1
    window = JS[max(0, idx - 1500):idx]
    assert "showTrafficDetail" in window or "traffic-detail" in window
    assert "getElementById('weather-detail')" not in window


def test_mode_switch_toggles_all_panels():
    assert "function applyModePanels" in JS
    for el in ["card-weather", "card-traffic", "card-nearme", "live-kpis",
               "live-kpis-traffic", "kpi-note-weather", "kpi-note-traffic"]:
        assert el in JS, f"{el} not toggled by applyModePanels"
    assert "applyModePanels(which)" in JS  # called from showTab


def test_traffic_kpis_present():
    for el in ["kpi-tflow", "kpi-tinc", "kpi-tclose", "kpi-tcov"]:
        assert f'id="{el}"' in HTML


def test_no_traffic_attribution_inside_weather_card():
    seg = HTML.split('id="card-weather"')[1].split('id="card-traffic"')[0]
    assert "TomTom" not in seg


@pytest.fixture()
def client():
    flask_app.config["TESTING"] = True
    return flask_app.test_client()


def test_live_page_serves_mode_cards(client):
    html = client.get("/live").data.decode()
    assert "Current Traffic" in html
    assert "Current Weather" in html
    assert "v=ph26" in html
