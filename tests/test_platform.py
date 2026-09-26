"""
Comprehensive Verification Suite for MoRTH Road Accident Research Platform.
Tests Data Discovery, Join Compatibility, Visualization Generation, Weather Agent,
Reconciliation Audit, OLS Slopes, Machine Learning, and Flask REST Endpoints.
"""
import unittest
import json
import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.data_pipeline.loader import DatasetLoader, OFFICIAL_INDIA_BENCHMARKS
from app.agents.discovery_agent import DataDiscoveryAgent
from app.agents.join_agent import JoinCompatibilityAgent
from app.agents.visualization_agent import VisualizationAgent
from app.agents.weather_agent import WeatherAgent
from app.analytics.statistics import compute_state_slopes_g10, compute_correlation_matrix
from app.analytics.ml_models import SafetyMLPipeline
from app.server import app

class TestPlatformAgents(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loader = DatasetLoader(benchmark_path="data/MoRTH_Primary_Dataset_3.xlsx")
        cls.clean_df = cls.loader.get_clean_df()
        cls.client = app.test_client()

    def test_01_reconciliation_zero_discrepancy(self):
        """Confirm 100% zero-discrepancy between state sums and published MoRTH totals."""
        for yr, expected in OFFICIAL_INDIA_BENCHMARKS.items():
            sub = self.clean_df[self.clean_df['Year'] == yr]
            acc_sum = int(sub['Accidents'].sum())
            fat_sum = int(sub['Fatalities'].sum())
            self.assertEqual(acc_sum, expected['Accidents'], f"Year {yr} accidents mismatch")
            self.assertEqual(fat_sum, expected['Fatalities'], f"Year {yr} fatalities mismatch")

    def test_02_discovery_agent(self):
        """Confirm Data Discovery Agent scans all workbooks and builds Variable Registry."""
        agent = DataDiscoveryAgent(data_dir="data")
        summary = agent.discover_all()
        self.assertGreaterEqual(summary['workbooks_count'], 3)
        self.assertGreater(summary['registered_variables_count'], 10)
        self.assertIn('Accidents', summary['available_parameters'])
        self.assertIn('Fatalities', summary['available_parameters'])
        self.assertIn('Weather_Condition', summary['unavailable_parameters'])

    def test_03_join_compatibility_agent(self):
        """Confirm Join Compatibility Agent blocks unsafe joins and allows safe joins."""
        join_agent = JoinCompatibilityAgent()
        
        # Unsafe join: MoRTH vs NCRB
        res_unsafe = join_agent.evaluate_join(
            {"source": "MoRTH", "geography": "State", "years": [2022], "granularity": "State-Year"},
            {"source": "NCRB", "geography": "State", "years": [2022], "granularity": "State-Year"}
        )
        self.assertEqual(res_unsafe['verdict'], "UNSAFE")
        self.assertFalse(res_unsafe['can_join'])

        # Safe join: State-Year matching
        res_safe = join_agent.evaluate_join(
            {"source": "MoRTH", "geography": "State", "years": [2018, 2019], "granularity": "State-Year"},
            {"source": "MoRTH", "geography": "State", "years": [2018, 2019], "granularity": "State-Year"}
        )
        self.assertEqual(res_safe['verdict'], "SAFE")
        self.assertTrue(res_safe['can_join'])

    def test_04_visualization_agent(self):
        """Confirm Visualization Agent catalog has all Tiers and generates valid payloads."""
        vis_agent = VisualizationAgent(self.loader)
        catalog = vis_agent.get_catalog()
        self.assertGreaterEqual(len(catalog), 10)

        # Test core graphs (verified panel only; supporting tiers stay honestly unavailable)
        for gid in ['G1', 'G2', 'G4', 'G7', 'G8', 'G10']:
            payload = vis_agent.generate_visualization(gid)
            self.assertNotIn('error', payload, f"Failed generating {gid}")
            self.assertIn('data', payload)
            self.assertIn('insight', payload)
        for gid in ['RD-01', 'VH-01', 'CS-01', 'SV-01']:
            payload = vis_agent.generate_visualization(gid)
            self.assertIn('error', payload, f"{gid} should stay unavailable without supporting files")

    def test_05_weather_agent(self):
        """Weather stays honestly unavailable: no IMD files exist in this workspace."""
        wx_agent = WeatherAgent(data_dir="data")
        status = wx_agent.check_status()
        self.assertIn('file_available', status)
        self.assertFalse(status['file_available'])
        self.assertFalse(status['loaded'])
        analytics = wx_agent.get_weather_analytics(self.clean_df)
        self.assertEqual(analytics['status'], "UNAVAILABLE")

    def test_06_statistical_slopes_g10(self):
        """Confirm OriginPro G10 OLS slopes are computed for all 38 reporting jurisdictions."""
        slopes_df = compute_state_slopes_g10(self.clean_df)
        self.assertEqual(len(slopes_df), 38)
        self.assertIn('Linear_Slope_per_Year', slopes_df.columns)
        self.assertIn('R2', slopes_df.columns)
        self.assertIn('p_value', slopes_df.columns)

    def test_07_machine_learning_pipeline(self):
        """Confirm ML Pipeline trains without error and produces valid test evaluations."""
        ml = SafetyMLPipeline()
        self.assertFalse(ml.is_trained)
        res = ml.train_forecast_comparison(self.clean_df, split_year=2022)
        self.assertEqual(res['status'], 'success')
        self.assertTrue(ml.is_trained)
        self.assertTrue(any('Naive' in m['model'] for m in res['comparison']))
        rf = next(m for m in res['comparison'] if m['model'] == 'Random Forest Regressor')
        self.assertGreater(rf['r2'], 0.5)

        clf_res = ml.train_risk_classifier(self.clean_df)
        self.assertIn('accuracy', clf_res)

        clust_res = ml.train_state_clustering(self.clean_df)
        self.assertEqual(len(clust_res['cluster_profiles']), 3)

    def test_08_rest_endpoints(self):
        """Confirm all Flask REST endpoints respond with HTTP 200."""
        # Metadata
        res = self.client.get('/api/metadata')
        self.assertEqual(res.status_code, 200)

        # KPIs default All Years
        res = self.client.post('/api/kpis', json={"state": "ALL", "year": "ALL", "zone": "ALL"})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['kpis']['total_incidents'], 3141577) # Sum across 2018-2024 panel

        # G1 Visualization
        res = self.client.post('/api/visualization/G1', json={})
        self.assertEqual(res.status_code, 200)

        # Audit Details
        res = self.client.get('/api/audit_details')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.get_json()['zero_mismatch'])

        # Slopes
        res = self.client.get('/api/g10_slopes')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.get_json()['slopes']), 38)

        # PDF Download
        res = self.client.get('/api/download_pdf_report')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.mimetype, 'application/pdf')
        self.assertGreater(len(res.data), 5000)

if __name__ == '__main__':
    unittest.main()
