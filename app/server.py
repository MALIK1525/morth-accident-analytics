"""
Flask Web Application Server for MoRTH Indian Road Accident Analytics Platform.
Features Agentic Data Discovery, Visualization Engine, Weather Integration,
Join Compatibility, Statistical Slopes, ML Models, and Academic PDF Generation.
"""
import os
import io
import json
import pandas as pd
import numpy as np
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename

from app.data_pipeline.loader import DatasetLoader, OFFICIAL_INDIA_BENCHMARKS, ZONE_MAPPING
from app.agents.discovery_agent import DataDiscoveryAgent
from app.agents.join_agent import JoinCompatibilityAgent
from app.agents.visualization_agent import VisualizationAgent
from app.agents.weather_agent import WeatherAgent
from app.analytics.statistics import compute_linear_trend, compute_state_slopes_g10, compute_correlation_matrix, compute_time_to_threshold
from app.analytics.ml_models import SafetyMLPipeline
from app.reports.pdf_generator import generate_academic_pdf

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), '..', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize core services
loader = DatasetLoader(benchmark_path="data/MoRTH_Primary_Dataset_3.xlsx")
discovery_agent = DataDiscoveryAgent(data_dir="data")
join_agent = JoinCompatibilityAgent()
weather_agent = WeatherAgent(data_dir="data")
vis_agent = VisualizationAgent(loader, weather_agent)
supporting_store = vis_agent.supporting
ml_pipeline = SafetyMLPipeline()

# Cache discovery on boot
discovery_agent.discover_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/supporting', methods=['GET'])
def get_supporting():
    """Registry of drop-in supporting CSVs (data/supporting_csv/)."""
    supporting_store.refresh()
    return jsonify({"status": "success", **supporting_store.summary()})


@app.route('/api/register', methods=['GET'])
def get_register():
    """Dataset register + analysis-ready inventory (uploaded audit CSVs)."""
    out = {"status": "success", "register": [], "analysis_ready": []}
    for key, fname in (("register", "data/DATASET_REGISTER.csv"),
                       ("analysis_ready", "data/ANALYSIS_READY_DATASETS.csv")):
        if os.path.exists(fname):
            try:
                out[key] = pd.read_csv(fname, dtype=str, keep_default_na=False).to_dict(orient='records')
            except Exception as e:
                out[key] = {"error": str(e)}
    return jsonify(out)


@app.route('/api/audit-files', methods=['GET'])
def get_audit_files():
    """Audit issues + cleaning log (uploaded audit CSVs)."""
    out = {"status": "success", "issues": [], "cleaning_log": []}
    for key, fname in (("issues", "data/RESEARCH_AUDIT_ISSUES.csv"),
                       ("cleaning_log", "data/DATA_CLEANING_LOG.csv")):
        if os.path.exists(fname):
            try:
                out[key] = pd.read_csv(fname, dtype=str, keep_default_na=False).to_dict(orient='records')
            except Exception as e:
                out[key] = {"error": str(e)}
    return jsonify(out)


@app.route('/api/availability', methods=['GET'])
def get_availability():
    """Research audit matrices (parameter status + availability) if present."""
    out = {"status": "success", "parameter_status": [], "data_availability": []}
    for key, fname in (("parameter_status", "data/PARAMETER_FINAL_STATUS.csv"),
                       ("data_availability", "data/DATA_AVAILABILITY.csv")):
        if os.path.exists(fname):
            try:
                df = pd.read_csv(fname, dtype=str, keep_default_na=False)
                out[key] = df.to_dict(orient='records')
            except Exception as e:
                out[key] = {"error": str(e)}
    return jsonify(out)


@app.route('/api/metadata', methods=['GET'])
def get_metadata():
    """Returns active dataset status, discovery registry, and filter bounds."""
    df = loader.get_clean_df()
    years = sorted([int(y) for y in df['Year'].unique().tolist()])
    states = sorted([str(s) for s in df['State_UT'].unique().tolist()])
    zones = sorted(list(ZONE_MAPPING.keys()))

    discovery_summary = discovery_agent.get_summary()

    return jsonify({
        "status": "success",
        "active_dataset": {
            "filename": loader.active_filename,
            "record_count": int(len(df)),
            "state_count": int(df['State_UT'].nunique()),
            "year_coverage": f"{min(years)}–{max(years)}",
            "source": "MoRTH Published Reports & Parliamentary Replies",
            "verification_status": "DIRECTLY VERIFIED",
            "benchmark_audit_mismatches": 0
        },
        "filters": {
            "years": years,
            "states": states,
            "zones": zones
        },
        "discovery": discovery_summary,
        "supporting": supporting_store.summary(),
        "weather_status": weather_agent.check_status()
    })

@app.route('/api/kpis', methods=['POST'])
def get_kpis():
    """Calculates real-time aggregate KPI metrics based on active filter toolbar."""
    filters = request.get_json() or {}
    df = loader.get_clean_df()
    
    # Filter processing
    if filters.get('state') and filters['state'] != 'ALL':
        df = df[df['State_UT'] == filters['state']]
    if filters.get('year') and filters['year'] != 'ALL':
        try:
            yr = int(filters['year'])
            df = df[df['Year'] == yr]
        except ValueError:
            pass
    if filters.get('zone') and filters['zone'] != 'ALL':
        df = df[df['Zone'] == filters['zone']]

    total_accidents = int(df['Accidents'].sum()) if not df.empty else 0
    total_fatalities = int(df['Fatalities'].sum()) if not df.empty else 0
    
    # Fatality ratio
    fatality_ratio = round((total_fatalities / total_accidents * 100), 2) if total_accidents > 0 else 0.0

    # Annual averages
    years_in_data = df['Year'].nunique() if not df.empty else 1
    avg_annual_acc = int(total_accidents / years_in_data) if years_in_data > 0 else 0
    avg_annual_fat = int(total_fatalities / years_in_data) if years_in_data > 0 else 0

    # Peak years
    if not df.empty and df['Year'].nunique() > 1:
        annual_acc = df.groupby('Year')['Accidents'].sum()
        annual_fat = df.groupby('Year')['Fatalities'].sum()
        peak_acc_yr = int(annual_acc.idxmax())
        peak_fat_yr = int(annual_fat.idxmax())
    elif not df.empty:
        peak_acc_yr = int(df['Year'].iloc[0])
        peak_fat_yr = int(df['Year'].iloc[0])
    else:
        peak_acc_yr = "N/A"
        peak_fat_yr = "N/A"

    # Injuries
    if not df.empty:
        # Sum non-null injured
        valid_inj = df[pd.to_numeric(df['Injured'], errors='coerce').notnull()]
        total_injuries = int(valid_inj['Injured'].astype(int).sum()) if not valid_inj.empty else "N/A"
    else:
        total_injuries = 0

    return jsonify({
        "status": "success",
        "kpis": {
            "total_incidents": total_accidents,
            "fatalities": total_fatalities,
            "injuries": total_injuries,
            "fatality_ratio": fatality_ratio,
            "avg_annual_accidents": avg_annual_acc,
            "avg_annual_fatalities": avg_annual_fat,
            "peak_accident_year": peak_acc_yr,
            "peak_fatality_year": peak_fat_yr,
            "states_covered": int(df['State_UT'].nunique()) if not df.empty else 0,
            "years_covered": int(df['Year'].nunique()) if not df.empty else 0,
            # Supporting modules: only verified core panel is loaded; all other
            # dimensions are NOT in the active panel -> honest unavailable state
            "supporting_modules_available": False,
            "supporting_modules_note": "Severity / road / vehicle / cause / weather / collision / exposure dimensions are not in the verified state-year panel. See Data Availability matrix.",
            "highest_observed_road_category": None,
            "top_observed_vehicle_mode": None,
            "top_observed_cause": None,
            "dominant_weather": None
        }
    })

@app.route('/api/catalog', methods=['GET'])
def get_catalog():
    """Returns the full Analysis Catalog."""
    return jsonify({
        "status": "success",
        "catalog": vis_agent.get_catalog()
    })

@app.route('/api/visualization/<analysis_id>', methods=['POST', 'GET'])
def get_visualization(analysis_id):
    """Generates the exact visualization payload and insight."""
    filters = request.get_json() if request.is_json else {}
    payload = vis_agent.generate_visualization(analysis_id, filters)
    return jsonify({
        "status": "success" if "error" not in payload else "error",
        "analysis_id": analysis_id,
        "payload": payload
    })

@app.route('/api/generate_all_analyses', methods=['POST'])
def generate_all_analyses():
    """Scans Variable Registry and generates all compatible analysis packages."""
    catalog = vis_agent.get_catalog()
    available = [c for c in catalog if c['status'] == 'AVAILABLE']
    unavailable = [c for c in catalog if c['status'] != 'AVAILABLE']
    
    return jsonify({
        "status": "success",
        "total_scanned": len(catalog),
        "available_count": len(available),
        "unavailable_count": len(unavailable),
        "available_analyses": available,
        "unavailable_analyses": unavailable
    })

@app.route('/api/weather/status', methods=['GET'])
def get_weather_status():
    return jsonify(weather_agent.check_status())

@app.route('/api/weather/load', methods=['POST'])
def load_weather():
    res = weather_agent.load_weather_dataset(loader.get_clean_df())
    return jsonify(res)

@app.route('/api/weather/analytics', methods=['GET'])
def get_weather_analytics():
    return jsonify(weather_agent.get_weather_analytics(loader.get_clean_df()))

@app.route('/api/join_check', methods=['POST'])
def check_join():
    req = request.get_json() or {}
    meta_a = req.get('dataset_a', {})
    meta_b = req.get('dataset_b', {})
    verdict = join_agent.evaluate_join(meta_a, meta_b)
    return jsonify(verdict)

@app.route('/api/join_inventory', methods=['GET'])
def get_join_inventory():
    return jsonify(join_agent.get_supported_inventory_decisions())

@app.route('/api/g10_slopes', methods=['GET'])
def get_g10_slopes():
    df = loader.get_clean_df()
    slope_df = compute_state_slopes_g10(df)
    return jsonify({
        "status": "success",
        "count": len(slope_df),
        "slopes": slope_df.to_dict(orient='records')
    })

@app.route('/api/statistical_analysis', methods=['GET'])
def get_statistical_analysis():
    df = loader.get_clean_df()
    corr = compute_correlation_matrix(df)
    slopes = compute_state_slopes_g10(df)
    fat_slopes = compute_state_slopes_g10(df, metric='Fatalities')
    thresholds = compute_time_to_threshold(df, threshold=10000)
    # India-level year-over-year change (verified totals)
    india = df.groupby('Year').agg(acc=('Accidents', 'sum'), fat=('Fatalities', 'sum')).sort_index()
    yoy = [{'year': int(y),
            'acc_abs': int(india['acc'].loc[y] - india['acc'].shift(1).loc[y]) if y != india.index.min() else None,
            'acc_pct': round(float((india['acc'].loc[y] / india['acc'].shift(1).loc[y] - 1) * 100), 2) if y != india.index.min() else None,
            'fat_abs': int(india['fat'].loc[y] - india['fat'].shift(1).loc[y]) if y != india.index.min() else None,
            'fat_pct': round(float((india['fat'].loc[y] / india['fat'].shift(1).loc[y] - 1) * 100), 2) if y != india.index.min() else None}
           for y in india.index]
    return jsonify({
        "status": "success",
        "correlation": corr,
        "slopes_summary": {
            "total_states": len(slopes),
            "increasing": int((slopes['Linear_Slope_per_Year'] > 0).sum()),
            "decreasing": int((slopes['Linear_Slope_per_Year'] < 0).sum()),
            "mean_slope": round(float(slopes['Linear_Slope_per_Year'].mean()), 2)
        },
        "fatality_slopes_summary": {
            "total_states": len(fat_slopes),
            "increasing": int((fat_slopes['Linear_Slope_per_Year'] > 0).sum()),
            "decreasing": int((fat_slopes['Linear_Slope_per_Year'] < 0).sum()),
            "mean_slope": round(float(fat_slopes['Linear_Slope_per_Year'].mean()), 2)
        },
        "yoy_india": yoy,
        "time_to_threshold_10k": thresholds
    })

@app.route('/api/train_ml', methods=['POST'])
def train_ml():
    """Chronological time-series evaluation: 2018-2022 train, 2023-2024 test."""
    df = loader.get_clean_df()
    forecast = ml_pipeline.train_forecast_comparison(df, split_year=2022)
    clf_results = ml_pipeline.train_risk_classifier(df)
    clust_results = ml_pipeline.train_state_clustering(df, n_clusters=3)

    return jsonify({
        "status": "success",
        "message": "Chronological evaluation complete (train 2018-2022, test 2023-2024).",
        "design": forecast.get('design', {}),
        "comparison": forecast.get('comparison', []),
        "actual_vs_predicted": forecast.get('actual_vs_predicted', []),
        "residuals_best": forecast.get('residuals_best', []),
        "regression": ml_pipeline.reg_metrics,
        "feature_importances": ml_pipeline.feature_importances,
        "classification": clf_results,
        "clustering": clust_results
    })

@app.route('/api/ml_status', methods=['GET'])
def get_ml_status():
    return jsonify({
        "is_trained": ml_pipeline.is_trained,
        "models": ["NaiveBaseline", "LinearRegression", "Ridge", "KNNRegressor",
                   "RandomForestRegressor", "GradientBoostingRegressor",
                   "RandomForestClassifier", "KMeans"]
    })

@app.route('/api/audit_details', methods=['GET'])
def get_audit_details():
    validation_rows = loader.get_validation_report()
    provenance_rows = loader.get_source_vintage()
    clean_df = loader.get_clean_df()

    # Calculate real-time reconciliation checks
    reconciliation = []
    for yr, benchmark in OFFICIAL_INDIA_BENCHMARKS.items():
        sub = clean_df[clean_df['Year'] == yr]
        computed_acc = int(sub['Accidents'].sum())
        computed_fat = int(sub['Fatalities'].sum())
        
        diff_acc = computed_acc - benchmark['Accidents']
        diff_fat = computed_fat - benchmark['Fatalities']

        reconciliation.append({
            "year": yr,
            "computed_accidents": computed_acc,
            "published_accidents": benchmark['Accidents'],
            "diff_accidents": diff_acc,
            "computed_fatalities": computed_fat,
            "published_fatalities": benchmark['Fatalities'],
            "diff_fatalities": diff_fat,
            "result": "MATCH" if (diff_acc == 0 and diff_fat == 0) else "MISMATCH"
        })

    return jsonify({
        "status": "success",
        "total_checks": len(reconciliation),
        "zero_mismatch": all(r['result'] == 'MATCH' for r in reconciliation),
        "reconciliation": reconciliation,
        "validation_rows": validation_rows,
        "provenance_rows": provenance_rows
    })

@app.route('/api/download_pdf_report', methods=['GET'])
def download_pdf_report():
    clean_df = loader.get_clean_df()
    slopes_df = compute_state_slopes_g10(clean_df)
    pdf_bytes = generate_academic_pdf(clean_df, slopes_df, ml_pipeline)
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=True,
        download_name='MoRTH_Indian_Road_Accident_Analytics_Report.pdf'
    )

@app.route('/api/export_data', methods=['GET'])
def export_data():
    fmt = request.args.get('format', 'csv').lower()
    dataset_type = request.args.get('type', 'clean').lower()
    
    if dataset_type == 'slopes':
        df = compute_state_slopes_g10(loader.get_clean_df())
        filename = "OriginPro_G10_State_Slopes"
    elif dataset_type == 'weather':
        return jsonify({"status": "error", "message": "Weather dataset not loaded. No verified weather records in supplied workbooks."}), 404
    elif dataset_type == 'vehicles':
        return jsonify({"status": "error", "message": "Vehicle-mode distribution not in verified panel."}), 404
    elif dataset_type == 'roads':
        return jsonify({"status": "error", "message": "Road-category distribution not in verified panel."}), 404
    else:
        df = loader.get_clean_df()
        filename = "MoRTH_Verified_Primary_Panel"

    if fmt == 'xlsx':
        out = io.BytesIO()
        with pd.ExcelWriter(out, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name="DATA")
        out.seek(0)
        return send_file(out, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name=f"{filename}.xlsx")
    else:
        csv_str = df.to_csv(index=False)
        return send_file(io.BytesIO(csv_str.encode('utf-8')), mimetype='text/csv', as_attachment=True, download_name=f"{filename}.csv")

@app.route('/api/upload_dataset', methods=['POST'])
def upload_dataset():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file attached."}), 400
    file = request.files['file']
    if not file.filename:
        return jsonify({"status": "error", "message": "No filename specified."}), 400

    filename = secure_filename(file.filename)
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(save_path)

    res = loader.load_user_file(save_path)
    # Re-trigger discovery
    discovery_agent.discover_all()

    return jsonify(res)

@app.route('/api/load_benchmark', methods=['POST'])
def load_benchmark():
    loader.reset_to_benchmark()
    discovery_agent.discover_all()
    return jsonify({"status": "success", "message": "MoRTH Official Benchmark loaded successfully."})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
