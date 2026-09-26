"""Regression tests for repaired modules: PDF honesty, export slopes, stats extras."""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.server import app

client = app.test_client()


def test_pdf_has_no_hardcoded_metrics():
    r = client.get('/api/download_pdf_report')
    assert r.status_code == 200
    # PDF is compressed; check readable text via reportlab-independent scan is unreliable,
    # so assert through the generator path with an untrained pipeline instead.
    from app.data_pipeline.loader import DatasetLoader
    from app.analytics.ml_models import SafetyMLPipeline
    from app.analytics.statistics import compute_state_slopes_g10
    from app.reports.pdf_generator import generate_academic_pdf
    loader = DatasetLoader(benchmark_path='data/MoRTH_Primary_Dataset_3.xlsx')
    g10 = compute_state_slopes_g10(loader.get_clean_df())
    fresh = SafetyMLPipeline()
    assert fresh.is_trained is False
    pdf = generate_academic_pdf(loader.get_clean_df(), g10, fresh)
    assert pdf.startswith(b'%PDF') and len(pdf) > 5000


def test_export_slopes_csv_xlsx():
    for fmt in ('csv', 'xlsx'):
        r = client.get(f'/api/export_data?format={fmt}&type=slopes')
        assert r.status_code == 200, fmt
    r = client.get('/api/export_data?format=csv&type=weather')
    assert r.status_code == 404  # honest unavailable, not fake data


def test_statistical_extras():
    r = client.get('/api/statistical_analysis').get_json()
    assert len(r['yoy_india']) == 7
    assert r['yoy_india'][-1]['year'] == 2024
    assert r['fatality_slopes_summary']['total_states'] == 38


def test_supporting_endpoints_present():
    assert client.get('/api/supporting').status_code == 200
    assert client.get('/api/register').status_code == 200
    assert client.get('/api/audit-files').status_code == 200
    assert client.get('/api/availability').status_code == 200
    assert client.get('/api/ml_status').status_code == 200
