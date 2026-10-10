"""Phase 19: map interaction mapping, tooltip/panel, geolocation, recovery."""
import json
import re


def _norm(s):
    return re.sub(r"\s+", " ", (s or "").lower().replace("&", "and")).strip()


def _js():
    return open("app/static/js/india_map.js", encoding="utf-8").read()


def test_all_benchmark_entities_resolve():
    from app.server import app
    with app.test_client() as c:
        states = c.get("/api/live/state-intel").get_json()["states"]
    fc = json.load(open("app/static/geo/india_states.geojson", encoding="utf-8"))
    js = _js()
    assert "andaman and nicobar" in js  # alias present
    geo = [_norm(f["properties"]["name"]) for f in fc["features"]]
    assert any("andaman" in g for g in geo)
    # every benchmark entity: direct norm match OR alias-covered
    alias_targets = {_norm(a) for a in
                     ["Dadra & Nagar Haveli and Daman & Diu",
                      "Dadra & Nagar Haveli", "Daman & Diu",
                      "Andaman & Nicobar Islands"]}
    idx = {_norm(b) for b in states}
    missing = [b for b in states
               if _norm(b) not in geo and _norm(b) not in alias_targets]
    assert missing == [], missing


def test_tooltip_and_panel_fields():
    js = _js()
    for token in ("Accidents:", "Fatalities:", "Injured:",
                  "Not available for this year",
                  "Current temperature:", "not live counts",
                  "Historical statistics"):
        assert token in js, token


def test_selection_search_reset_wired():
    js = _js()
    for token in ("selectState", "fillStateSearch", "btn-india-reset",
                  "stateStyle(true)", "resetStyle"):
        assert token in js, token


def test_choropleth_is_counts_not_risk():
    js = _js()
    html = open("app/templates/live.html", encoding="utf-8").read()
    assert "choroOpacity" in js and "NOT risk" in html
    low = js.lower()
    for banned in ("risk score", "risk map", "high-risk", "high risk",
                   "risk prediction", "at-risk", "risk heatmap"):
        assert banned not in low, banned


def test_tooltip_bound_once_with_status():
    js = _js()
    assert "setBoundaryStatus" in js
    assert "bindTooltip(() => stateTooltip(name)" in js  # bound once, sticky auto-open
    assert "interactive: true" in js
    html = open("app/templates/live.html", encoding="utf-8").read()
    assert 'id="boundary-status"' in html


def test_geolocation_gated_and_private():
    js = _js()
    assert js.index("btn-near-me") < js.index("getCurrentPosition")
    for banned in ("localStorage", "sessionStorage", "analytics", "console.log(pos"):
        assert banned not in js, banned


def test_no_credentials_or_coords_in_urls():
    js = _js()
    assert "apikey" not in js.lower()
    # only the two sanctioned same-origin weather calls (state centroid, near-me)
    assert js.count("/api/live/weather?lat=") == 2


def test_weather_point_contract():
    from app.server import app
    with app.test_client() as c:
        r = c.get("/api/live/weather?lat=abc&lon=0")
        assert r.status_code == 400
