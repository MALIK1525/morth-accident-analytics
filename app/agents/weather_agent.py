"""
Weather Data Agent for MoRTH Road Accident Research Platform.

Uses the validated Phase 7 weather-MoRTH join (weather_morth_join.csv):
IMD Pune CMPG gridded rainfall (0.25°) + Tmax/Tmin (1°), daily 2018-2024,
spatially aggregated to state level via SOI ABDB boundaries.

236 usable state-years (JOINED + valid rainfall). 18 excluded rows
(islands with no valid grid cells + legacy DNH/Diu splits) are preserved
in the source file but never enter analytical outputs.

Humidity / visibility / fog / wind: NOT AVAILABLE FROM VERIFIED DATA.
All associations reported are observational, never causal.
"""
import os
import math
import pandas as pd
import numpy as np

# Validated Phase 8 pooled associations (observational). Recomputed live in
# get_correlation(); constants below are NOT used as results, only as a
# cross-check reference documented in PHASE8_WEATHER_ASSOCIATION_REPORT.md.

JOIN_FILENAME = "weather_morth_join.csv"

SEARCH_DIRS = [".", "data"]


def _find_join_file(data_dir="data"):
    candidates = [os.path.join(data_dir, JOIN_FILENAME),
                  JOIN_FILENAME,
                  os.path.join(".", JOIN_FILENAME)]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None


def _safe(v):
    """Convert NaN/Inf to None for JSON-safe output (null, never 0)."""
    try:
        f = float(v)
        if math.isnan(f) or math.isinf(f):
            return None
        return f
    except (TypeError, ValueError):
        return v


class WeatherAgent:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.weather_file = _find_join_file(data_dir)
        self.is_loaded = False
        self.weather_df = None       # usable analytical rows only (236)
        self.full_df = None          # all rows incl. exclusions (254)
        self.merged_df = None

    # ---------- loading ----------

    def load_weather_dataset(self, primary_df=None):
        """Loads the validated Phase 7 weather-MoRTH join table."""
        path = _find_join_file(self.data_dir)
        if path is None:
            return {
                "success": False,
                "error": ("Historical weather analytics unavailable in this deployment "
                          "because the verified IMD source file (weather_morth_join.csv) "
                          "is not included. Required enabler: Phase 7 STATE_WEATHER_ANNUAL "
                          "aggregation joined to the MoRTH panel.")
            }
        try:
            df = pd.read_csv(path)
        except Exception as e:
            return {"success": False, "error": str(e)}

        required = ["State_UT", "Year", "Annual_Rainfall_mm",
                    "Annual_Mean_Tmax_C", "Annual_Mean_Tmin_C"]
        missing = [c for c in required if c not in df.columns]
        if missing:
            return {"success": False,
                    "error": f"Weather join table missing columns: {missing}"}

        self.weather_file = path
        self.full_df = df
        usable = df[(df.get("Join_Status", "JOINED") == "JOINED")
                    & df["Annual_Rainfall_mm"].notna()].copy()
        self.weather_df = usable
        self.is_loaded = True
        if primary_df is not None:
            self.merged_df = usable  # join table already carries Accidents/Fatalities
        return {
            "success": True,
            "records_loaded": int(len(usable)),
            "rows_excluded": int(len(df) - len(usable)),
            "states_covered": int(usable["State_UT"].nunique()),
            "years_covered": (f"{int(usable['Year'].min())}–{int(usable['Year'].max())}"
                              if len(usable) else "none"),
            "variables_registered": ["Annual_Rainfall_mm", "Annual_Mean_Tmax_C",
                                     "Annual_Mean_Tmin_C"],
            "variables_unavailable": ["humidity", "visibility", "fog", "wind"],
            "message": "Validated IMD weather-MoRTH join loaded (236 usable state-years)."
        }

    def _ensure(self, primary_df=None):
        if not self.is_loaded:
            res = self.load_weather_dataset(primary_df)
            if not res.get("success"):
                return res
        return None

    # ---------- status / metadata ----------

    def check_status(self):
        """Truthful deployment status derived from actual files."""
        path = _find_join_file(self.data_dir)
        if path is None:
            return {
                "loaded": False,
                "file_available": False,
                "status": "UNAVAILABLE",
                "source": "India Meteorological Department (IMD), Pune CMPG gridded archives",
                "message": ("Historical weather analytics unavailable in this deployment "
                            "because the verified IMD source file (weather_morth_join.csv) "
                            "is not included."),
                "required_enabler": ("Phase 7 STATE_WEATHER_ANNUAL_2018_2024 + validated "
                                     "(State_UT, Year) join to the MoRTH panel.")
            }
        err = self._ensure()
        if err:
            return {"loaded": False, "file_available": True, "status": "UNAVAILABLE",
                    "message": err.get("error")}
        n = len(self.weather_df)
        return {
            "loaded": True,
            "file_available": True,
            "status": "AVAILABLE" if n >= 200 else "PARTIALLY_AVAILABLE",
            "source": "India Meteorological Department (IMD), Pune CMPG gridded data",
            "variables": ["Annual_Rainfall_mm (mm)", "Annual_Mean_Tmax_C (°C)",
                          "Annual_Mean_Tmin_C (°C)"],
            "variables_unavailable": ["humidity", "visibility", "fog", "wind"],
            "spatial_resolution": "rainfall 0.25° grid; temperature 1° grid",
            "temporal_coverage": "daily 2018–2024, aggregated to state-year",
            "aggregation_method": ("validated state-boundary spatial aggregation "
                                   "(SOI ABDB); equal-cell weighting, area sensitivity ≤0.6%"),
            "boundary_version": "SOI ABDB (post-2019: merged DNH-DD; J&K/Ladakh separate)",
            "usable_state_years": int(n),
            "excluded_rows": int(len(self.full_df) - n),
            "exclusion_reasons": ("Lakshadweep 7 (no valid grid cells); "
                                  "Andaman & Nicobar 7 (all cells masked); "
                                  "legacy DNH/Diu 2018–19 x4 (split not reconstructible)"),
            "message": f"Validated IMD weather join active: {n} usable state-years."
        }

    def get_metadata(self):
        st = self.check_status()
        st["provenance_note"] = ("Source: India Meteorological Department (IMD), gridded "
                                 "rainfall/temperature data; spatially aggregated to state "
                                 "level using the project's validated boundary workflow.")
        return st

    # ---------- data endpoints ----------

    def _apply_filters(self, df, filters=None):
        filters = filters or {}
        if filters.get("state") and filters["state"] != "ALL":
            df = df[df["State_UT"] == filters["state"]]
        if filters.get("year") and filters["year"] != "ALL":
            try:
                df = df[df["Year"] == int(filters["year"])]
            except (ValueError, TypeError):
                pass
        if filters.get("zone") and filters["zone"] != "ALL":
            if "Zone" in df.columns:
                df = df[df["Zone"] == filters["zone"]]
            else:
                # Join table has no Zone column: derive from project zone mapping.
                try:
                    from app.data_pipeline.loader import get_zone_for_state
                    df = df[df["State_UT"].apply(
                        lambda s: get_zone_for_state(s) == filters["zone"])]
                except ImportError:
                    pass
        return df

    def get_annual(self, filters=None):
        """State-year weather rows (W1-W3, W10-W12 source). Null where unavailable."""
        err = self._ensure()
        if err:
            return {"status": "UNAVAILABLE", "message": err.get("error"), "rows": []}
        df = self._apply_filters(self.full_df, filters)
        rows = []
        for _, r in df.iterrows():
            rows.append({
                "state": str(r["State_UT"]),
                "year": int(r["Year"]),
                "rainfall_mm": _safe(r.get("Annual_Rainfall_mm")),
                "tmax_c": _safe(r.get("Annual_Mean_Tmax_C")),
                "tmin_c": _safe(r.get("Annual_Mean_Tmin_C")),
                "accidents": (int(r["Accidents"]) if "Accidents" in df.columns
                              and pd.notna(r.get("Accidents")) else None),
                "fatalities": (int(r["Fatalities"]) if "Fatalities" in df.columns
                               and pd.notna(r.get("Fatalities")) else None),
                "available": bool(pd.notna(r.get("Annual_Rainfall_mm"))),
                "quality": str(r.get("Quality_Status", "UNKNOWN")),
            })
        return {"status": "AVAILABLE", "count": len(rows), "rows": rows}

    def get_state(self, state, year=None):
        f = {"state": state, "year": str(year) if year else "ALL", "zone": "ALL"}
        return self.get_annual(f)

    def get_correlation(self):
        """Pooled observational associations, computed live from usable rows."""
        err = self._ensure()
        if err:
            return {"status": "UNAVAILABLE", "message": err.get("error")}
        try:
            from scipy import stats as sstats
        except ImportError:
            return {"status": "UNAVAILABLE",
                    "message": "scipy not available for correlation computation."}
        df = self.weather_df
        pairs = [("Annual_Rainfall_mm", "Accidents"),
                 ("Annual_Rainfall_mm", "Fatalities"),
                 ("Annual_Mean_Tmax_C", "Accidents"),
                 ("Annual_Mean_Tmax_C", "Fatalities"),
                 ("Annual_Mean_Tmin_C", "Accidents"),
                 ("Annual_Mean_Tmin_C", "Fatalities")]
        out = []
        for x, y in pairs:
            sub = df[[x, y]].dropna()
            n = len(sub)
            if n < 4:
                out.append({"x": x, "y": y, "n": n, "status": "INSUFFICIENT_N"})
                continue
            r, p = sstats.pearsonr(sub[x], sub[y])
            rho, pp = sstats.spearmanr(sub[x], sub[y])
            out.append({"x": x, "y": y, "n": n,
                        "pearson_r": _safe(r), "pearson_p": _safe(p),
                        "spearman_rho": _safe(rho), "spearman_p": _safe(pp),
                        "status": "OK"})
        return {"status": "AVAILABLE",
                "design": "pooled state-year observational association (N=236); "
                          "between-state scale differences apply; not causal evidence",
                "associations": out}

    def get_weather_analytics(self, primary_df=None):
        """Legacy endpoint: scatter data for rainfall vs accidents/fatalities."""
        err = self._ensure(primary_df)
        if err:
            return {"status": "UNAVAILABLE", "message": err.get("error")}
        df = self.weather_df
        scatter_acc, scatter_fat = [], []
        for _, r in df.iterrows():
            base = {"state": str(r["State_UT"]), "year": int(r["Year"]),
                    "rainfall_mm": _safe(r["Annual_Rainfall_mm"]),
                    "tmax_c": _safe(r["Annual_Mean_Tmax_C"]),
                    "tmin_c": _safe(r["Annual_Mean_Tmin_C"])}
            if pd.notna(r.get("Accidents")):
                scatter_acc.append({**base, "accidents": int(r["Accidents"])})
            if pd.notna(r.get("Fatalities")):
                scatter_fat.append({**base, "fatalities": int(r["Fatalities"])})
        return {
            "status": "AVAILABLE",
            "rainfall_vs_accidents": scatter_acc,
            "rainfall_vs_fatalities": scatter_fat,
            "methodology_note": ("Observed association only — not causal evidence. "
                                 "Pooled state-year design; between-state scale applies."),
            "source_note": ("Source: India Meteorological Department (IMD), gridded "
                            "rainfall/temperature data; spatially aggregated to state level "
                            "using the project's validated boundary workflow.")
        }
