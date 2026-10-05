"""Phase 14 final integration tests: labels, about/footer, endpoints, freeze."""
import io

from app.server import app as flask_app


def _client():
    flask_app.config["TESTING"] = True
    return flask_app.test_client()


def test_research_label_present():
    html = _client().get("/").get_data(as_text=True)
    assert "VERIFIED RESEARCH DATA" in html


def test_about_section_present():
    html = _client().get("/").get_data(as_text=True)
    assert "About this project" in html
    assert "do not prove causation" in html or "association, not causation" in html
    assert "/live" in html


def test_footer_present():
    html = _client().get("/").get_data(as_text=True)
    assert "<footer" in html
    assert "MoRTH" in html


def test_live_label_present():
    html = _client().get("/live").get_data(as_text=True)
    assert "LIVE EXTERNAL DATA" in html


def test_research_dashboard_loads():
    assert _client().get("/").status_code == 200


def test_key_endpoints_ok():
    c = _client()
    assert c.get("/api/live/status").status_code == 200
    assert c.get("/api/audit_details").status_code == 200
    assert c.get("/api/metadata").status_code == 200


def test_benchmark_zero_mismatch():
    d = _client().get("/api/audit_details").get_json()
    assert d["zero_mismatch"] is True


def test_live_endpoints_isolated_from_research():
    c = _client()
    before = c.get("/api/audit_details").get_json()
    c.get("/api/live/weather/summary")
    c.get("/api/live/traffic/flow")
    c.get("/api/live/traffic/incidents")
    c.get("/api/live/watch/scan")
    after = c.get("/api/audit_details").get_json()
    assert before == after


def test_bw_helpers_defined_once():
    src = open("app/static/js/app.js", encoding="utf-8").read()
    assert src.count("function bwStyle(") == 1
    assert src.count("function bwLine(") == 1
    assert src.count("function bwBar(") == 1
    assert src.count("function renderChartById(") == 1


def test_g6_g9_trace_bindings():
    src = open("app/static/js/app.js", encoding="utf-8").read()
    assert "dash: st.dash" in src and "symbol: st.symbol" in src


def test_no_chart_crash_strings():
    src = open("app/static/js/app.js", encoding="utf-8").read()
    assert "bwStyle is not defined" not in src


def test_demo_flow_doc_exists():
    import os
    assert os.path.exists(
        "FINAL_SUBMISSION_PACKAGE/07_DEFENSE/FINAL_LIVE_WEBSITE_DEMO_FLOW.md")
