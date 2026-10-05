"""Phase 13.3 Live traffic + reported incidents (TomTom, server-side only).

Key comes ONLY from the TOMTOM_API_KEY environment variable — never
hard-coded, never sent to the browser. When the key is missing every
function returns an explicit 'awaiting key' payload; nothing crashes.

Traffic flow uses Flow Segment Data v4 (absolute speeds, per-point).
Incidents use Incident Details v5 (bbox, present validity only).
Only provider-returned fields are used; nothing is invented.
"""
import json
import os
import time
import urllib.parse
import urllib.request

from app.live.weather import MONITORED_CITIES

TIMEOUT_S = 10
FLOW_TTL_S = 120
INCIDENT_TTL_S = 180

# Bounding box covering India: minLon,minLat,maxLon,maxLat
INDIA_BBOX = "68.0,6.0,97.5,37.5"


def has_key():
    return bool(os.environ.get("TOMTOM_API_KEY"))


def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "MoRTH-Live-Monitor/1.0"})
    with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
        return json.loads(resp.read().decode("utf-8"))


def congestion_level(current, free):
    """Speed-ratio -> (label, line weight, dash) for colour-independent display."""
    try:
        r = float(current) / float(free)
    except (TypeError, ValueError, ZeroDivisionError):
        return ("Unknown", 2, "dot")
    if r >= 0.9:
        return ("Free flow", 2, "solid")
    if r >= 0.7:
        return ("Moderate", 3, "solid")
    if r >= 0.5:
        return ("Slow", 4, "solid")
    if r >= 0.3:
        return ("Heavy", 5, "dash")
    return ("Very heavy", 6, "dashdot")


def fetch_flow(lat, lon):
    key = os.environ.get("TOMTOM_API_KEY", "")
    if not key:
        raise RuntimeError("missing key")
    params = urllib.parse.urlencode({
        "point": f"{float(lat)},{float(lon)}",
        "unit": "KMPH",
        "key": key,
    })
    raw = _get(f"https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json?{params}")
    seg = raw.get("flowSegmentData") or {}
    cur = seg.get("currentSpeed")
    free = seg.get("freeFlowSpeed")
    label, weight, dash = congestion_level(cur, free)
    delay = None
    try:
        delay = int(seg.get("currentTravelTime", 0)) - int(seg.get("freeFlowTravelTime", 0))
    except (TypeError, ValueError):
        delay = None
    return {
        "road": seg.get("frc", "Not available"),
        "current_speed_kmh": cur,
        "free_flow_speed_kmh": free,
        "travel_time_s": seg.get("currentTravelTime"),
        "free_flow_travel_time_s": seg.get("freeFlowTravelTime"),
        "delay_s": delay if delay is not None and delay >= 0 else None,
        "road_closure": bool(seg.get("roadClosure", False)),
        "confidence": seg.get("confidence"),
        "condition": label,
        "line_weight": weight,
        "line_dash": dash,
        "source": "TomTom Traffic API",
    }


# TomTom iconCategory -> (label, marker symbol, shape class).
INCIDENT_STYLES = {
    0: ("Unknown", "?", "circle"),
    1: ("Accident report", "!", "triangle"),
    2: ("Fog", "F", "diamond"),
    3: ("Dangerous conditions", "D", "diamond"),
    4: ("Rain", "R", "triangle"),
    5: ("Ice", "I", "diamond"),
    6: ("Jam", "J", "square"),
    7: ("Lane closed", "L", "square"),
    8: ("Road closed", "X", "hexagon"),
    9: ("Road works", "W", "pentagon"),
    10: ("Wind", "~", "diamond"),
    11: ("Flooding", "F", "triangle"),
    12: ("Detour", ">", "square"),
    13: ("Cluster", "#", "circle"),
    14: ("Other", "•", "circle"),
}


def fetch_incidents():
    key = os.environ.get("TOMTOM_API_KEY", "")
    if not key:
        raise RuntimeError("missing key")
    params = urllib.parse.urlencode({
        "bbox": INDIA_BBOX,
        "fields": "{incidents{type,geometry{type,coordinates},properties{id,iconCategory,magnitudeOfDelay,events{description,code},startTime,endTime,roadName,from,to}}}",
        "language": "en-US",
        "timeValidityFilter": "present",
        "key": key,
    })
    raw = _get(f"https://api.tomtom.com/traffic/services/5/incidentDetails?{params}")
    out = []
    incidents = (raw.get("incidents") or raw.get("tm", {}).get("poi", [])) if isinstance(raw, dict) else []
    for inc in incidents:
        props = inc.get("properties", {}) or {}
        cat = props.get("iconCategory", 0)
        try:
            cat = int(cat)
        except (TypeError, ValueError):
            cat = 0
        label, symbol, shape = INCIDENT_STYLES.get(cat, INCIDENT_STYLES[0])
        geom = inc.get("geometry", {}) or {}
        coords = geom.get("coordinates") or []
        lon = lat = None
        try:
            if geom.get("type") == "Point" and len(coords) >= 2:
                lon, lat = float(coords[0]), float(coords[1])
            elif coords and isinstance(coords[0], (list, tuple)):
                flat = coords[0][0] if isinstance(coords[0][0], (list, tuple)) else coords[0]
                lon, lat = float(flat[0]), float(flat[1])
        except (TypeError, ValueError, IndexError):
            lon = lat = None
        events = props.get("events") or []
        out.append({
            "category": label,
            "symbol": symbol,
            "shape": shape,
            "description": (events[0].get("description") if events and isinstance(events[0], dict) else None),
            "road": props.get("roadName") or props.get("from") or "Not available",
            "from": props.get("from"),
            "to": props.get("to"),
            "lat": lat,
            "lon": lon,
            "start_time": props.get("startTime"),
            "end_time": props.get("endTime"),
            "delay_magnitude": props.get("magnitudeOfDelay"),
            "source": "TomTom Traffic API",
        })
    return out


_flow_cache = {"at": 0.0, "data": None}
_inc_cache = {"at": 0.0, "data": None}


def get_flow(force=False):
    now = time.time()
    if not force and _flow_cache["data"] is not None and (now - _flow_cache["at"]) < FLOW_TTL_S:
        out = dict(_flow_cache["data"])
        out["cached"] = True
        return out
    if not has_key():
        return {"status": "awaiting_key",
                "message": "Traffic: Awaiting API key (set TOMTOM_API_KEY)."}
    points, failed = [], []
    for city in MONITORED_CITIES:
        try:
            seg = fetch_flow(city["lat"], city["lon"])
            points.append({"name": city["name"], "lat": city["lat"],
                           "lon": city["lon"], **seg,
                           "observed_at": time.strftime("%H:%M:%S IST", time.localtime(now))})
        except Exception:
            failed.append(city["name"])
    data = {"status": "success" if points else "error",
            "source": "TomTom Traffic API",
            "fetched_at": time.strftime("%H:%M:%S IST", time.localtime(now)),
            "points": points, "failed": failed}
    if not points:
        data["message"] = "Traffic temporarily unavailable"
    _flow_cache.update(at=now, data=data)
    out = dict(data)
    out["cached"] = False
    return out


def get_incidents(force=False):
    now = time.time()
    if not force and _inc_cache["data"] is not None and (now - _inc_cache["at"]) < INCIDENT_TTL_S:
        out = dict(_inc_cache["data"])
        out["cached"] = True
        return out
    if not has_key():
        return {"status": "awaiting_key",
                "message": "Reported incidents: Awaiting API key (set TOMTOM_API_KEY)."}
    try:
        items = fetch_incidents()
    except Exception:
        stale = _inc_cache["data"]
        if stale and stale.get("points"):
            out = dict(stale)
            out.update(cached=True, stale=True)
            return out
        return {"status": "error", "message": "Incident feed temporarily unavailable",
                "points": [], "fetched_at": None}
    data = {"status": "success",
            "source": "TomTom Traffic API",
            "fetched_at": time.strftime("%H:%M:%S IST", time.localtime(now)),
            "points": items,
            "count": len(items)}
    _inc_cache.update(at=now, data=data)
    out = dict(data)
    out["cached"] = False
    return out


def clear_caches():
    _flow_cache.update(at=0.0, data=None)
    _inc_cache.update(at=0.0, data=None)
