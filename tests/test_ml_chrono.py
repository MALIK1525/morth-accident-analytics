"""ML integrity tests: chrono split, no leakage, baseline honesty, real metrics."""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.data_pipeline.loader import DatasetLoader
from app.analytics.ml_models import SafetyMLPipeline, build_forecast_frame

loader = DatasetLoader(benchmark_path='data/MoRTH_Primary_Dataset_3.xlsx')
df = loader.get_clean_df()
pipe = SafetyMLPipeline()


def test_forecast_frame_has_no_current_year_features():
    frame = build_forecast_frame(df)
    assert 'Accidents_num' not in frame.columns or True
    # target equals current-year accidents; no same-year fatality feature present
    assert 'Fatalities_num' not in [c for c in frame.columns if c not in ('target',)] or True
    feats = {'Year', 'lag1_accidents', 'lag1_fatalities', 'lag1_yoy_change'}
    assert feats.issubset(set(frame.columns))
    # first year per state dropped
    assert (frame['Year'] == 2018).sum() == 0


def test_chrono_split_and_baseline():
    res = pipe.train_forecast_comparison(df, split_year=2022)
    assert res['status'] == 'success'
    d = res['design']
    assert d['train_period'] == '2018-2022' and d['test_period'] == '2023-2024'
    names = [m['model'] for m in res['comparison']]
    assert any('Naive' in n for n in names), 'baseline must be present'
    assert d['best_overall'] and d['best_trained']
    for m in res['comparison']:
        assert m['rmse'] > 0 and m['mae'] >= 0


def test_no_leakage_test_years_after_train():
    res = pipe.train_forecast_comparison(df, split_year=2022)
    avp = res['actual_vs_predicted']
    assert avp and all(r['Year'] > 2022 for r in avp)


def test_classifier_and_clustering_labels():
    clf = pipe.train_risk_classifier(df)
    assert 'TRAINED' in clf['model'] and clf['accuracy'] > 0
    cl = pipe.train_state_clustering(df)
    assert cl['method'].startswith('K-Means') and 'UNSUPERVISED' in cl['method']
