"""Phase 2.7: supporting-data recovery regression tests.

Every value asserted here comes from the verified MoRTH AR 2024 mirror
CSVs in data/supporting_csv/ (provenance in *.provenance.md). Nothing is
fabricated: tests assert file presence, schema activation, totals
reconciliation with published MoRTH India figures, and benchmark isolation.
"""
import glob
import json
import os

import pytest

from app.data_pipeline.supporting_loader import SupportingDataStore
from app.server import app

SUP = os.path.join('data', 'supporting_csv')

EXPECTED = {
    'road_user': 'road-accidents-2024-fatality-road-user.csv',
    'violation': 'road-accidents-2024-type-of-violation.csv',
    'collision': 'road-accidents-2024-type-of-collision.csv',
    'licence': 'road-accidents-2024-type-of-license.csv',
    'safety_device': 'road-accidents-2024-safety-device.csv',
    'victim_crime_matrix': 'road-accidents-2024-victims-crime-vehicle.csv',
    'cities_overview': 'road-accidents-2024-cities-accidents-fatalities.csv',
    'exposure': 'road-accidents-registrations-density-2014-24.csv',
}


@pytest.fixture(scope='module')
def store():
    return SupportingDataStore()


@pytest.fixture(scope='module')
def client():
    app.config['TESTING'] = True
    return app.test_client()


def test_supporting_csvs_present():
    for fname in EXPECTED.values():
        assert os.path.isfile(os.path.join(SUP, fname)), f'missing {fname}'


def test_provenance_present_for_each_csv():
    for fname in EXPECTED.values():
        path = os.path.join(SUP, fname + '.provenance.md')
        assert os.path.isfile(path), f'missing provenance for {fname}'
        text = open(path, encoding='utf-8').read()
        assert 'MoRTH' in text and 'SHA256' in text


def test_schemas_activate_with_correct_files(store):
    for schema, fname in EXPECTED.items():
        reg = store.get(schema)
        assert reg is not None, f'schema {schema} not activated'
        assert reg['filename'] == fname, f'{schema} misclassified to {reg["filename"]}'
        assert reg['status'] == 'AVAILABLE'


def test_no_unrecognized_supporting_files(store):
    assert store.unrecognized == [], f'unrecognized: {store.unrecognized}'


def test_road_user_2024_reconciles(store):
    t = store.get('road_user')['table']
    assert int(t[t.Year == 2024].Killed.sum()) == 177175


def test_collision_2024_reconciles(store):
    t = store.get('collision')['table']
    assert int(t[t.Year == 2024].Accidents.sum()) == 487707
    assert int(t[t.Year == 2024].Killed.sum()) == 177175


def test_violation_2024_reconciles(store):
    t = store.get('violation')['table']
    assert int(t[t.Year == 2024].Killed.sum()) == 177175
    cats = t.Category.unique().tolist()
    assert any('Over-speeding' in c or 'speeding' in c.lower() for c in cats)
    # total row must not leak in as a category
    assert not any(c.strip().lower() in ('total', 'all india') for c in cats)


def test_licence_covers_2020_2024(store):
    t = store.get('licence')['table']
    assert sorted(t.Year.unique().tolist()) == [2020, 2021, 2022, 2023, 2024]
    assert int(t[(t.Year == 2024)].Accidents.sum()) == 487707


def test_cities_50_records(store):
    t = store.get('cities_overview')['table']
    assert len(t) == 50
    assert 'Delhi' in t['City'].tolist()


def test_exposure_has_vehicle_denominators(store):
    t = store.get('exposure')['table']
    assert t.Year.min() <= 2014
    row22 = t[t.Year == 2022].iloc[0]
    assert row22.notna().sum() >= 5


def test_modules_return_data(client):
    for gid in ['VH-01', 'CS-01', 'CL-01', 'EX-01', 'DL-01', 'SD-01', 'CT-01']:
        r = client.post('/api/visualization/' + gid, json={})
        assert r.status_code == 200, gid
        payload = json.loads(r.data)['payload']
        assert 'data' in payload, f'{gid} has no data'
        assert 'error' not in payload or payload.get('error') is None


def test_benchmark_untouched_by_supporting_data(client):
    r = client.get('/api/audit_details')
    assert json.loads(r.data).get('zero_mismatch') is True
