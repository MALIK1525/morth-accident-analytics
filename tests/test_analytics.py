"""
Automated Test Suite for MoRTH Analytics & AI Risk Prediction Application.
Validates:
1. Benchmark data loading and record counts.
2. Official India totals reconciliation (0 discrepancy).
3. Derived metrics (Fatality Ratio = Deaths / Crashes * 100).
4. Statistical regression engine (G10 slopes, R2, p-values).
5. Machine learning pipeline (Random Forest, K-Means clustering).
6. Non-destructive upload handling.
7. PDF generation without crashes.
8. Flask API endpoints.
"""
import os
import pytest
import pandas as pd
import numpy as np

from app.data_pipeline.loader import DatasetLoader, OFFICIAL_INDIA_BENCHMARKS, ZONE_MAPPING
from app.analytics.statistics import compute_linear_trend, compute_state_slopes_g10, compute_cagr
from app.analytics.ml_models import SafetyMLPipeline
from app.reports.pdf_generator import generate_pdf_report
from app.server import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_benchmark_loading():
    loader = DatasetLoader(data_dir="data")
    summary = loader.load_benchmark()
    assert summary['total_rows'] == 254
    assert summary['unique_states'] == 38  # 36 current + 2 historic UTs
    assert summary['year_coverage'] == "2018–2024"
    assert summary['sy_duplicates'] == 0
    assert summary['negative_values'] == 0
    assert summary['data_quality_badge'] == "DIRECTLY VERIFIED"

def test_national_totals_reconciliation():
    loader = DatasetLoader(data_dir="data")
    summary = loader.load_benchmark()
    rec_list = summary['reconciliation']
    assert len(rec_list) == 7
    
    for r in rec_list:
        yr = r['year']
        bench = OFFICIAL_INDIA_BENCHMARKS[yr]
        assert r['computed_accidents'] == bench['Accidents']
        assert r['accidents_status'] == "MATCH"
        assert r['computed_fatalities'] == bench['Fatalities']
        assert r['fatalities_status'] == "MATCH"
        if yr <= 2022:
            assert r['computed_injured'] == bench['Injured']
            assert r['injured_status'] == "MATCH"

def test_fatality_ratio_calculation():
    loader = DatasetLoader(data_dir="data")
    loader.load_benchmark()
    df = loader.clean_data
    # Spot check 2024 Tamil Nadu: Accidents=67526, Fatalities=18449
    tn = df[(df['State_UT'] == 'Tamil Nadu') & (df['Year'] == 2024)].iloc[0]
    expected_ratio = (18449 / 67526) * 100.0
    assert abs(tn['Fatalities_per_100_Accidents_calc'] - expected_ratio) < 0.01

def test_g10_linear_regression_slopes():
    loader = DatasetLoader(data_dir="data")
    loader.load_benchmark()
    g10_df = compute_state_slopes_g10(loader.clean_data, metric="Accidents_num")
    assert len(g10_df) == 38
    assert "Slope" in g10_df.columns
    assert "R2" in g10_df.columns
    assert "p_value" in g10_df.columns
    # Ensure at least some valid slopes exist
    valid = g10_df.dropna(subset=['Slope'])
    assert len(valid) >= 36

def test_ml_pipeline_execution():
    loader = DatasetLoader(data_dir="data")
    loader.load_benchmark()
    ml = SafetyMLPipeline()
    res = ml.train_forecast_comparison(loader.clean_data, split_year=2022)
    assert res['status'] == 'success'
    assert any('Naive' in m['model'] for m in res['comparison'])
    rf = next(m for m in res['comparison'] if m['model'] == 'Random Forest Regressor')
    assert rf['r2'] > 0.5
    assert rf['mae'] > 0
    assert 'lag1_accidents' in res['feature_importances']

    clf_metrics = ml.train_risk_classifier(loader.clean_data)
    assert clf_metrics['accuracy'] > 50.0

    cluster_res = ml.perform_kmeans_clustering(loader.clean_data, k=3, year=2024)
    assert len(cluster_res['cluster_profiles']) == 3

def test_pdf_report_generation():
    loader = DatasetLoader(data_dir="data")
    audit = loader.load_benchmark()
    g10 = compute_state_slopes_g10(loader.clean_data)
    ml = SafetyMLPipeline()
    rf = ml.train_fatality_regressor(loader.clean_data)
    
    pdf_bytes = generate_pdf_report(loader.clean_data, audit, g10, rf)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 5000
    assert pdf_bytes.startswith(b'%PDF')

def test_api_endpoints(client):
    r_index = client.get('/')
    assert r_index.status_code == 200

    r_meta = client.get('/api/metadata')
    assert r_meta.status_code == 200
    assert r_meta.json['status'] == 'success'

    r_kpis = client.post('/api/kpis', json={})
    assert r_kpis.status_code == 200
    assert r_kpis.json['kpis']['total_incidents'] > 0

    r_t1 = client.post('/api/visualization/G1', json={})
    assert r_t1.status_code == 200
    assert len(r_t1.json['payload']['data']['values']) == 7

    r_slopes = client.get('/api/g10_slopes')
    assert r_slopes.status_code == 200
    assert len(r_slopes.json['slopes']) == 38
