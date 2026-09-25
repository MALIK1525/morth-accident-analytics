"""
Data Ingestion, Validation and Preprocessing Module for MoRTH Road Accident Dataset.
Follows non-destructive data integrity rules: original data is never modified.
"""
import os
import pandas as pd
import numpy as np

# Official benchmark totals from MoRTH & Parliamentary records
OFFICIAL_INDIA_BENCHMARKS = {
    2018: {"Accidents": 470403, "Fatalities": 157593, "Injured": 464715},
    2019: {"Accidents": 456959, "Fatalities": 158984, "Injured": 449360},
    2020: {"Accidents": 372181, "Fatalities": 138383, "Injured": 346747},
    2021: {"Accidents": 412432, "Fatalities": 153972, "Injured": 384448},
    2022: {"Accidents": 461312, "Fatalities": 168491, "Injured": 443366},
    2023: {"Accidents": 480583, "Fatalities": 172890, "Injured": 462825},
    2024: {"Accidents": 487707, "Fatalities": 177175, "Injured": 471441},
}

# Project-defined analytical zones (not official administrative zones)
ZONE_MAPPING = {
    "North": [
        "Jammu & Kashmir", "Ladakh", "Himachal Pradesh", "Punjab", "Chandigarh",
        "Haryana", "Delhi", "Uttarakhand", "Uttar Pradesh", "Rajasthan"
    ],
    "South": [
        "Andhra Pradesh", "Telangana", "Karnataka", "Kerala", "Tamil Nadu",
        "Puducherry", "Lakshadweep", "Andaman & Nicobar Islands"
    ],
    "East": [
        "Bihar", "Jharkhand", "West Bengal", "Odisha"
    ],
    "West": [
        "Gujarat", "Maharashtra", "Goa", "Dadra & Nagar Haveli", "Daman & Diu",
        "Dadra & Nagar Haveli and Daman & Diu"
    ],
    "Central": [
        "Madhya Pradesh", "Chhattisgarh"
    ],
    "Northeast": [
        "Assam", "Arunachal Pradesh", "Manipur", "Meghalaya", "Mizoram",
        "Nagaland", "Sikkim", "Tripura"
    ]
}

STATE_TO_ZONE = {}
for zone, states in ZONE_MAPPING.items():
    for state in states:
        STATE_TO_ZONE[state.strip().lower()] = zone

def get_zone_for_state(state_name):
    if not state_name or pd.isna(state_name):
        return "Unknown"
    norm = str(state_name).strip().lower()
    return STATE_TO_ZONE.get(norm, "Unknown")

class DatasetLoader:
    def __init__(self, data_dir="data", benchmark_path=None):
        self.data_dir = data_dir
        self.raw_data = None
        self.clean_data = None
        self.metadata = {}
        self.validation_report = []
        self.source_vintage_data = []
        self.supporting_inventory = []
        self.data_dictionary = []
        self.active_filename = ""
        self.is_benchmark = False

        # Automatically load benchmark
        target_bench = benchmark_path if benchmark_path else os.path.join(self.data_dir, "MoRTH_Primary_Dataset_3.xlsx")
        if os.path.exists(target_bench):
            self.load_benchmark(target_bench)

    def load_benchmark(self, filepath=None):
        """Loads the verified MoRTH primary dataset (MoRTH_Primary_Dataset_3.xlsx)"""
        if filepath is None:
            filepath = os.path.join(self.data_dir, "MoRTH_Primary_Dataset_3.xlsx")
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"MoRTH primary dataset not found at {filepath}")
        
        self.active_filename = os.path.basename(filepath)
        self.is_benchmark = True
        
        xl = pd.ExcelFile(filepath)
        
        # Read CLEAN sheet (skipping 2 header description rows)
        raw_clean = xl.parse("CLEAN", skiprows=2)
        # Select relevant canonical columns
        cols = ['State_UT', 'Year', 'Accidents', 'Fatalities', 'Injured',
                'Fatalities_per_Accident', 'Fatalities_per_100_Accidents',
                'India_Accident_Share_pct', 'India_Fatality_Share_pct',
                'Data_Completeness_Flag', 'Admin_Unit_Note']
        available_cols = [c for c in cols if c in raw_clean.columns]
        self.raw_data = raw_clean[available_cols].copy()
        
        # Process into clean typed copy without mutating raw_data
        df = self.raw_data.copy()
        df['State_UT'] = df['State_UT'].astype(str).str.strip()
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce').astype(int)
        
        # Safe numeric parsing: NV and blanks become np.nan in numeric computation fields
        df['Accidents_num'] = pd.to_numeric(df['Accidents'].replace('NV', np.nan), errors='coerce')
        df['Fatalities_num'] = pd.to_numeric(df['Fatalities'].replace('NV', np.nan), errors='coerce')
        df['Injured_num'] = pd.to_numeric(df['Injured'].replace('NV', np.nan), errors='coerce')
        
        # Ensure Accidents, Fatalities are numeric for analytics
        df['Accidents'] = df['Accidents_num'].fillna(0).astype(int)
        df['Fatalities'] = df['Fatalities_num'].fillna(0).astype(int)

        # Re-derive / verify derived metrics: Fatalities per 100 Accidents
        df['Fatalities_per_100_Accidents_calc'] = np.where(
            df['Accidents_num'] > 0,
            (df['Fatalities_num'] / df['Accidents_num']) * 100.0,
            np.nan
        )
        
        # Assign Analytical Zone
        df['Zone'] = df['State_UT'].apply(get_zone_for_state)
        
        self.clean_data = df
        
        # Read supporting sheets if present
        if "DATA_DICTIONARY" in xl.sheet_names:
            dd_raw = xl.parse("DATA_DICTIONARY", skiprows=2).dropna(how='all')
            self.data_dictionary = dd_raw.to_dict(orient="records")
            
        if "VALIDATION" in xl.sheet_names:
            val_raw = xl.parse("VALIDATION", skiprows=2).dropna(subset=['Check', 'Description'])
            self.validation_report = val_raw.to_dict(orient="records")
            
        if "SOURCE_VINTAGE_COMPARISON" in xl.sheet_names:
            svc_raw = xl.parse("SOURCE_VINTAGE_COMPARISON", skiprows=2).dropna(subset=['Year', 'Variable'])
            self.source_vintage_data = svc_raw.to_dict(orient="records")
            
        if "SUPPORTING_INVENTORY" in xl.sheet_names:
            sup_raw = xl.parse("SUPPORTING_INVENTORY", skiprows=2).dropna(subset=['Dataset', 'Year'])
            self.supporting_inventory = sup_raw.to_dict(orient="records")
            
        self.audit_summary = self.run_quality_audit()
        return self.audit_summary

    def load_user_upload(self, filepath, original_filename=None):
        """Safely loads a user-uploaded CSV or Excel file without destructive overwriting."""
        self.active_filename = original_filename or os.path.basename(filepath)
        self.is_benchmark = False
        
        ext = os.path.splitext(filepath)[1].lower()
        if ext in ['.xlsx', '.xls']:
            xl = pd.ExcelFile(filepath)
            sheet_to_use = xl.sheet_names[0]
            for s in xl.sheet_names:
                if s.upper() in ['CLEAN', 'DATA', 'PRIMARY', 'ACCIDENTS']:
                    sheet_to_use = s
                    break
            raw_df = xl.parse(sheet_to_use)
        elif ext == '.csv':
            raw_df = pd.read_csv(filepath)
        else:
            raise ValueError(f"Unsupported file format: {ext}. Only CSV and Excel supported.")
            
        self.raw_data = raw_df.copy()
        
        mapping, mapped_df = self._auto_map_columns(raw_df)
        self.column_mapping = mapping
        
        if 'State_UT' in mapped_df.columns:
            mapped_df['Zone'] = mapped_df['State_UT'].apply(get_zone_for_state)
            
        if 'Accidents_num' in mapped_df.columns and 'Fatalities_num' in mapped_df.columns:
            mapped_df['Fatalities_per_100_Accidents_calc'] = np.where(
                mapped_df['Accidents_num'] > 0,
                (mapped_df['Fatalities_num'] / mapped_df['Accidents_num']) * 100.0,
                np.nan
            )
            
        self.clean_data = mapped_df
        self.audit_summary = self.run_quality_audit()
        return self.audit_summary

    def _auto_map_columns(self, df):
        """Identifies columns with fuzzy matching without dangerous guessing."""
        col_patterns = {
            'State_UT': ['state_ut', 'state/ut', 'state', 'states/uts', 'state_name', 'state / ut', 'ut'],
            'Year': ['year', 'accident_year', 'reporting_year', 'yr'],
            'Accidents': ['accidents', 'total_accidents', 'road_accidents', 'total accidents', 'road accidents', 'incidents', 'total incidents'],
            'Fatalities': ['fatalities', 'deaths', 'killed', 'total_killed', 'persons_killed', 'dead', 'fatalities (killed)'],
            'Injured': ['injured', 'injuries', 'persons_injured', 'total_injured', 'non_fatal_injuries', 'casualties']
        }
        
        mapping = {}
        mapped_df = pd.DataFrame()
        lower_cols = {str(c).strip().lower(): c for c in df.columns}
        
        for std_col, candidates in col_patterns.items():
            matched = None
            confidence = "LOW"
            for cand in candidates:
                if cand in lower_cols:
                    matched = lower_cols[cand]
                    confidence = "HIGH" if cand == std_col.lower() else "MEDIUM"
                    break
            
            mapping[std_col] = {
                "detected": matched,
                "confidence": confidence,
                "action": "Mapped" if matched else "Not Found"
            }
            
            if matched:
                if std_col in ['Accidents', 'Fatalities', 'Injured']:
                    mapped_df[std_col] = df[matched]
                    mapped_df[f"{std_col}_num"] = pd.to_numeric(
                        df[matched].replace(['NV', 'NA', 'None', '-', ''], np.nan),
                        errors='coerce'
                    )
                elif std_col == 'Year':
                    mapped_df['Year'] = pd.to_numeric(df[matched], errors='coerce').fillna(0).astype(int)
                elif std_col == 'State_UT':
                    mapped_df['State_UT'] = df[matched].astype(str).str.strip()
            else:
                if std_col in ['Accidents', 'Fatalities', 'Injured']:
                    mapped_df[std_col] = "NV"
                    mapped_df[f"{std_col}_num"] = np.nan
        
        for c in df.columns:
            if c not in [m["detected"] for m in mapping.values() if m["detected"]]:
                mapped_df[c] = df[c]
                
        return mapping, mapped_df

    def run_quality_audit(self):
        """Runs a rigorous non-destructive data quality and reconciliation audit."""
        if self.clean_data is None:
            return {}
            
        df = self.clean_data
        total_rows = int(len(df))
        total_cols = int(len(df.columns))
        
        if 'State_UT' in df.columns and 'Year' in df.columns:
            sy_dups = int(df.duplicated(subset=['State_UT', 'Year']).sum())
            sy_unique_status = "PASS (0 duplicates)" if sy_dups == 0 else f"FAIL ({sy_dups} duplicate State-Years)"
            unique_states = int(df['State_UT'].nunique())
            unique_years = [int(y) for y in sorted(df['Year'].unique()) if y > 0]
        else:
            sy_dups = 0
            sy_unique_status = "NOT EVALUATED (Missing State or Year)"
            unique_states = 0
            unique_years = []

        acc_col = 'Accidents_num' if 'Accidents_num' in df.columns else 'Accidents'
        fat_col = 'Fatalities_num' if 'Fatalities_num' in df.columns else 'Fatalities'
        inj_col = 'Injured_num' if 'Injured_num' in df.columns else 'Injured'

        missing_acc = int(df[acc_col].isnull().sum()) if acc_col in df.columns else total_rows
        missing_fat = int(df[fat_col].isnull().sum()) if fat_col in df.columns else total_rows
        missing_inj = int(df[inj_col].isnull().sum()) if inj_col in df.columns else total_rows

        negative_acc = int((df[acc_col] < 0).sum()) if acc_col in df.columns else 0
        negative_fat = int((df[fat_col] < 0).sum()) if fat_col in df.columns else 0
        negative_inj = int((df[inj_col] < 0).sum()) if inj_col in df.columns else 0

        zero_acc = int((df[acc_col] == 0).sum()) if acc_col in df.columns else 0
        zero_fat = int((df[fat_col] == 0).sum()) if fat_col in df.columns else 0

        reconciliation = []
        for yr in unique_years:
            if yr in OFFICIAL_INDIA_BENCHMARKS:
                bench = OFFICIAL_INDIA_BENCHMARKS[yr]
                sub = df[df['Year'] == yr]
                
                c_acc = int(sub[acc_col].sum()) if acc_col in df.columns and not sub[acc_col].dropna().empty else None
                c_fat = int(sub[fat_col].sum()) if fat_col in df.columns and not sub[fat_col].dropna().empty else None
                
                if yr <= 2022:
                    c_inj = int(sub[inj_col].sum()) if inj_col in df.columns and not sub[inj_col].dropna().empty else None
                else:
                    c_inj = None
                
                acc_diff = int(c_acc - bench['Accidents']) if c_acc is not None else None
                fat_diff = int(c_fat - bench['Fatalities']) if c_fat is not None else None
                inj_diff = int(c_inj - bench['Injured']) if (c_inj is not None and yr <= 2022) else None
                
                reconciliation.append({
                    "year": int(yr),
                    "computed_accidents": c_acc,
                    "published_accidents": int(bench['Accidents']),
                    "accidents_diff": acc_diff,
                    "accidents_status": "MATCH" if acc_diff == 0 else ("PARTIAL" if acc_diff is None else "MISMATCH"),
                    "computed_fatalities": c_fat,
                    "published_fatalities": int(bench['Fatalities']),
                    "fatalities_diff": fat_diff,
                    "fatalities_status": "MATCH" if fat_diff == 0 else ("PARTIAL" if fat_diff is None else "MISMATCH"),
                    "computed_injured": c_inj,
                    "published_injured": int(bench['Injured']),
                    "injured_diff": inj_diff,
                    "injured_status": "MATCH" if inj_diff == 0 else ("NV (India-total only)" if yr > 2022 else "MISMATCH")
                })

        return {
            "filename": str(self.active_filename),
            "is_benchmark": bool(self.is_benchmark),
            "total_rows": total_rows,
            "total_cols": total_cols,
            "unique_states": unique_states,
            "year_coverage": f"{min(unique_years)}–{max(unique_years)}" if unique_years else "None",
            "unique_years": unique_years,
            "sy_duplicates": sy_dups,
            "sy_unique_status": sy_unique_status,
            "missing_accidents": missing_acc,
            "missing_fatalities": missing_fat,
            "missing_injured": missing_inj,
            "negative_values": negative_acc + negative_fat + negative_inj,
            "zero_accidents": zero_acc,
            "zero_fatalities": zero_fat,
            "reconciliation": reconciliation,
            "boundary_note": "Administrative boundaries changed in 2019/2020: Dadra & Nagar Haveli and Daman & Diu merged (37 units in 2018-2019 -> 36 units in 2020-2024); Ladakh became separate UT.",
            "data_quality_badge": "DIRECTLY VERIFIED" if self.is_benchmark else "USER UPLOADED",
            "validation_checks_passed": True if (negative_acc + negative_fat == 0 and sy_dups == 0) else False
        }

    def get_clean_df(self):
        if self.clean_data is None:
            self.load_benchmark()
        return self.clean_data

    def get_validation_report(self):
        return self.validation_report

    def get_source_vintage(self):
        return self.source_vintage_data

    def get_audit_summary(self):
        return self.audit_summary

    def load_user_file(self, filepath, original_filename=None):
        return self.load_user_upload(filepath, original_filename)

    def reset_to_benchmark(self):
        return self.load_benchmark()
