"""
Dataset Workspace agent for the reusable accident-analysis platform (Website Phase 2).

MODE B (user-uploaded dataset) ONLY. The verified MoRTH benchmark (Mode A) is
never touched by this module: it operates on an in-memory copy of the uploaded
file and produces inspection / mapping / quality / cleaning / readiness outputs.

Every numeric value returned is JSON-safe (no NaN / Infinity); unavailable
information is reported as explicit status strings, never fabricated.
"""
import math
import pandas as pd
import numpy as np

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls", ".json"}

# Research parameter framework: standard parameter -> candidate header spellings.
# Confidence HIGH = exact canonical header, MEDIUM = known alias, LOW = weak hint.
PARAMETER_PATTERNS = {
    # A. Accident identification
    "Accident_ID": ["accident_id", "accident id", "crash_id", "case_id", "fir_no", "id"],
    "Date": ["date", "acc_date", "accident_date", "crash_date", "date_of_accident", "dt"],
    "Time": ["time", "acc_time", "accident_time", "crash_time", "hour", "time_of_accident"],
    "Location": ["location", "place", "site", "address", "landmark"],
    # B. Geography
    "State": ["state_ut", "state/ut", "state", "state_name", "state / ut", "ut", "states/uts"],
    "District": ["district", "dist", "district_name"],
    "City": ["city", "town", "urban_agglomeration", "million_plus_city"],
    "Police_Jurisdiction": ["police_station", "police_jurisdiction", "jurisdiction", "ps_name", "thana"],
    "Latitude": ["latitude", "lat", "y_coord"],
    "Longitude": ["longitude", "long", "lng", "lon", "x_coord"],
    # C. Severity
    "Fatal": ["fatal", "fatal_accidents", "fatalities", "deaths", "killed", "persons_killed", "dead"],
    "Grievous_Injury": ["grievous", "grievous_injury", "serious_injury", "greviously_injured"],
    "Minor_Injury": ["minor_injury", "minor", "slight_injury"],
    "Deaths": ["deaths", "fatalities", "killed", "persons_killed", "dead", "no_of_deaths"],
    "Injuries": ["injured", "injuries", "persons_injured", "total_injured", "casualties", "no_of_injured"],
    "Accidents": ["accidents", "total_accidents", "road_accidents", "incidents", "total incidents",
                  "no_of_accidents", "crash_count"],
    # D. Temporal
    "Year": ["year", "accident_year", "reporting_year", "yr"],
    "Month": ["month", "accident_month", "mon"],
    "Day": ["day", "day_of_month", "date_day"],
    "Day_Of_Week": ["day_of_week", "weekday", "dow"],
    "Hour": ["hour", "hour_of_day", "hr"],
    "Day_Night": ["day_night", "day/night", "light_condition_day_night", "daynight"],
    "Season": ["season", "seasonal"],
    # E. Road
    "Road_Type": ["road_type", "road_category", "road_class"],
    "Road_Surface": ["surface", "road_surface", "surface_type"],
    "Road_Condition": ["road_condition", "condition"],
    "Junction": ["junction", "junction_type", "intersection"],
    "Traffic_Control": ["traffic_control", "control", "signal"],
    "Road_Width": ["road_width", "width", "carriageway_width"],
    "Lanes": ["lanes", "no_of_lanes", "lane_count"],
    "Lighting": ["lighting", "light_condition", "street_light"],
    "Urban_Rural": ["urban_rural", "urban/rural", "area_type", "location_type"],
    # F. Vehicle
    "Vehicle_Type": ["vehicle_type", "vehicle", "vehicle_involved", "mode"],
    "Vehicle_Count": ["number_of_vehicles", "no_of_vehicles", "vehicle_count", "vehicles_involved"],
    "Vehicle_Age": ["vehicle_age", "age_of_vehicle"],
    "Manoeuvre": ["manoeuvre", "maneuver", "vehicle_manoeuvre"],
    # G. Driver
    "Driver_Age": ["driver_age", "age_of_driver"],
    "Driver_Gender": ["driver_gender", "gender_of_driver", "driver_sex"],
    "Licence_Status": ["licence_status", "license_status", "licence", "license"],
    "Driver_Experience": ["experience", "driving_experience", "driver_experience"],
    "Alcohol": ["alcohol", "drunk_driving", "drink_and_drive", "alcohol_consumption"],
    "Speeding": ["speeding", "overspeeding", "over_speeding", "high_speed"],
    "Wrong_Side": ["wrong_side", "wrong_side_driving", "wrongside"],
    "Overtaking": ["overtaking", "overtake"],
    "Distraction": ["distraction", "distracted", "mobile_phone"],
    "Fatigue": ["fatigue", "drowsy", "sleep"],
    # H. Cause
    "Cause": ["cause", "accident_cause", "cause_of_accident", "reason", "contributory_cause"],
    # I. Collision
    "Collision_Type": ["collision_type", "collision", "crash_type", "accident_type", "type_of_collision"],
    # J. Environment
    "Weather": ["weather", "weather_condition", "weather_cond"],
    "Rainfall": ["rainfall", "rain", "precipitation", "annual_rainfall_mm"],
    "Temperature": ["temperature", "temp", "tmax", "tmin", "mean_temp"],
    "Humidity": ["humidity", "relative_humidity"],
    "Visibility": ["visibility"],
    "Wind": ["wind", "wind_speed"],
    # K. Exposure
    "Population": ["population", "pop"],
    "Registered_Vehicles": ["registered_vehicles", "vehicles_registered", "vehicle_population"],
    "Traffic_Volume": ["traffic_volume", "aadt", "traffic", "pcu"],
    "Road_Length": ["road_length", "length_of_roads"],
    "Vehicle_Km": ["vehicle_km", "vkt", "vehicle_km_travelled"],
}

# Analysis family -> parameters that can support it (any-of semantics per family).
READINESS_RULES = {
    "india_state_comparison": ["State", "Accidents"],
    "year_trend": ["Year", "Accidents"],
    "seasonal": ["Month", "Accidents"],
    "weather": ["Weather", "Rainfall", "Temperature"],
    "road": ["Road_Type", "Road_Condition", "Road_Surface"],
    "vehicle": ["Vehicle_Type", "Vehicle_Count"],
    "driver": ["Driver_Age", "Driver_Gender", "Licence_Status", "Alcohol", "Speeding"],
    "cause": ["Cause", "Speeding", "Alcohol"],
    "collision": ["Collision_Type"],
    "gis": ["Latitude", "Longitude"],
    "exposure_normalized": ["Population", "Registered_Vehicles", "Road_Length", "Traffic_Volume"],
    "machine_learning": ["Year", "State", "Accidents"],
}


def _safe_int(x):
    try:
        if x is None or (isinstance(x, float) and (math.isnan(x) or math.isinf(x))):
            return None
        return int(x)
    except (TypeError, ValueError):
        return None


def _safe_float(x):
    try:
        f = float(x)
        if math.isnan(f) or math.isinf(f):
            return None
        return f
    except (TypeError, ValueError):
        return None


class UploadWorkspace:
    """Holds ONE active uploaded dataset (Mode B) plus its derived artefacts."""

    def __init__(self):
        self.reset()

    def reset(self):
        self.filename = None
        self.file_type = None
        self.file_size = None
        self.raw_df = None
        self.mapping = {}
        self.manual_overrides = {}
        self.cleaning_log = []

    @property
    def has_dataset(self):
        return self.raw_df is not None

    # ---------- parsing ----------
    def load_file(self, path, original_filename, file_size=None):
        import os
        ext = os.path.splitext(original_filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise ValueError(f"Unsupported file type '{ext}'. Supported: CSV, XLSX, JSON.")
        try:
            if ext == ".csv":
                df = pd.read_csv(path)
            elif ext in (".xlsx", ".xls"):
                xl = pd.ExcelFile(path)
                if not xl.sheet_names:
                    raise ValueError("Workbook contains no sheets.")
                df = xl.parse(xl.sheet_names[0])
            elif ext == ".json":
                df = pd.read_json(path)
                if isinstance(df, pd.Series):
                    df = df.to_frame().T
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Could not parse file as {ext}: {e}")
        if df is None or df.empty or len(df.columns) == 0:
            raise ValueError("Dataset contains no usable rows.")
        # Flatten record-style JSON artefacts; drop fully-empty columns.
        df = df.dropna(axis=1, how="all")
        if len(df.columns) == 0:
            raise ValueError("Dataset contains columns, but all are empty.")
        self.reset()
        self.filename = original_filename
        self.file_type = ext.lstrip(".")
        self.file_size = file_size
        self.raw_df = df
        self.mapping = self._auto_map(df)
        return self.inspect()

    # ---------- inspection ----------
    def inspect(self):
        if not self.has_dataset:
            return {"status": "empty", "message": "No uploaded dataset."}
        df = self.raw_df
        dtypes = {str(c): str(df[c].dtype) for c in df.columns}
        missing = {str(c): _safe_int(int(df[c].isnull().sum())) for c in df.columns}
        sample_unique = {}
        for c in df.columns:
            if df[c].dtype == object or str(df[c].dtype) == "category":
                try:
                    sample_unique[str(c)] = [str(v) for v in df[c].dropna().unique()[:20]]
                except Exception:
                    sample_unique[str(c)] = []
        years = []
        for cand in ("Year", "year", "YEAR", "accident_year"):
            if cand in df.columns:
                try:
                    ys = pd.to_numeric(df[cand], errors="coerce").dropna().astype(int)
                    years = sorted(int(y) for y in ys.unique().tolist())
                    break
                except Exception:
                    pass
        geo = [str(c) for c in df.columns
               if str(c).strip().lower() in ("state", "state_ut", "district", "city")]
        return {
            "status": "success",
            "filename": self.filename,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "rows": _safe_int(len(df)),
            "columns": _safe_int(len(df.columns)),
            "column_names": [str(c) for c in df.columns],
            "dtypes": dtypes,
            "duplicate_rows": _safe_int(int(df.duplicated().sum())),
            "missing_by_column": missing,
            "categorical_samples": sample_unique,
            "year_coverage": years,
            "geographic_columns": geo,
        }

    # ---------- mapping ----------
    def _auto_map(self, df):
        lower = {str(c).strip().lower(): str(c) for c in df.columns}
        mapping = {}
        for param, candidates in PARAMETER_PATTERNS.items():
            found, conf = None, None
            for i, cand in enumerate(candidates):
                if cand in lower:
                    found = lower[cand]
                    conf = "High" if i == 0 else ("Medium" if i < 3 else "Low")
                    break
            if found:
                mapping[param] = {"column": found, "confidence": conf, "status": "Mapped"}
            else:
                mapping[param] = {"column": None, "confidence": None,
                                  "status": "Unmapped",
                                  "reason": "No reliable parameter match"}
        for k, v in self.manual_overrides.items():
            if k in mapping:
                mapping[k] = v
        return mapping

    def get_mapping(self):
        return {"status": "success" if self.has_dataset else "empty",
                "mapping": self.mapping}

    def set_mapping(self, param, column):
        """Manual correction: column=None unmaps the parameter."""
        if not self.has_dataset:
            raise ValueError("No uploaded dataset.")
        if param not in PARAMETER_PATTERNS:
            raise ValueError(f"Unknown research parameter '{param}'.")
        if column is not None and column not in [str(c) for c in self.raw_df.columns]:
            raise ValueError(f"Column '{column}' not present in uploaded dataset.")
        entry = ({"column": column, "confidence": "Manual", "status": "Mapped"}
                 if column else {"column": None, "confidence": None,
                                 "status": "Unmapped", "reason": "Unmapped by user"})
        self.manual_overrides[param] = entry
        self.mapping = self._auto_map(self.raw_df)
        return self.mapping

    # ---------- quality ----------
    def quality_report(self):
        if not self.has_dataset:
            return {"status": "empty", "message": "No uploaded dataset."}
        df = self.raw_df
        m = self.mapping
        out = {"status": "success", "rows": _safe_int(len(df)),
               "duplicate_rows": _safe_int(int(df.duplicated().sum())),
               "empty_columns": [str(c) for c in df.columns if df[c].isnull().all()],
               "constant_columns": [],
               "checks": {}}

        def col(param):
            e = m.get(param, {})
            return e.get("column") if e.get("status") == "Mapped" else None

        # Missingness for mapped core columns
        for param in ("State", "Date", "Accidents", "Fatal", "Deaths", "Injuries",
                      "Cause", "Collision_Type", "Weather"):
            c = col(param)
            if c:
                out["checks"][f"missing_{param}"] = _safe_int(int(df[c].isnull().sum()))
        # Invalid dates
        dc = col("Date")
        if dc:
            parsed = pd.to_datetime(df[dc], errors="coerce", dayfirst=True)
            out["checks"]["invalid_dates"] = _safe_int(
                int(parsed.isnull().sum() - df[dc].isnull().sum()))
            valid = parsed.dropna()
            if not valid.empty:
                out["checks"]["date_range"] = [str(valid.min().date()), str(valid.max().date())]
        # Invalid numerics
        for param in ("Accidents", "Deaths", "Injuries", "Fatal"):
            c = col(param)
            if c:
                nums = pd.to_numeric(df[c], errors="coerce")
                out["checks"][f"invalid_numeric_{param}"] = _safe_int(
                    int(nums.isnull().sum() - df[c].isnull().sum()))
                out["checks"][f"negative_{param}"] = _safe_int(int((nums < 0).sum()))
        # Coordinates
        for param, lo, hi in (("Latitude", -90, 90), ("Longitude", -180, 180)):
            c = col(param)
            if c:
                nums = pd.to_numeric(df[c], errors="coerce")
                bad = nums.isnull() & df[c].notnull()
                oor = ((nums < lo) | (nums > hi)) & df[c].notnull()
                out["checks"][f"invalid_{param}"] = _safe_int(int((bad | oor).sum()))
        for c in df.columns:
            try:
                if df[c].nunique(dropna=True) == 1:
                    out["constant_columns"].append(str(c))
            except Exception:
                pass
        return out

    # ---------- cleaning (transparent, non-destructive) ----------
    def build_clean(self):
        if not self.has_dataset:
            raise ValueError("No uploaded dataset.")
        df = self.raw_df.copy()
        log = []
        n0 = len(df)
        df = df.drop_duplicates()
        removed = n0 - len(df)
        log.append(f"Removed {removed} exact duplicate rows ({n0} -> {len(df)}).")
        m = self.mapping

        def col(param):
            e = m.get(param, {})
            return e.get("column") if e.get("status") == "Mapped" else None

        sc = col("State")
        if sc:
            before = df[sc].astype(str)
            df[sc] = before.str.strip()
            changed = int((before != df[sc]).sum())
            log.append(f"Trimmed whitespace in '{sc}' ({changed} values changed).")
        dc = col("Date")
        if dc:
            parsed = pd.to_datetime(df[dc], errors="coerce", dayfirst=True)
            bad = int(parsed.isnull().sum() - df[dc].isnull().sum())
            log.append(f"Standardized date format in '{dc}' ({bad} invalid dates retained as missing, not dropped).")
        for param in ("Accidents", "Deaths", "Injuries", "Fatal"):
            c = col(param)
            if c:
                nums = pd.to_numeric(df[c], errors="coerce")
                bad = int(nums.isnull().sum() - df[c].isnull().sum())
                df[c + "__num"] = nums
                log.append(f"Coerced '{c}' to numeric as '{c}__num' ({bad} non-numeric retained as missing).")
        log.append(f"Raw upload preserved separately ({n0} rows); analysis dataset has {len(df)} rows.")
        self.cleaning_log = log
        return {"status": "success", "raw_rows": _safe_int(n0),
                "clean_rows": _safe_int(len(df)), "cleaning_log": log}

    # ---------- readiness ----------
    def readiness(self):
        if not self.has_dataset:
            return {"status": "empty", "message": "No uploaded dataset."}
        df = self.raw_df
        mapped = {p for p, e in self.mapping.items() if e.get("status") == "Mapped"}
        fams = {}
        for fam, params in READINESS_RULES.items():
            present = [p for p in params if p in mapped]
            ok = len(present) > 0
            # Require minimum data support: mapped column mostly non-missing.
            support = True
            if ok:
                for p in present:
                    c = self.mapping[p]["column"]
                    try:
                        frac = float(df[c].notnull().mean())
                    except Exception:
                        frac = 0.0
                    if frac < 0.2:
                        support = False
            status = "AVAILABLE" if (ok and support) else "NOT AVAILABLE"
            reason = ("Supported by: " + ", ".join(present)) if status == "AVAILABLE" else (
                "No compatible variable present in uploaded dataset."
                if not ok else "Mapped variable has insufficient non-missing data (<20%).")
            fams[fam] = {"status": status, "reason": reason,
                         "supporting_parameters": present}
        return {"status": "success", "families": fams}
