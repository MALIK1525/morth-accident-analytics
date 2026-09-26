"""
Time-series ML pipeline for the MoRTH state-year panel.

DESIGN (no leakage):
- Task: predict a state's ANNUAL accident count for year t using ONLY
  information available before year t (lags, YoY change of lags, Year, Zone).
- Same-year contemporaneous variables are NEVER used as features.
- Chronological split: train on Year <= split_year (default 2022),
  test on Year > split_year (2023-2024). No shuffling.
- Models compared against a naive previous-year baseline on identical test rows.
- Primary metric: RMSE. Best overall vs best TRAINED model reported separately.

Terminology: KNN = supervised regressor here; K-Means = unsupervised clustering.
Risk tiers from the classifier are TRAINED model outputs, not heuristics.
"""
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import (RandomForestRegressor, RandomForestClassifier,
                              GradientBoostingRegressor)
from sklearn.metrics import (mean_absolute_error, mean_squared_error, r2_score,
                             accuracy_score, confusion_matrix)

TARGET = 'Accidents'
LAG_FEATURES = ['lag1_accidents', 'lag1_fatalities', 'lag1_yoy_change']
PRIMARY_METRIC = 'rmse'


def build_forecast_frame(clean_df, target=TARGET):
    """State-sorted lag features. First year per state is dropped (no history)."""
    df = clean_df.dropna(subset=['Accidents_num', 'Fatalities_num', 'Year']).copy()
    df = df.sort_values(['State_UT', 'Year'])
    g = df.groupby('State_UT')
    df['lag1_accidents'] = g['Accidents_num'].shift(1)
    df['lag1_fatalities'] = g['Fatalities_num'].shift(1)
    df['lag2_accidents'] = g['Accidents_num'].shift(2)
    df['lag1_yoy_change'] = (df['lag1_accidents'] - df['lag2_accidents']) / df['lag2_accidents'].replace(0, np.nan)
    df['lag1_yoy_change'] = df['lag1_yoy_change'].fillna(0.0)
    df = df.dropna(subset=['lag1_accidents', 'lag1_fatalities']).copy()
    df['target'] = df['Accidents_num'] if target == 'Accidents' else df['Fatalities_num']
    return df


def _feature_matrix(df):
    num = df[['Year', 'lag1_accidents', 'lag1_fatalities', 'lag1_yoy_change']].copy()
    zone = pd.get_dummies(df['Zone'], prefix='Zone', drop_first=True)
    X = pd.concat([num.reset_index(drop=True), zone.reset_index(drop=True)], axis=1)
    return X


def _metrics(y_true, y_pred):
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    mae = float(mean_absolute_error(y_true, y_pred))
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    try:
        r2 = float(r2_score(y_true, y_pred))
    except ValueError:
        r2 = None
    mape = float(np.mean(np.abs((y_true - y_pred) / np.where(y_true == 0, np.nan, y_true))) * 100)
    return {'mae': round(mae, 2), 'rmse': round(rmse, 2), 'r2': round(r2, 4) if r2 is not None else None,
            'mape': round(float(mape), 2) if np.isfinite(mape) else None}


class SafetyMLPipeline:
    def __init__(self):
        self.is_trained = False
        self.design = {}
        self.comparison = []
        self.actual_vs_predicted = []
        self.feature_importances = {}
        self.reg_metrics = {}
        self.clf_metrics = {}
        self.cluster_results = {}

    # ---------- main forecasting comparison ----------
    def train_forecast_comparison(self, clean_df, split_year=2022):
        frame = build_forecast_frame(clean_df)
        train = frame[frame['Year'] <= split_year].copy()
        test = frame[frame['Year'] > split_year].copy()
        if train.empty or test.empty:
            return {'status': 'error', 'message': 'Chronological split left an empty partition.'}

        X_train, y_train = _feature_matrix(train), train['target'].values
        X_test, y_test = _feature_matrix(test), test['target'].values
        # align columns (a zone may be absent from one partition)
        X_train, X_test = X_train.align(X_test, join='outer', axis=1, fill_value=0)

        models = {
            'Naive previous-year baseline': None,
            'Linear Regression': LinearRegression(),
            'Ridge Regression': Ridge(alpha=1.0),
            'KNN Regression (k=5, supervised)': KNeighborsRegressor(n_neighbors=5),
            'Random Forest Regressor': RandomForestRegressor(n_estimators=200, max_depth=8, random_state=42),
            'Gradient Boosting Regressor': GradientBoostingRegressor(random_state=42),
        }
        comparison = []
        preds = {}
        for name, model in models.items():
            if model is None:
                y_pred = test['lag1_accidents'].values  # naive: last year's count
            else:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
            m = _metrics(y_test, y_pred)
            m['model'] = name
            m['trained'] = model is not None
            comparison.append(m)
            preds[name] = np.asarray(y_pred, dtype=float).tolist()
            if name == 'Random Forest Regressor':
                self.feature_importances = dict(sorted(
                    zip(X_train.columns, [round(float(i), 4) for i in model.feature_importances_]),
                    key=lambda kv: kv[1], reverse=True))

        comparison.sort(key=lambda m: m[PRIMARY_METRIC])
        best_overall = comparison[0]['model']
        trained = [m for m in comparison if m['trained']]
        best_trained = min(trained, key=lambda m: m[PRIMARY_METRIC])['model'] if trained else None

        residuals = (y_test - np.asarray(preds[best_trained or best_overall])).tolist()
        self.actual_vs_predicted = [
            {'State_UT': str(s), 'Year': int(y), 'Actual': int(a),
             **{f'Predicted_{n}': int(round(p[i])) for n, p in preds.items()}}
            for i, (s, y, a) in enumerate(zip(test['State_UT'], test['Year'], y_test))]
        self.comparison = comparison
        self.is_trained = True
        self.design = {
            'task': 'Predict state annual accident count for year t from pre-t history only',
            'target': TARGET,
            'features': ['Year'] + LAG_FEATURES + ['Zone (one-hot)'],
            'train_period': f"2018-{split_year}",
            'test_period': f"{split_year + 1}-2024",
            'n_train': int(len(train)), 'n_test': int(len(test)),
            'n_states_train': int(train['State_UT'].nunique()),
            'n_states_test': int(test['State_UT'].nunique()),
            'primary_metric': PRIMARY_METRIC,
            'best_overall': best_overall, 'best_trained': best_trained,
            'leakage_note': 'Features use lags strictly before year t; chronological split; no shuffling.',
        }
        self.reg_metrics = next(m for m in comparison if m['model'] == 'Random Forest Regressor')
        return {'status': 'success', 'design': self.design, 'comparison': comparison,
                'actual_vs_predicted': self.actual_vs_predicted,
                'residuals_best': [round(float(r), 1) for r in residuals],
                'feature_importances': self.feature_importances}

    # ---------- severity-tier classifier (trained, supervised) ----------
    def train_risk_classifier(self, clean_df):
        df = clean_df.dropna(subset=['Accidents_num', 'Fatalities_num', 'Year']).copy()
        ratio = df['Fatalities_num'] / df['Accidents_num'].replace(0, np.nan)
        q33, q66 = ratio.quantile(0.33), ratio.quantile(0.66)
        df['Risk_Category'] = pd.cut(ratio, [-np.inf, q33, q66, np.inf],
                                     labels=['Low severity ratio', 'Moderate severity ratio', 'High severity ratio'])
        df = df.dropna(subset=['Risk_Category'])
        X = pd.concat([df[['Year', 'Accidents_num']].reset_index(drop=True),
                       pd.get_dummies(df['Zone'], prefix='Zone', drop_first=True).reset_index(drop=True)], axis=1)
        y = df['Risk_Category']
        # chronological split to respect time order
        tr = df['Year'] <= 2022
        clf = RandomForestClassifier(n_estimators=150, max_depth=6, random_state=42)
        clf.fit(X[tr.values], y[tr.values])
        pred = clf.predict(X[(~tr).values])
        true = y[(~tr).values]
        acc = float(accuracy_score(true, pred))
        cm = confusion_matrix(true, pred, labels=list(clf.classes_)).tolist()
        self.clf_metrics = {
            'model': 'Random Forest Classifier (TRAINED, supervised)',
            'train_period': '2018-2022', 'test_period': '2023-2024',
            'n_train': int(tr.sum()), 'n_test': int((~tr).sum()),
            'accuracy': round(acc * 100, 2), 'classes': list(clf.classes_),
            'confusion_matrix': cm,
            'label': 'Severity-ratio tier prediction is a trained model output, not a heuristic score.',
        }
        return self.clf_metrics

    # ---------- unsupervised state grouping ----------
    def train_state_clustering(self, clean_df, n_clusters=3, year=2024):
        from sklearn.preprocessing import StandardScaler
        from sklearn.cluster import KMeans
        sub = clean_df[clean_df['Year'] == year].dropna(subset=['Accidents_num', 'Fatalities_num']).copy()
        if len(sub) < n_clusters:
            return {'status': 'error', 'message': 'Fewer states than clusters.'}
        Xs = StandardScaler().fit_transform(sub[['Accidents_num', 'Fatalities_num']].values)
        sub['Cluster'] = KMeans(n_clusters=n_clusters, random_state=42, n_init=10).fit_predict(Xs)
        profiles = []
        for k in range(n_clusters):
            s = sub[sub['Cluster'] == k]
            profiles.append({'cluster_id': k, 'count': int(len(s)),
                             'avg_accidents': round(float(s['Accidents_num'].mean()), 1),
                             'avg_fatalities': round(float(s['Fatalities_num'].mean()), 1),
                             'sample_states': s['State_UT'].head(6).tolist()})
        self.cluster_results = {'status': 'success', 'method': 'K-Means (UNSUPERVISED)',
                                'year': year, 'k': n_clusters, 'cluster_profiles': profiles,
                                'state_assignments': sub[['State_UT', 'Cluster']].to_dict(orient='records')}
        return self.cluster_results

    # ---------- backward-compatible aliases ----------
    def prepare_data(self, clean_df):
        frame = build_forecast_frame(clean_df)
        return frame, None, None

    def train_fatality_regressor(self, clean_df, **kw):
        return self.train_forecast_comparison(clean_df, **kw)

    def train_fatalities_regressor(self, clean_df, **kw):
        return self.train_forecast_comparison(clean_df, **kw)

    def perform_kmeans_clustering(self, clean_df, k=3, **kw):
        return self.train_state_clustering(clean_df, n_clusters=k, **kw)
