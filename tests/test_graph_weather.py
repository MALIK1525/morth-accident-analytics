"""Graph + weather repair tests: G1-G10 schema, weather endpoints, NaN-free JSON."""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.server import app

client = app.test_client()
IDS = ['G1', 'G2', 'G3', 'G4', 'G5', 'G6', 'G7', 'G8', 'G9', 'G10']


def test_g1_g10_schema_and_nan_free():
    for i in IDS:
        r = client.post(f'/api/visualization/{i}',
                        json={'state': 'ALL', 'year': 'ALL', 'zone': 'ALL'})
        assert r.status_code == 200, i
        raw = r.data.decode('utf-8')
        assert 'NaN' not in raw and 'Infinity' not in raw, i
        d = r.get_json()
        assert d['status'] == 'success', i
        assert set(d['payload']) >= {'data', 'meta'}, i


def test_g_filters_state_year_zone():
    d = client.post('/api/visualization/G9',
                    json={'state': 'Kerala', 'year': '2020', 'zone': 'ALL'}).get_json()
    assert [s['state'] for s in d['payload']['data']['series']] == ['Kerala']
    d = client.post('/api/visualization/G5',
                    json={'state': 'ALL', 'year': '2022', 'zone': 'ALL'}).get_json()
    assert d['status'] == 'success'


def test_weather_status_truthful():
    d = client.get('/api/weather/status').get_json()
    assert d['status'] == 'AVAILABLE'
    assert d['usable_state_years'] == 236
    assert 'humidity' in str(d.get('variables_unavailable', '')).lower() \
        or any('humidity' in str(v).lower() for v in d.get('variables_unavailable', []))


def test_weather_endpoints_nan_free():
    for m, u, kw in [('GET', '/api/weather/metadata', {}),
                     ('GET', '/api/weather/correlation', {}),
                     ('GET', '/api/weather/analytics', {}),
                     ('POST', '/api/weather/annual', {'state': 'ALL', 'year': 'ALL', 'zone': 'ALL'})]:
        r = client.post(u, json=kw) if m == 'POST' else client.get(u)
        assert r.status_code == 200, u
        raw = r.data.decode('utf-8')
        assert 'NaN' not in raw and 'Infinity' not in raw, u


def test_weather_correlation_matches_phase8():
    d = client.get('/api/weather/correlation').get_json()
    assert d['status'] == 'AVAILABLE'
    vals = {(a['x'], a['y']): a['pearson_r'] for a in d['associations']
            if a.get('status') == 'OK'}
    assert abs(vals[('Annual_Rainfall_mm', 'Accidents')] - (-0.234)) < 0.01
    assert abs(vals[('Annual_Rainfall_mm', 'Fatalities')] - (-0.376)) < 0.01
    assert abs(vals[('Annual_Mean_Tmax_C', 'Accidents')] - 0.452) < 0.01
    assert 'causal' in d['design'].lower() and 'not causal' in d['design'].lower()


def test_weather_excluded_rows_null_not_zero():
    d = client.post('/api/weather/annual',
                    json={'state': 'Lakshadweep', 'year': '2020', 'zone': 'ALL'}).get_json()
    assert d['count'] == 1
    assert d['rows'][0]['rainfall_mm'] is None
    assert d['rows'][0]['available'] is False


def test_weather_zone_filter_narrows():
    d = client.post('/api/weather/annual',
                    json={'state': 'ALL', 'year': 'ALL', 'zone': 'North'}).get_json()
    assert d['count'] == 70
    assert all(r['state'] in ('Jammu & Kashmir', 'Ladakh', 'Himachal Pradesh', 'Punjab',
                              'Chandigarh', 'Haryana', 'Delhi', 'Uttarakhand',
                              'Uttar Pradesh', 'Rajasthan') for r in d['rows'])
    d = client.post('/api/weather/annual',
                    json={'state': 'Punjab', 'year': '2024', 'zone': 'ALL'}).get_json()
    assert d['count'] == 1 and d['rows'][0]['available'] is True
