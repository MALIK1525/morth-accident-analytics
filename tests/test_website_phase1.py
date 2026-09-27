"""Regression tests for Website Phase 1 fixes: NaN-safe JSON, registry contract, G9 filter."""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.server import app

client = app.test_client()


def test_no_nan_leak_in_json():
    for url in ('/api/g10_slopes', '/api/statistical_analysis', '/api/audit_details'):
        raw = client.get(url).data.decode('utf-8')
        assert 'NaN' not in raw, url
        assert 'Infinity' not in raw, url


def test_g10_insufficient_rows_are_null_not_nan():
    d = client.get('/api/g10_slopes').get_json()
    legacy = [s for s in d['slopes'] if s['State_UT'] in ('Dadra & Nagar Haveli', 'Daman & Diu')]
    assert len(legacy) == 2
    for s in legacy:
        assert s['Linear_Slope_per_Year'] is None
        assert s['p_value'] is None


def test_registry_contract():
    d = client.get('/api/metadata').get_json()
    reg = d['discovery'].get('variable_registry')
    assert isinstance(reg, list) and len(reg) > 100
    assert all(set(v) >= {'variable', 'source', 'sheet', 'granularity', 'coverage', 'status'} for v in reg)


def test_g9_honors_state_filter():
    d = client.post('/api/visualization/G9', json={'state': 'Punjab', 'year': 'ALL', 'zone': 'ALL'}).get_json()
    assert [s['state'] for s in d['payload']['data']['series']] == ['Punjab']


def test_kpi_injury_na_for_unpublished_scope():
    d = client.post('/api/kpis', json={'state': 'Punjab', 'year': '2024', 'zone': 'ALL'}).get_json()
    assert d['kpis']['injuries'] == 'N/A'
