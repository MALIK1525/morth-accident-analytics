"""
Data Discovery Agent for MoRTH Indian Road Accident Analytics Platform.
Dynamically inspects all supplied workbooks, sheets, columns, and data structures.
Builds the dynamic Variable Registry and Data Granularity Catalog.
"""
import os
import glob
import pandas as pd
import numpy as np

class DataDiscoveryAgent:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.workbooks_indexed = {}
        self.variable_registry = []
        self.granularity_catalog = {}
        self.available_parameters = set()
        self.unavailable_parameters = {}

    def discover_all(self):
        """Scans all workbooks in data directory and registers every parameter dynamically."""
        xlsx_files = sorted(glob.glob(os.path.join(self.data_dir, "*.xlsx")))
        csv_files = sorted(glob.glob(os.path.join(self.data_dir, "*.csv")))
        
        self.workbooks_indexed = {}
        self.variable_registry = []
        
        for file_path in xlsx_files:
            self._inspect_workbook(file_path)
            
        for file_path in csv_files:
            self._inspect_csv(file_path)
            
        self._build_granularity_and_availability()
        return {
            "workbooks_count": len(self.workbooks_indexed),
            "registered_variables_count": len(self.variable_registry),
            "available_parameters": sorted(list(self.available_parameters)),
            "unavailable_parameters": self.unavailable_parameters,
            "variable_registry": self.variable_registry
        }

    def _inspect_workbook(self, file_path):
        filename = os.path.basename(file_path)
        try:
            xl = pd.ExcelFile(file_path)
            sheets_meta = {}
            
            for sheet_name in xl.sheet_names:
                # Skip pure notes or readmes for data registry, but log them
                if sheet_name.upper() in ['README']:
                    continue
                    
                df = xl.parse(sheet_name)
                # Detect header row if sheet has metadata comments (e.g., skip first 2 rows)
                if df.shape[0] > 2 and 'CLEAN' in sheet_name.upper():
                    # Check if row 2 has actual headers
                    sub_df = xl.parse(sheet_name, skiprows=2)
                    if 'State_UT' in sub_df.columns:
                        df = sub_df
                elif df.shape[0] > 3 and sheet_name.startswith('G'):
                    # OriginPro tables usually have description in row 0-1, headers in row 2
                    sub_df = xl.parse(sheet_name, skiprows=2)
                    if len(sub_df.columns) > 1 and not str(sub_df.columns[0]).startswith('Unnamed'):
                        df = sub_df

                row_count, col_count = df.shape
                col_names = [str(c).strip() for c in df.columns if not str(c).startswith('Unnamed:')]
                
                # Determine sheet granularity
                granularity = self._infer_granularity(df, col_names)
                
                sheets_meta[sheet_name] = {
                    "row_count": row_count,
                    "col_count": col_count,
                    "columns": col_names,
                    "granularity": granularity
                }
                
                # Register meaningful variables
                self._register_sheet_variables(filename, sheet_name, df, col_names, granularity)
                
            self.workbooks_indexed[filename] = {
                "filepath": file_path,
                "sheets": sheets_meta
            }
        except Exception as e:
            print(f"Error inspecting {filename}: {e}")

    def _inspect_csv(self, file_path):
        filename = os.path.basename(file_path)
        try:
            df = pd.read_csv(file_path)
            row_count, col_count = df.shape
            col_names = [str(c).strip() for c in df.columns]
            granularity = self._infer_granularity(df, col_names)
            
            self.workbooks_indexed[filename] = {
                "filepath": file_path,
                "sheets": {
                    "CSV": {
                        "row_count": row_count,
                        "col_count": col_count,
                        "columns": col_names,
                        "granularity": granularity
                    }
                }
            }
            self._register_sheet_variables(filename, "CSV", df, col_names, granularity)
        except Exception as e:
            print(f"Error inspecting CSV {filename}: {e}")

    def _infer_granularity(self, df, col_names):
        lower_cols = [c.lower() for c in col_names]
        has_state = any(k in lower_cols for k in ['state', 'state_ut', 'states/uts', 'state/ut'])
        has_year = any(k in lower_cols for k in ['year', 'yr'])
        has_zone = any('zone' in k for k in lower_cols)
        has_month = any('month' in k for k in lower_cols)
        has_weather = any('weather' in k or 'rain' in k for k in lower_cols)
        has_road = any('road' in k or 'highway' in k for k in lower_cols)
        has_vehicle = any('vehicle' in k or 'mode' in k for k in lower_cols)

        if has_state and has_year:
            if has_weather: return "State-Year-Weather"
            if has_road: return "State-Year-Road"
            if has_vehicle: return "State-Year-Vehicle"
            return "State-Year"
        elif has_zone and has_year:
            return "Zone-Year"
        elif has_year and not has_state:
            if has_vehicle: return "India-Year-Vehicle"
            if has_road: return "India-Year-RoadCategory"
            return "India-Year"
        elif has_state and not has_year:
            return "State-Snapshot"
        else:
            return "National-Aggregate"

    def _register_sheet_variables(self, filename, sheet_name, df, col_names, granularity):
        for col in col_names:
            if str(col).startswith('Unnamed:') or str(col).lower() in ['index', 's.no', 'sl no']:
                continue
                
            clean_name = str(col).strip()
            self.available_parameters.add(clean_name)
            
            # Determine data type & coverage
            series = df[col] if col in df.columns else None
            unique_count = int(series.nunique()) if series is not None else 0
            
            # Year coverage if Year column exists in sheet
            year_col = next((c for c in df.columns if str(c).lower() in ['year', 'yr']), None)
            if year_col:
                years = [int(y) for y in pd.to_numeric(df[year_col], errors='coerce').dropna().unique() if y > 2000]
                coverage_str = f"{min(years)}–{max(years)}" if years else "Multi-Year"
            else:
                coverage_str = "Snapshot / Aggregate"
                
            # Verification status
            status = "DIRECTLY VERIFIED" if "Primary_Dataset" in filename or "OriginPro" in filename else "SUPPORTING"
            
            # Visualizations compatible with this variable
            vis_types = self._determine_visualizations(clean_name, series, granularity)
            
            # Check if variable already registered from higher priority workbook
            existing = next((v for v in self.variable_registry if v["variable"] == clean_name and v["source"] == filename), None)
            if not existing:
                self.variable_registry.append({
                    "variable": clean_name,
                    "source": filename,
                    "sheet": sheet_name,
                    "granularity": granularity,
                    "coverage": coverage_str,
                    "unique_values": unique_count,
                    "status": status,
                    "visualizations": vis_types,
                    "filters_supported": ["State/UT", "Year", "Zone"] if granularity == "State-Year" else ["Year"]
                })

    def _determine_visualizations(self, var_name, series, granularity):
        vis = []
        name_lower = var_name.lower()
        
        if any(k in name_lower for k in ['accident', 'fatalit', 'injur', 'ratio', 'slope', 'count', 'rate', 'death']):
            vis.extend(["Line Chart", "Bar Chart", "Time-Series Heatmap", "OLS Linear Regression"])
        if granularity in ["State-Year", "State-Snapshot"]:
            vis.extend(["State Comparison Bar", "Choropleth/Map", "Box Plot"])
        if granularity in ["Zone-Year", "Zone"]:
            vis.extend(["Grouped Bar", "Zone Multi-line Trend"])
        if any(k in name_lower for k in ['share', 'pct', 'percent', 'composition']):
            vis.extend(["100% Stacked Bar", "Donut Chart"])
        if any(k in name_lower for k in ['slope', 'r2', 'speed', 'rainfall']):
            vis.extend(["Distribution Histogram", "Scatter Plot"])
            
        return list(dict.fromkeys(vis)) # remove duplicates

    def _build_granularity_and_availability(self):
        # Register unavailable parameters with scientific explanation of why they are not in the primary panel
        standard_parameters = {
            "Accidents": "Reported road crash occurrences",
            "Fatalities": "Persons killed within 30 days of crash",
            "Injured": "Persons sustaining grievous or minor injuries",
            "Fatality_Ratio": "Fatalities per 100 accidents (Severity index)",
            "Zone": "Analytical grouping of Indian States/UTs",
            "State_UT": "Administrative reporting unit (36 current, 38 historical)",
            "Weather_Condition": "Atmospheric conditions at time of collision (Rain, Fog, Mist, Clear)",
            "Rainfall_mm": "Precipitation level measured by IMD",
            "Road_Category": "Highway classification (National Highway, State Highway, Other)",
            "Road_Condition": "Physical road surface condition (Potholed, Under Construction, Normal)",
            "Vehicle_Mode": "Mode of transport of victims (Two-Wheeler, Pedestrian, Car, Truck, Bus)",
            "Accident_Severity": "Classification by outcome (Fatal, Grievous, Minor, Non-Injury)",
            "Driver_Age": "Age profile of primary vehicle driver",
            "Driver_Gender": "Gender of involved operators",
            "Collision_Type": "Impact geometry (Head-On, Hit from Back, Hit Side, Overturn)",
            "Crash_Cause": "Contributory cause (Overspeeding, Drunk Driving, Wrong Side, Mobile Phone)",
            "Junction_Type": "Intersection configuration (T-Junction, Y-Junction, Roundabout)",
            "Traffic_Control": "Control mechanism (Signalized, Police Controlled, Uncontrolled)",
            "Lighting_Condition": "Environmental illumination (Daylight, Night lit, Night dark)",
            "Registered_Vehicles": "Vehicle population denominator from Vahan / MoRTH Transport Yearbook",
            "Population": "Census and projected state populations for exposure rates",
            "Road_Length_km": "Network length denominator for spatial accident density"
        }
        
        self.unavailable_parameters = {}
        for param, desc in standard_parameters.items():
            found = any(param.lower() in str(v["variable"]).lower() for v in self.variable_registry)
            if not found:
                self.unavailable_parameters[param] = {
                    "description": desc,
                    "status": "UNAVAILABLE IN ACTIVE PANEL",
                    "reason": "Not provided in the primary State-Year panel. Disaggregated state-level records require separate official source integration.",
                    "required_source": "IMD (Weather), MoRTH Form 1-4 / Table 2.2-2.3 (Road/Severity), Vahan (Exposure)",
                    "action_available": "Load Supporting Dataset / User Upload"
                }

    def get_variable_registry(self):
        if not self.variable_registry:
            self.discover_all()
        return self.variable_registry

    def get_summary(self):
        return {
            "total_variables": len(self.variable_registry),
            "available_parameters": sorted(list(self.available_parameters)),
            "unavailable_parameters": self.unavailable_parameters,
            "workbooks": list(self.workbooks_indexed.keys())
        }
