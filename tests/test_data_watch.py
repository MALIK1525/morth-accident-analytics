"""Phase 13.4 Government Data Watch tests (research suite untouched)."""
import json
import os

import pytest

from app.live import watch as live_watch
from app.server import app as flask_app


@pytest.fixture()
def client():
    flask_app.config["TESTING"] = True
    return flask_app.test_client()


CKAN_PAGE = {"result": {"results": [{
    "id": "abc", "name": "road-accidents-2024", "title": "Road Accidents 2024",
    "notes": "State-wise accidents and fatalities, MoRTH report tables.",
    "organization": {"title": "Government of India (GoI)"},
    "metadata_created": "2025-01-01", "metadata_modified": "2025-06-01"}]}}


class FakeResp:
    def __init__(self, payload, raw=False):
        self._payload = payload
        self._raw = raw

    def read(self, n=-1):
        if self._raw:
            return self._payload[:n] if n and n > 0 else self._payload
        return json.dumps(self._payload).encode()

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _patch(monkeypatch, handler):
    monkeypatch.setattr("urllib.request.urlopen", handler)


def _ckan_ok(monkeypatch, page=None):
    def fake(req, timeout=None):
        url = req.full_url if hasattr(req, "full_url") else req.get_full_url()
        if "package_search" in url:
            return FakeResp(CKAN_PAGE)
        return FakeResp(b"<html>MoRTH reports</html>", raw=True)
    _patch(monkeypatch, fake)


def test_opencity_discovery(monkeypatch, tmp_path):
    monkeypatch.setattr(live_watch, "HISTORY_PATH", str(tmp_path / "h.json"))
    _ckan_ok(monkeypatch)
    items, failed = live_watch.fetch_opencity()
    assert items and failed == []
    assert items[0]["source"] == "OpenCity"
    assert items[0]["relevance"] == "RELEVANT"


def test_duplicate_detection(monkeypatch, tmp_path):
    monkeypatch.setattr(live_watch, "HISTORY_PATH", str(tmp_path / "h.json"))
    monkeypatch.setattr(live_watch, "PAGE_WATCHERS", [])
    _ckan_ok(monkeypatch)
    live_watch.clear_cache()
    first = live_watch.scan(force=True)
    assert first["counts"]["new"] >= 1
    live_watch.clear_cache()
    second = live_watch.scan(force=True)
    assert second["counts"]["new"] == 0


def test_updated_detection(monkeypatch, tmp_path):
    monkeypatch.setattr(live_watch, "HISTORY_PATH", str(tmp_path / "h.json"))
    monkeypatch.setattr(live_watch, "PAGE_WATCHERS", [])
    _ckan_ok(monkeypatch)
    live_watch.clear_cache()
    live_watch.scan(force=True)
    CKAN_PAGE["result"]["results"][0]["metadata_modified"] = "2025-09-01"
    live_watch.clear_cache()
    third = live_watch.scan(force=True)
    assert third["counts"]["updated"] >= 1
    CKAN_PAGE["result"]["results"][0]["metadata_modified"] = "2025-06-01"


def test_source_classification():
    assert live_watch.detect_vintage("NCRB ADSI report") == "NCRB"
    assert live_watch.detect_vintage("MoRTH year book") == "MoRTH"


def test_relevance_classification():
    r = live_watch.classify_relevance("Road Accidents 2024", "fatalities by state")
    assert r["relevance"] == "RELEVANT"
    r2 = live_watch.classify_relevance("Municipal Budget", "city spending")
    assert r2["relevance"] == "NOT_RELEVANT"


def test_vintage_separation_in_compat():
    c = live_watch.compatibility_audit("ADSI 2023", "NCRB traffic accidents")
    assert c["vintage"] == "NCRB"
    assert "never merge" in c["vintage_warning"].lower()


def test_geography_detection():
    assert "District" in live_watch.detect_geography("district-wise accidents")
    assert "City" in live_watch.detect_geography("million-plus cities")


def test_stock_flow_distinction():
    r = live_watch.classify_relevance("Vahan registrations", "monthly vehicle flow data")
    assert r["exposure_candidate"] is True
    assert "FLOW" in r["stock_or_flow"]


def test_review_queue_dir_only(monkeypatch, tmp_path):
    monkeypatch.setattr(live_watch, "REVIEW_DIR", str(tmp_path / "rq"))

    def fake(req, timeout=None):
        return FakeResp(b"a,b\n1,2", raw=True)
    _patch(monkeypatch, fake)
    dest = live_watch.queue_download("https://example.com/data.csv")
    assert os.path.dirname(os.path.abspath(dest)) == os.path.abspath(str(tmp_path / "rq"))


def test_download_rejects_non_http():
    with pytest.raises(ValueError):
        live_watch.queue_download("ftp://example.com/x.csv")


def test_protected_paths_static():
    import app.live.watch as w
    src = open(w.__file__, encoding="utf-8").read()
    for banned in ("02_VERIFIED_DATA", "research_analysis", "MoRTH_Primary",
                   "ORIGINPRO", "FINAL_BTECH", "FINAL_SUBMISSION"):
        assert banned not in src


def test_scan_writes_only_watch_dir(monkeypatch, tmp_path):
    monkeypatch.setattr(live_watch, "HISTORY_PATH", str(tmp_path / "h.json"))
    monkeypatch.setattr(live_watch, "PAGE_WATCHERS", [])
    _ckan_ok(monkeypatch)
    live_watch.clear_cache()
    live_watch.scan(force=True)
    assert os.path.exists(str(tmp_path / "h.json"))


def test_missing_datagovin_key(monkeypatch):
    monkeypatch.delenv("DATA_GOV_IN_API_KEY", raising=False)
    assert live_watch.fetch_datagovin()["status"] == "awaiting_key"


def test_timeout_graceful(monkeypatch):
    import socket

    def fake(req, timeout=None):
        raise socket.timeout("t")
    _patch(monkeypatch, fake)
    with pytest.raises(Exception):
        live_watch.fetch_page_snapshot(live_watch.PAGE_WATCHERS[0])


def test_malformed_ckan(monkeypatch):
    def fake(req, timeout=None):
        return FakeResp({"bad": True})
    _patch(monkeypatch, fake)
    items, _ = live_watch.fetch_opencity()
    assert items == []


def test_page_unavailable_status(monkeypatch, tmp_path):
    import urllib.error
    monkeypatch.setattr(live_watch, "HISTORY_PATH", str(tmp_path / "h.json"))
    monkeypatch.setattr(live_watch, "PAGE_WATCHERS", live_watch.PAGE_WATCHERS)

    def fake(req, timeout=None):
        url = req.full_url if hasattr(req, "full_url") else req.get_full_url()
        if "package_search" in url:
            return FakeResp({"result": {"results": []}})
        raise urllib.error.HTTPError(url, 404, "nf", {}, None)
    _patch(monkeypatch, fake)
    live_watch.clear_cache()
    data = live_watch.scan(force=True)
    assert all(p["status"] == "SOURCE_UNAVAILABLE" for p in data["pages"])
    assert data["status"] == "success"  # scan itself survives


def test_no_auto_integration_surface():
    import app.live.routes as r
    src = open(r.__file__, encoding="utf-8").read()
    assert "benchmark" not in src.lower()


def test_freshness_and_scan_endpoint(client, monkeypatch, tmp_path):
    monkeypatch.setattr(live_watch, "HISTORY_PATH", str(tmp_path / "h.json"))
    monkeypatch.setattr(live_watch, "PAGE_WATCHERS", [])
    _ckan_ok(monkeypatch)
    live_watch.clear_cache()
    r = client.get("/api/live/watch/scan?refresh=1")
    d = r.get_json()
    assert d["status"] == "success"
    assert "scanned_at" in d and "counts" in d


def test_download_endpoint_validation(client):
    r = client.post("/api/live/watch/download", json={"url": "ftp://x/y"})
    assert r.status_code == 400
    r2 = client.post("/api/live/watch/download", json={})
    assert r2.status_code == 400


def test_filter_fields_present(client, monkeypatch, tmp_path):
    monkeypatch.setattr(live_watch, "HISTORY_PATH", str(tmp_path / "h.json"))
    monkeypatch.setattr(live_watch, "PAGE_WATCHERS", [])
    _ckan_ok(monkeypatch)
    live_watch.clear_cache()
    d = client.get("/api/live/watch/scan?refresh=1").get_json()
    item = d["datasets"][0]
    for field in ("status", "relevance", "source", "compatibility",
                  "detected_at", "url"):
        assert field in item
    assert "vintage" in item["compatibility"]


def test_watch_page_served(client):
    html = client.get("/live").get_data(as_text=True)
    assert "Government Data Watch" in html
    assert "discovery only" in html.lower() or "Discovery only" in html


def test_pib_manual_card(client, monkeypatch, tmp_path):
    monkeypatch.setattr(live_watch, "HISTORY_PATH", str(tmp_path / "h.json"))
    monkeypatch.setattr(live_watch, "PAGE_WATCHERS", [])
    _ckan_ok(monkeypatch)
    live_watch.clear_cache()
    d = client.get("/api/live/watch/scan?refresh=1").get_json()
    assert d["pib"]["status"] == "manual_check"
