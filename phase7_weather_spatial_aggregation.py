"""Phase 7: SOI boundaries + IMD aggregation + MoRTH join. No weather-accident stats, no website changes.
Run: python phase7_weather_spatial_aggregation.py"""
import netCDF4 as nc, numpy as np, pandas as pd, hashlib, os, json
import geopandas as gpd
from shapely.geometry import box
from datetime import date
from openpyxl import Workbook

RAWB = "phase7_raw/boundaries/SOI"
RAW = "phase6_raw/weather/IMD"
print("hash rar:", hashlib.sha256(open(os.path.join(RAWB, "SOI_ABDB_PANINDIA.rar"), "rb").read()).hexdigest()[:16])

g = gpd.read_file(os.path.join(RAWB, "extracted/State_District_Subdistrict_PAN INDIA/State Boundary/State Boundary.shp"))
g = g[~g.STATE.str.startswith("DISPUTED")].copy()
print("polygons:", len(g), "| valid:", int(g.is_valid.sum()), "| crs-projected:", g.crs.is_projected)
g4326 = g.to_crs(4326)
g["state_area_m2"] = g.geometry.area

# MoRTH mapping (UPPER source -> MoRTH); legacy 18-19 separate DNH/Diu have no polygon
MOTH = {"DADRA & NAGAR HAVELI & DAMAN & DIU": "Dadra & Nagar Haveli and Daman & Diu",
 "JAMMU AND KASHMIR": "Jammu & Kashmir", "LADAKH": "Ladakh", "ANDAMAN & NICOBAR": "Andaman & Nicobar Islands",
 "DELHI": "Delhi", "TAMIL NADU": "Tamil Nadu"}
morth_states = pd.read_csv("phase3_state_population.csv")[["State_UT"]].drop_duplicates()
covered = set(MOTH.get(s, s.title().replace(" And ", " & ")) for s in g.STATE)
have = set(morth_states.State_UT)
print("MoRTH entities without polygon:", sorted(have - covered - {"Dadra & Nagar Haveli", "Daman & Diu"}))
print("legacy-only (expected UNRESOLVED):", sorted(have & {"Dadra & Nagar Haveli", "Daman & Diu"}))

# ---- grid cell polygons ----
d0 = nc.Dataset(os.path.join(RAW, "RF25_2018.nc"))
rlon, rlat = d0.variables["LONGITUDE"][:], d0.variables["LATITUDE"][:]; d0.close()
rcells, rxy = [], []
for j, la in enumerate(rlat):
    for i, lo in enumerate(rlon):
        rcells.append(box(lo-0.125, la-0.125, lo+0.125, la+0.125)); rxy.append((j, i))
rcells = gpd.GeoDataFrame({"cell": range(len(rcells))}, geometry=rcells, crs=4326).to_crs(g.crs)
ov = gpd.overlay(rcells, g[["STATE", "geometry"]], how="intersection")
ov["iarea"] = ov.geometry.area
# state -> (cell flat idx over 129x135, weight)
rain_w = {}
for s, grp in ov.groupby("STATE"):
    tot = grp.iarea.sum()
    idx = (grp.cell.values // 135 * 135 + grp.cell.values % 135)  # flat
    rain_w[s] = (grp.cell.values, (grp.iarea / tot).values, tot)
print("rain states with cells:", len(rain_w))

# temp 1-deg grid: lon/lat standard IMD 67.5..97.5? use cell centers 8..37 x 68..98 approx -> derive from shape only
# IMD 1-deg: 31 lats (7.5..37.5), 31 lons (67.5..97.5)
tlat = np.arange(7.5, 38.0, 1.0); tlon = np.arange(67.5, 98.0, 1.0)
tcells = []
for j, la in enumerate(tlat):
    for i, lo in enumerate(tlon):
        tcells.append(box(lo-0.5, la-0.5, lo+0.5, la+0.5))
tcells = gpd.GeoDataFrame({"cell": range(len(tcells))}, geometry=tcells, crs=4326).to_crs(g.crs)
ovt = gpd.overlay(tcells, g[["STATE", "geometry"]], how="intersection")
ovt["iarea"] = ovt.geometry.area
temp_w = {}
for s, grp in ovt.groupby("STATE"):
    tot = grp.iarea.sum()
    temp_w[s] = (grp.cell.values, (grp.iarea / tot).values, tot)
print("temp states with cells:", len(temp_w))

# ---- daily state series ----
YEARS = list(range(2018, 2025))
daily = {}  # (state,year) -> dict
for y in YEARS:
    rf = nc.Dataset(os.path.join(RAW, "RF25_%d.nc" % y)).variables["RAINFALL"][:]
    rf = np.ma.filled(np.ma.masked_values(np.ma.array(rf, copy=False, subok=True), -999.0), np.nan).astype(float)
    nd = rf.shape[0]
    tx = np.fromfile(os.path.join(RAW, "TMAX1_%d.nc" % y), dtype="<f4").reshape(nd, 31, 31)
    tn = np.fromfile(os.path.join(RAW, "TMIN1_%d.nc" % y), dtype="<f4").reshape(nd, 31, 31)
    assert nd == (366 if y in (2020, 2024) else 365), (y, nd)
    for s in g.STATE:
        ci, w, tot = rain_w.get(s, (np.array([]), np.array([]), 0))
        if len(ci):
            flat = (ci // 135) * 135 + (ci % 135)
            jj, ii = flat // 135, flat % 135
            cell = rf[:, jj, ii]
            okm = ~np.isnan(cell)
            wsum = (okm * w).sum(1)
            use = wsum >= 0.5
            rd = np.full(nd, np.nan)
            rd[use] = (np.where(okm, cell, 0) * w).sum(1)[use] / wsum[use]
            rcov = wsum / w.sum() * 100  # per-day valid-weight fraction (avg later)
            rcov_mean = float(wsum.mean() / w.sum() * 100)
        else:
            rd = np.full(nd, np.nan); rcov_mean = 0.0
        ci2, w2, tot2 = temp_w.get(s, (np.array([]), np.array([]), 0))
        xd = np.full(nd, np.nan); nd2 = np.full(nd, np.nan); tcov = np.zeros(nd)
        if len(ci2):
            jj2, ii2 = ci2 // 31, ci2 % 31
            vx = tx[:, jj2, ii2]; vn = tn[:, jj2, ii2]
            mx = (vx != 99.9); mn = (vn != 99.9)
            ws = np.where(mx, w2, 0); wn = np.where(mn, w2, 0)
            sx = ws.sum(1); sn = wn.sum(1)
            v = sx > 0.5; u = sn > 0.5
            xd[v] = (np.where(mx, vx, 0) * w2).sum(1)[v] / sx[v]
            nd2[u] = (np.where(mn, vn, 0) * w2).sum(1)[u] / sn[u]
            sa = g.set_index("STATE").state_area_m2[s]
            tcov = sx * tot2 / sa * 100
        daily[(s, y)] = {"rain": rd, "tmax": xd, "tmin": nd2, "tmax_cov": tcov, "rain_cov": rcov_mean,
                         "ndays": nd, "rain_cells": len(ci), "temp_cells": len(ci2)}
    print(y, "done")

# ---- monthly + annual ----
mon_rows, ann_rows = [], []
import calendar
for (s, y), d in daily.items():
    mo = "Dadra & Nagar Haveli and Daman & Diu" if False else MOTH.get(s, s.title().replace(" And ", " & "))
    for m in range(1, 13):
        n = calendar.monthrange(y, m)[1]
        sl = slice(sum(calendar.monthrange(y, k)[1] for k in range(1, m)), sum(calendar.monthrange(y, k)[1] for k in range(1, m+1)))
        r = d["rain"][sl]; x = d["tmax"][sl]; n2 = d["tmin"][sl]
        rv = r[~np.isnan(r)]; xv = x[~np.isnan(x)]; nv = n2[~np.isnan(n2)]
        mon_rows.append({"State_UT": mo, "Boundary_STATE": s, "Year": y, "Month": m,
            "Monthly_Rainfall_mm": round(float(rv.sum()), 1) if len(rv) == n else np.nan,
            "Mean_Tmax_C": round(float(xv.mean()), 2) if len(xv) >= 25 else np.nan,
            "Mean_Tmin_C": round(float(nv.mean()), 2) if len(nv) >= 25 else np.nan,
            "Valid_Days": n, "Rain_Days_OK": int(len(rv) == n),
            "Coverage_Status": "VERIFIED" if (len(rv) == n and len(xv) >= 25) else ("PARTIAL_COVERAGE" if len(rv) == n else "INSUFFICIENT_COVERAGE"),
            "Aggregation_Method": "area-weighted state mean (LCC m2 weights)", "Source": "IMD RF25/TMAX1/TMIN1"})
    r = d["rain"]; x = d["tmax"]; n2 = d["tmin"]
    rv_ok = int(np.isnan(r).sum() == 0)
    xv = x[~np.isnan(x)]; nv = n2[~np.isnan(n2)]
    need = 330
    ok = rv_ok and len(xv) >= need and len(nv) >= need
    ann_rows.append({"State_UT": mo, "Boundary_STATE": s, "Year": y,
        "Annual_Rainfall_mm": round(float(r.sum()), 1) if rv_ok else np.nan,
        "Annual_Mean_Tmax_C": round(float(xv.mean()), 2) if len(xv) >= need else np.nan,
        "Annual_Mean_Tmin_C": round(float(nv.mean()), 2) if len(nv) >= need else np.nan,
        "Valid_Rainfall_Days": int((~np.isnan(r)).sum()), "Valid_Tmax_Days": int(len(xv)), "Valid_Tmin_Days": int(len(nv)),
        "Rainfall_Coverage_pct": round(float(d["rain_cov"]), 1), "Tmax_Coverage_pct": round(float((~np.isnan(x)).mean()*100), 1),
        "Rain_Cells": d["rain_cells"], "Temp_Cells": d["temp_cells"],
        "Boundary_Vintage": "SOI ABDB (post-2019 incl. Ladakh + merged DNH-DD)",
        "Aggregation_Method": "area-weighted state mean (LCC m2 weights)",
        "Quality_Status": "VERIFIED" if ok else ("NO_VALID_GRID_CELL" if d["temp_cells"] == 0 else "PARTIAL_COVERAGE"),
        "Source": "IMD RF25/TMAX1/TMIN1"})
MON = pd.DataFrame(mon_rows); ANN = pd.DataFrame(ann_rows)
print("annual VERIFIED:", int((ANN.Quality_Status == "VERIFIED").sum()), "/", len(ANN))
print(ANN[ANN.Quality_Status != "VERIFIED"][["State_UT", "Year", "Quality_Status", "Temp_Cells"]].to_string(index=False))

# ---- MoRTH join ----
morth = pd.read_csv("phase3_state_population.csv")[["State_UT", "Year", "Accidents", "Fatalities"]]
J = morth.merge(ANN, on=["State_UT", "Year"], how="left", indicator=True)
print("MoRTH rows:", len(morth), "| matched:", int((J._merge == "both").sum()), "| unmatched:", int((J._merge == "left_only").sum()))
print("unmatched:", J[J._merge == "left_only"][["State_UT", "Year"]].drop_duplicates().to_string(index=False))
assert not J.duplicated(["State_UT", "Year"]).any()

ANN.to_csv("state_weather_annual.csv", index=False)
MON.to_csv("state_weather_monthly.csv", index=False)
J.to_csv("weather_morth_join.csv", index=False)
json.dump({"annual_verified": int((ANN.Quality_Status == "VERIFIED").sum()), "annual_total": len(ANN),
    "morth_matched": int((J._merge == "both").sum()), "morth_unmatched": int((J._merge == "left_only").sum())},
    open("phase7_results.json", "w"), indent=1)
print("saved.")
