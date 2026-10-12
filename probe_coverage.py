import io
import json
import math
import urllib.request

BASE = 'https://morth-accident-analytics.onrender.com'
CITIES = [
    ('Delhi-N', 28.61, 77.21), ('Chandigarh-N', 30.73, 76.78),
    ('Chennai-S', 13.08, 80.27), ('Bengaluru-S', 12.97, 77.59),
    ('Kolkata-E', 22.57, 88.36), ('Bhubaneswar-E', 20.30, 85.83),
    ('Mumbai-W', 19.08, 72.88), ('Ahmedabad-W', 23.03, 72.58),
    ('Bhopal-C', 23.26, 77.41), ('Nagpur-C', 21.15, 79.09),
]


def latlon_to_tile(lat, lon, z):
    n = 2 ** z
    x = int((lon + 180.0) / 360.0 * n)
    lat_r = math.radians(lat)
    y = int((1.0 - math.asinh(math.tan(lat_r)) / math.pi) / 2.0 * n)
    return x, y


def get(path, timeout=90):
    try:
        with urllib.request.urlopen(BASE + path, timeout=timeout) as r:
            return r.status, r.headers.get('Content-Type'), r.read()
    except Exception as e:
        return f'ERR {e}', None, b''


def png_stats(body):
    try:
        from PIL import Image
        im = Image.open(io.BytesIO(body)).convert('RGBA')
        px = list(im.getdata())
        opaque = sum(1 for p in px if p[3] > 10)
        return f'{im.size} opaque={opaque}/{len(px)}'
    except ImportError:
        return f'{len(body)} bytes (no PIL)'


rows = []
for name, lat, lon in CITIES:
    for z in (7, 11):
        x, y = latlon_to_tile(lat, lon, z)
        st, ct, body = get(f'/api/live/traffic/tile/relative0/{z}/{x}/{y}.png')
        rows.append((name, z, x, y, st, ct, png_stats(body)))
    st, ct, body = get(f'/api/live/traffic/segment?lat={lat}&lon={lon}')
    try:
        d = json.loads(body)
        seg = (d.get('status'), d.get('current_speed_kmh'), d.get('free_flow_speed_kmh')) if st == 200 else d
    except Exception:
        seg = body[:80]
    rows.append((name, 'seg', '-', '-', st, ct, seg))

for r in rows:
    print(r)
with open('coverage_matrix.json', 'w') as f:
    json.dump([list(map(str, r)) for r in rows], f, indent=1)
print('saved coverage_matrix.json')
