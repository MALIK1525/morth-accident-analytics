"""Website Phase 2 tests: reusable upload workspace (Mode B) + Mode A preservation."""
import io
import json
import os
import unittest

import pandas as pd

from app.server import app


def _csv_bytes(rows):
    buf = io.BytesIO()
    pd.DataFrame(rows).to_csv(buf, index=False)
    buf.seek(0)
    return buf


SAMPLE = [
    {"State_Name": "Punjab", "Year": 2020, "Acc_Date": "12-03-2020",
     "Accidents": 10, "Deaths": 3, "Weather_Cond": "Rain", "Vehicle_Type": "Car"},
    {"State_Name": "Punjab", "Year": 2021, "Acc_Date": "05-07-2021",
     "Accidents": 12, "Deaths": 4, "Weather_Cond": "Clear", "Vehicle_Type": "Truck"},
    {"State_Name": "Kerala", "Year": 2020, "Acc_Date": "bad-date",
     "Accidents": 7, "Deaths": 1, "Weather_Cond": "Rain", "Vehicle_Type": "Bus"},
    {"State_Name": "Punjab", "Year": 2021, "Acc_Date": "05-07-2021",
     "Accidents": 12, "Deaths": 4, "Weather_Cond": "Clear", "Vehicle_Type": "Truck"},
    {"State_Name": "Kerala", "Year": 2021, "Acc_Date": "01-01-2021",
     "Accidents": "NV", "Deaths": None, "Weather_Cond": None, "Vehicle_Type": "Car"},
]


class Phase2UploadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        cls.client = app.test_client()

    def _upload(self, content, filename, ctype="text/csv"):
        return self.client.post("/api/upload_dataset", data={
            "file": (content, filename)}, content_type="multipart/form-data")

    def test_01_csv_upload(self):
        res = self._upload(_csv_bytes(SAMPLE), "sample.csv")
        self.assertEqual(res.status_code, 200, res.get_data(as_text=True))
        body = res.get_json()
        self.assertEqual(body["status"], "success")
        self.assertEqual(body["dataset_mode"], "upload")

    def test_02_xlsx_upload(self):
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as w:
            pd.DataFrame(SAMPLE).to_excel(w, index=False)
        buf.seek(0)
        res = self._upload(buf, "sample.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        self.assertEqual(res.status_code, 200, res.get_data(as_text=True))

    def test_03_json_upload(self):
        buf = io.BytesIO(json.dumps(SAMPLE).encode())
        res = self._upload(buf, "sample.json", "application/json")
        self.assertEqual(res.status_code, 200, res.get_data(as_text=True))

    def test_04_unsupported_rejected(self):
        res = self._upload(io.BytesIO(b"evil"), "run.exe",
                           "application/octet-stream")
        self.assertEqual(res.status_code, 400)
        self.assertIn("Unsupported", res.get_json()["message"])

    def test_05_empty_rejected(self):
        buf = io.BytesIO(b"a,b\n")
        res = self._upload(buf, "empty.csv")
        self.assertEqual(res.status_code, 400)

    def test_06_inspection(self):
        self._upload(_csv_bytes(SAMPLE), "sample.csv")
        res = self.client.get("/api/dataset/inspect")
        body = res.get_json()
        self.assertEqual(body["rows"], 5)
        self.assertEqual(body["columns"], 7)
        self.assertEqual(body["duplicate_rows"], 1)

    def test_07_mapping(self):
        self._upload(_csv_bytes(SAMPLE), "sample.csv")
        body = self.client.get("/api/dataset/mapping").get_json()
        m = body["mapping"]
        self.assertEqual(m["State"]["column"], "State_Name")
        self.assertEqual(m["Date"]["column"], "Acc_Date")
        self.assertEqual(m["Weather"]["column"], "Weather_Cond")

    def test_08_ambiguous_unmapped(self):
        rows = [{"ABC123": 1, "ZZZ9": 2}]
        self._upload(_csv_bytes(rows), "weird.csv")
        m = self.client.get("/api/dataset/mapping").get_json()["mapping"]
        unmapped = [p for p, e in m.items() if e["status"] == "Unmapped"]
        self.assertTrue(len(unmapped) > 0)
        # restore usable sample
        self._upload(_csv_bytes(SAMPLE), "sample.csv")

    def test_09_quality_missing_dup(self):
        self._upload(_csv_bytes(SAMPLE), "sample.csv")
        q = self.client.get("/api/dataset/quality").get_json()
        self.assertEqual(q["duplicate_rows"], 1)
        self.assertGreaterEqual(q["checks"].get("missing_Weather", 0), 1)
        self.assertGreaterEqual(q["checks"].get("invalid_dates", 0), 1)

    def test_10_cleaning_log(self):
        self._upload(_csv_bytes(SAMPLE), "sample.csv")
        body = self.client.post("/api/dataset/clean").get_json()
        self.assertEqual(body["raw_rows"], 5)
        self.assertEqual(body["clean_rows"], 4)
        self.assertTrue(any("duplicate" in s for s in body["cleaning_log"]))

    def test_11_readiness(self):
        self._upload(_csv_bytes(SAMPLE), "sample.csv")
        fams = self.client.get("/api/dataset/readiness").get_json()["families"]
        self.assertEqual(fams["year_trend"]["status"], "AVAILABLE")
        self.assertEqual(fams["weather"]["status"], "AVAILABLE")
        self.assertEqual(fams["gis"]["status"], "NOT AVAILABLE")
        self.assertEqual(fams["exposure_normalized"]["status"], "NOT AVAILABLE")

    def test_12_manual_mapping(self):
        self._upload(_csv_bytes(SAMPLE), "sample.csv")
        res = self.client.post("/api/dataset/mapping",
                               json={"parameter": "City", "column": "Vehicle_Type"})
        self.assertEqual(res.status_code, 200)
        m = res.get_json()["mapping"]
        self.assertEqual(m["City"]["confidence"], "Manual")
        # unknown parameter rejected
        res = self.client.post("/api/dataset/mapping",
                               json={"parameter": "Nope", "column": "Vehicle_Type"})
        self.assertEqual(res.status_code, 400)

    def test_13_separation_benchmark_intact(self):
        self._upload(_csv_bytes(SAMPLE), "sample.csv")
        res = self.client.post("/api/dataset/switch", json={"mode": "benchmark"})
        self.assertEqual(res.status_code, 200)
        kpis = self.client.post("/api/kpis",
                                json={"state": "ALL", "year": "ALL",
                                      "zone": "ALL"}).get_json()["kpis"]
        # benchmark totals unchanged (254 obs: 38 states, 2018-2024)
        self.assertEqual(kpis["states_covered"], 38)
        self.assertEqual(kpis["peak_accident_year"], 2024)
        # switch back to upload
        res = self.client.post("/api/dataset/switch", json={"mode": "upload"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["active_mode"], "upload")

    def test_14_switching_invalid(self):
        res = self.client.post("/api/dataset/switch", json={"mode": "bogus"})
        self.assertEqual(res.status_code, 400)

    def test_15_path_traversal(self):
        res = self._upload(_csv_bytes(SAMPLE), "../../evil.csv")
        # secure_filename neutralises; must not be an error nor escape uploads
        self.assertIn(res.status_code, (200, 400))
        updir = os.path.abspath("uploads")
        for f in os.listdir(updir):
            self.assertTrue(os.path.abspath(os.path.join(updir, f)).startswith(updir))

    def test_16_size_cap_configured(self):
        self.assertEqual(app.config["MAX_CONTENT_LENGTH"], 32 * 1024 * 1024)

    def test_17_g1_regression(self):
        self.client.post("/api/dataset/switch", json={"mode": "benchmark"})
        res = self.client.post("/api/visualization/G1", json={})
        self.assertEqual(res.status_code, 200)
        body = res.get_json()
        self.assertNotIn("NaN", res.get_data(as_text=True)[:100000])

    def test_18_weather_regression(self):
        res = self.client.get("/api/weather/status")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["status"], "AVAILABLE")

    def test_19_status_endpoint(self):
        st = self.client.get("/api/dataset/status").get_json()
        self.assertIn(st["active_mode"], ("benchmark", "upload"))
        self.assertTrue(st["benchmark_preserved"])


if __name__ == "__main__":
    unittest.main()
