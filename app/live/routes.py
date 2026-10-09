"""Phase 13 Live Monitor routes. Strictly separated from research modules."""
import os

from flask import Blueprint, jsonify, render_template, request

from app.live import weather as live_weather
from app.live import traffic as live_traffic
from app.live import watch as live_watch

live_bp = Blueprint("live", __name__)


@live_bp.route("/live")
def live_page():
    return render_template("live.html")


@live_bp.route("/api/live/status", methods=["GET"])
def live_status():
    import time as _t
    now = _t.time()

    def _age(cache, ttl):
        at = (cache or {}).get("at", 0) or 0
        age = int(now - at) if at else None
        return {"age_s": age, "stale": bool(at and (now - at) > ttl)}
    return jsonify({
        "status": "success",
        "diagnostics": {
            "tomtom_key_configured": live_traffic.has_key(),
            "datagovin_key_configured": bool(os.environ.get("DATA_GOV_IN_API_KEY")),
            "weather_cache": _age(getattr(live_weather, "_cache", {}), live_weather.CACHE_TTL_S),
            "weather_last_error": getattr(live_weather, "_last_error", {}),
            "traffic_cache": _age(getattr(live_traffic, "_flow_cache", {}), live_traffic.FLOW_TTL_S),
            "note": "Key presence only — values never exposed. Ages are server-cache ages.",
        },
        "layers": [
            {"layer": "Weather", "state": "AVAILABLE",
             "note": "Open-Meteo live feed"},
            {"layer": "Traffic", "state": ("AVAILABLE" if live_traffic.has_key() else "AWAITING_API_KEY"),
             "note": ("TomTom live feed" if live_traffic.has_key() else "Awaiting API key — Phase 13.3 (set TOMTOM_API_KEY)")},
            {"layer": "Reported incidents", "state": ("AVAILABLE" if live_traffic.has_key() else "AWAITING_API"),
             "note": ("TomTom incident feed — NOT official accident records" if live_traffic.has_key() else "Awaiting traffic incident API — Phase 13.3")},
            {"layer": "Official accident records", "state": "NOT_AVAILABLE",
             "note": "iRAD/eDAR is access-restricted; not publicly available"},
            {"layer": "Hazards", "state": "PARTIAL",
             "note": "Weather-driven hazards only until Phase 13.3"},
            {"layer": "Government data watch", "state": "AVAILABLE",
             "note": "OpenCity CKAN + MoRTH/NCRB page checks (Phase 13.4)"},
        ],
    })


@live_bp.route("/api/live/weather", methods=["GET"])
def live_weather_point():
    try:
        obs = live_weather.fetch_point(request.args.get("lat"),
                                       request.args.get("lon"))
    except (TypeError, ValueError) as e:
        return jsonify({"status": "error",
                        "message": f"Invalid coordinates: {e}"}), 400
    except Exception:
        return jsonify({"status": "error",
                        "message": "Weather temporarily unavailable"}), 502
    return jsonify({"status": "success", **obs})


@live_bp.route("/api/live/weather/summary", methods=["GET"])
def live_weather_summary():
    force = (request.args.get("refresh") == "1")
    try:
        return jsonify(live_weather.get_summary(force=force))
    except Exception:
        return jsonify({"status": "error",
                        "message": "Weather temporarily unavailable"}), 502


@live_bp.route("/api/live/watch/scan", methods=["GET"])
def live_watch_scan():
    force = (request.args.get("refresh") == "1")
    try:
        return jsonify(live_watch.scan(force=force))
    except Exception:
        return jsonify({"status": "error",
                        "message": "Data Watch temporarily unavailable"}), 502


@live_bp.route("/api/live/watch/download", methods=["POST"])
def live_watch_download():
    body = request.get_json(silent=True) or {}
    url = (body.get("url") or "").strip()
    if not url:
        return jsonify({"status": "error", "message": "No URL provided."}), 400
    try:
        dest = live_watch.queue_download(url)
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except Exception:
        return jsonify({"status": "error",
                        "message": "Download failed or source unavailable."}), 502
    return jsonify({"status": "success",
                    "message": "Saved to review queue (NOT verified research data).",
                    "path": os.path.basename(dest)})


@live_bp.route("/api/live/traffic/flow", methods=["GET"])
def live_traffic_flow():
    force = (request.args.get("refresh") == "1")
    try:
        return jsonify(live_traffic.get_flow(force=force))
    except Exception:
        return jsonify({"status": "error",
                        "message": "Traffic temporarily unavailable"}), 502


@live_bp.route("/api/live/traffic/incidents", methods=["GET"])
def live_traffic_incidents():
    force = (request.args.get("refresh") == "1")
    try:
        return jsonify(live_traffic.get_incidents(force=force))
    except Exception:
        return jsonify({"status": "error",
                        "message": "Incident feed temporarily unavailable"}), 502
