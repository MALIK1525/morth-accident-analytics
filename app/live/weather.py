"""Phase 13 Live Monitor — Open-Meteo weather client (stdlib only).

Server-side proxy: the browser never calls Open-Meteo directly.
No API key required. All values pass through untouched; missing
fields are returned as None (frontend shows 'Not available').
"""
import json
import time
import urllib.parse
import urllib.request

BASE_URL = "https://api.open-meteo.com/v1/forecast"
TIMEOUT_S = 10

# Last provider failure classification (exception class + short message only;
# the request URL carries no credentials, so nothing secret can leak here).
_last_error = {"at": None, "kind": None, "detail": None}

# Monitored locations (city proxy points; NOT state measurements).
MONITORED_CITIES = [
    {"name": "Delhi", "lat": 28.61, "lon": 77.21},
    {"name": "Mumbai", "lat": 19.08, "lon": 72.88},
    {"name": "Chennai", "lat": 13.08, "lon": 80.27},
    {"name": "Kolkata", "lat": 22.57, "lon": 88.36},
    {"name": "Bengaluru", "lat": 12.97, "lon": 77.59},
    {"name": "Hyderabad", "lat": 17.38, "lon": 78.48},
    {"name": "Ahmedabad", "lat": 23.03, "lon": 72.58},
    {"name": "Pune", "lat": 18.52, "lon": 73.86},
    {"name": "Jaipur", "lat": 26.91, "lon": 75.79},
    {"name": "Lucknow", "lat": 26.85, "lon": 80.95},
]

# WMO weather-code -> (label, icon, shape) for colour-independent markers.
def describe_code(code):
    try:
        code = int(code)
    except (TypeError, ValueError):
        return ("Not available", "?", "circle")
    if code == 0:
        return ("Clear sky", "\u2600", "circle")
    if code in (1, 2):
        return ("Partly cloudy", "\u26c5", "circle")
    if code == 3:
        return ("Overcast", "\u2601", "square")
    if code in (45, 48):
        return ("Fog", "\U0001f32b", "diamond")
    if code in (51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82):
        return ("Rain", "\U0001f327", "triangle")
    if code in (71, 73, 75, 77, 85, 86):
        return ("Snow", "\u2744", "hexagon")
    if code in (95, 96, 99):
        return ("Thunderstorm", "\u26c8", "star")
    return ("Unknown", "?", "circle")


def _fetch(url, attempts=2):
    last = None
    for i in range(attempts):
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "MoRTH-Live-Monitor/1.0"})
            with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            last = e
            _last_error.update(at=time.strftime("%H:%M:%S IST", time.localtime()),
                              kind=type(e).__name__, detail=str(e)[:200])
            time.sleep(1.5 * (i + 1))
    raise last


def fetch_point(lat, lon):
    """Fetch current weather for one coordinate. Raises on failure."""
    lat = float(lat)
    lon = float(lon)
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError("Coordinates out of range.")
    params = urllib.parse.urlencode({
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m,wind_direction_10m",
        "hourly": "visibility",
        "timezone": "Asia/Kolkata",
        "forecast_days": 1,
    })
    raw = _fetch(f"{BASE_URL}?{params}")
    cur = raw.get("current") or {}
    vis = None
    hourly = raw.get("hourly") or {}
    for v in reversed(hourly.get("visibility") or []):
        if isinstance(v, (int, float)):
            vis = v
            break
    label, icon, shape = describe_code(cur.get("weather_code"))
    return {
        "temperature_c": cur.get("temperature_2m"),
        "humidity_pct": cur.get("relative_humidity_2m"),
        "precipitation_mm": cur.get("precipitation"),
        "weather_code": cur.get("weather_code"),
        "condition": label,
        "icon": icon,
        "shape": shape,
        "wind_speed_kmh": cur.get("wind_speed_10m"),
        "wind_direction_deg": cur.get("wind_direction_10m"),
        "visibility_m": vis,
        "observed_at": cur.get("time"),
        "source": "Open-Meteo",
    }


_cache = {"at": 0.0, "data": None, "error": None}
CACHE_TTL_S = 300


def get_summary(force=False):
    """Return cached monitored-location summary; refresh when stale."""
    now = time.time()
    if not force and _cache["data"] is not None and (now - _cache["at"]) < CACHE_TTL_S:
        out = dict(_cache["data"])
        out["cached"] = True
        return out
    points, failed = [], []
    for city in MONITORED_CITIES:
        try:
            obs = fetch_point(city["lat"], city["lon"])
            points.append({"name": city["name"], "lat": city["lat"],
                           "lon": city["lon"], **obs})
        except Exception:
            failed.append(city["name"])
    temps = [p["temperature_c"] for p in points
             if isinstance(p["temperature_c"], (int, float))]
    data = {
        "status": "success" if points else "error",
        "source": "Open-Meteo",
        "fetched_at": time.strftime("%H:%M:%S IST", time.localtime(now)),
        "points": points,
        "failed": failed,
        "summary": {
            "locations_monitored": len(points),
            "rain_affected": sum(1 for p in points
                                 if isinstance(p["precipitation_mm"], (int, float))
                                 and p["precipitation_mm"] > 0),
            "avg_temp_c": round(sum(temps) / len(temps), 1) if temps else None,
            "max_temp_c": max(temps) if temps else None,
            "min_temp_c": min(temps) if temps else None,
        },
    }
    prev = _cache.get("data")
    prev_points = (prev or {}).get("points") or []
    if not points and prev_points:
        out = dict(prev)
        out.update(cached=True, stale=True,
                   stale_note="Provider unreachable; showing last successful update "
                              f"from {prev.get('fetched_at', 'unknown time')}.")
        return out
    _cache.update(at=now, data=data, error=None if points else "all failed")
    return data


def clear_cache():
    _cache.update(at=0.0, data=None, error=None)
