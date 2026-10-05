"""Phase 13 Live Monitor routes. Strictly separated from research modules."""
from flask import Blueprint, jsonify, render_template, request

from app.live import weather as live_weather

live_bp = Blueprint("live", __name__)


@live_bp.route("/live")
def live_page():
    return render_template("live.html")


@live_bp.route("/api/live/status", methods=["GET"])
def live_status():
    return jsonify({
        "status": "success",
        "layers": [
            {"layer": "Weather", "state": "AVAILABLE",
             "note": "Open-Meteo live feed"},
            {"layer": "Traffic", "state": "AWAITING_API_KEY",
             "note": "Awaiting Phase 13.3 traffic integration"},
            {"layer": "Reported incidents", "state": "AWAITING_API",
             "note": "Awaiting traffic incident API — Phase 13.3"},
            {"layer": "Official accident records", "state": "NOT_AVAILABLE",
             "note": "iRAD/eDAR is access-restricted; not publicly available"},
            {"layer": "Hazards", "state": "PARTIAL",
             "note": "Weather-driven hazards only until Phase 13.3"},
            {"layer": "Government data watch", "state": "PLANNED",
             "note": "Phase 13.4"},
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
