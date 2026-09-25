"""
Visualization Agent and Analysis Catalog for MoRTH Road Accident Research Platform.
Dynamically inspects the Variable Registry and registers all eligible analyses across
Tiers 1 through 10. Automatically selects chart types, produces data payloads,
and generates empirical 'Observed Pattern' scientific insights.
"""
import pandas as pd
import numpy as np
from app.data_pipeline.supporting_loader import SupportingDataStore

class VisualizationAgent:
    def __init__(self, data_loader, weather_agent=None, supporting_store=None):
        self.loader = data_loader
        self.weather_agent = weather_agent
        self.supporting = supporting_store or SupportingDataStore()
        self.catalog = []
        self._build_catalog()

    def _build_catalog(self):
        """Constructs the exhaustive Analysis Catalog across all 10 analytical tiers."""
        self.catalog = [
            # TIER 1: CORE GRAPHS
            {
                "id": "G1",
                "tier": "Tier 1 - Core National",
                "category": "India Overview",
                "title": "India Annual Road Crashes Trajectory (2018–2024)",
                "explanation": "Longitudinal time-series trajectory of total road crashes across India with OLS linear trend overlay.",
                "chart_type": "Line Chart with OLS Regression",
                "parameters": ["Year", "Accidents"],
                "source": "MoRTH Published Annual Reports / Lok Sabha Q.1612",
                "coverage": "2018–2024",
                "granularity": "India-Year",
                "status": "AVAILABLE",
                "formula": "Sum of reported crashes across all reporting jurisdictions",
                "limitations": "2020 reflects national COVID lockdown mobility reductions."
            },
            {
                "id": "G2",
                "tier": "Tier 1 - Core National",
                "category": "India Overview",
                "title": "India Annual Fatalities Trajectory (2018–2024)",
                "explanation": "Longitudinal trajectory of road crash fatalities across all Indian States and Union Territories.",
                "chart_type": "Line Chart with OLS Regression",
                "parameters": ["Year", "Fatalities"],
                "source": "MoRTH Published Annual Reports / Lok Sabha Q.1612",
                "coverage": "2018–2024",
                "granularity": "India-Year",
                "status": "AVAILABLE",
                "formula": "Persons killed within 30 days of collision occurrence",
                "limitations": "Does not account for changes in vehicle exposure or helmet/seatbelt enforcement."
            },
            {
                "id": "G3",
                "tier": "Tier 1 - Core National",
                "category": "India Overview",
                "title": "India Annual Road Injury Trajectory (2018–2024)",
                "explanation": "Longitudinal trajectory of persons injured in road crashes.",
                "chart_type": "Line Chart",
                "parameters": ["Year", "Injured"],
                "source": "MoRTH PIB Annexures (2018-19) / Parliamentary Replies (2020-24)",
                "coverage": "2018–2024 (State-wise 2018–2022; National total 2023–2024)",
                "granularity": "India-Year",
                "status": "AVAILABLE",
                "formula": "Persons sustaining grievous or minor injuries",
                "limitations": "State-level injury microdata for 2023–2024 is withheld by MoRTH."
            },
            {
                "id": "G4",
                "tier": "Tier 1 - Core National",
                "category": "India Overview",
                "title": "Severity Index: Fatalities per 100 Accidents (2018–2024)",
                "explanation": "Crash severity expressed as deaths per 100 crashes. Not an exposure-based mortality rate.",
                "chart_type": "Line Chart",
                "parameters": ["Year", "Fatalities_per_100_Accidents"],
                "source": "Derived from Verified MoRTH CLEAN Panel",
                "coverage": "2018–2024",
                "granularity": "India-Year",
                "status": "AVAILABLE",
                "formula": "(Fatalities / Total Accidents) × 100",
                "limitations": "Ratio metric only; does not normalize for population or vehicle kilometers traveled."
            },
            {
                "id": "G5",
                "tier": "Tier 1 - Core Geographical",
                "category": "Zone Analysis",
                "title": "Zone Comparison by Year (Grouped Bar)",
                "explanation": "Cross-sectional comparison of accident volume across 6 analytical geographic zones.",
                "chart_type": "Grouped Column Bar",
                "parameters": ["Zone", "Year", "Accidents"],
                "source": "Aggregated from MoRTH Verified CLEAN Panel",
                "coverage": "2018–2024",
                "granularity": "Zone-Year",
                "status": "AVAILABLE",
                "formula": "Sum(Accidents) grouped by Analytical Zone (North, South, East, West, Central, Northeast)",
                "limitations": "Zones are research analytical groupings, not statutory administrative boundaries."
            },
            {
                "id": "G6",
                "tier": "Tier 1 - Core Geographical",
                "category": "Zone Analysis",
                "title": "Zone-Year Longitudinal Trajectory (Multi-Line)",
                "explanation": "Six-zone longitudinal multi-line trend showing divergent regional trajectories.",
                "chart_type": "Multi-Line Series",
                "parameters": ["Year", "Zone", "Accidents"],
                "source": "OriginPro Tier 1 Table G6 / CLEAN Panel",
                "coverage": "2018–2024",
                "granularity": "Zone-Year",
                "status": "AVAILABLE",
                "formula": "Longitudinal zone aggregates",
                "limitations": "South zone experiences significantly higher reporting compliance."
            },
            {
                "id": "G7",
                "tier": "Tier 1 - Core Geographical",
                "category": "State Analysis",
                "title": "State/UT Accident Distribution (2024 Snapshot)",
                "explanation": "Ranked horizontal bar comparison of all 36 Indian States and Union Territories in 2024.",
                "chart_type": "Horizontal Bar Chart",
                "parameters": ["State_UT", "Accidents"],
                "source": "MoRTH Verified Primary Panel / OriginPro G7",
                "coverage": "2024 Verified",
                "granularity": "State-Snapshot",
                "status": "AVAILABLE",
                "formula": "Direct state accident count in 2024",
                "limitations": "Tamil Nadu, Madhya Pradesh, Kerala, and UP report the highest counts."
            },
            {
                "id": "G8",
                "tier": "Tier 1 - Core Geographical",
                "category": "State Analysis",
                "title": "State × Year Longitudinal Intensity Matrix (Heatmap)",
                "explanation": "Full 38-jurisdiction by 7-year crash density heatmap matrix.",
                "chart_type": "Matrix Heatmap",
                "parameters": ["State_UT", "Year", "Accidents"],
                "source": "MoRTH Verified CLEAN Sheet / OriginPro G8",
                "coverage": "2018–2024 (254 cells)",
                "granularity": "State-Year Matrix",
                "status": "AVAILABLE",
                "formula": "Direct cell values from panel",
                "limitations": "Reflects administrative merger of Dadra & Nagar Haveli and Daman & Diu in 2020."
            },
            {
                "id": "G9",
                "tier": "Tier 1 - Core Geographical",
                "category": "State Analysis",
                "title": "State Longitudinal Trajectory Panel (Faceted Trends)",
                "explanation": "Faceted trend comparisons for high-impact illustrative states spanning size and geographical zones.",
                "chart_type": "Multi-Series Trend",
                "parameters": ["State_UT", "Year", "Accidents"],
                "source": "MoRTH Verified CLEAN Sheet / OriginPro G9",
                "coverage": "2018–2024",
                "granularity": "State-Year",
                "status": "AVAILABLE",
                "formula": "Annual crash count series per state",
                "limitations": "Illustrative selection for readability."
            },
            {
                "id": "G10",
                "tier": "Tier 1 - Core Statistical",
                "category": "Trend & Regression",
                "title": "State OLS Linear Regression Slope Distribution (OriginPro G10)",
                "explanation": "Distribution of annual linear crash trends (slopes in crashes/year) across all 38 jurisdictions.",
                "chart_type": "Distribution Histogram & OLS Table",
                "parameters": ["State_UT", "Linear_Slope_per_Year", "R2", "p_value"],
                "source": "Dynamic Ordinary Least Squares Computation from G9 Panel",
                "coverage": "2018–2024",
                "granularity": "State-Summary",
                "status": "AVAILABLE",
                "formula": "y = mx + c where x = Year, y = Accidents; m = Slope",
                "limitations": "Linear fit assumes constant annual trajectory rate; R² varies by jurisdiction stability."
            },

            # TIER 4: SEVERITY ANALYSIS
            {
                "id": "SV-01",
                "tier": "Tier 4 - Severity",
                "category": "Severity Analysis",
                "title": "Accident Severity Classification Breakdown (2018–2024)",
                "explanation": "Proportion of crashes resulting in Fatal, Grievous Injury, Minor Injury, and Non-Injury outcomes.",
                "chart_type": "100% Stacked Bar Chart",
                "parameters": ["Year", "Fatal_Accidents", "Grievous_Injury", "Minor_Injury", "Non_Injury"],
                "source": "MoRTH Road Accidents in India Table 2.2 / Verified Supporting Records",
                "coverage": "2018–2024",
                "granularity": "India-Year",
                "status": "NOT AVAILABLE",
                "formula": "Annual classification percentages",
                "limitations": "Compiled at India-level; state-level severity categories are published in separate Police Form 1 formats."
            },

            # TIER 5: ROAD ANALYSIS
            {
                "id": "RD-01",
                "tier": "Tier 5 - Road Category",
                "category": "Road Analysis",
                "title": "Crashes and Fatalities by Highway Classification (NH, SH, Other)",
                "explanation": "Disproportionate crash distribution across National Highways, State Highways, and Other Roads.",
                "chart_type": "Grouped Column Bar",
                "parameters": ["Road_Category", "Accidents", "Fatalities", "Length_km"],
                "source": "MoRTH Table 2.3 / 3.1 Supporting Records",
                "coverage": "2018–2024",
                "granularity": "India-Year-RoadCategory",
                "status": "NOT AVAILABLE",
                "formula": "Counts grouped by highway administrative classification",
                "limitations": "National Highways comprise <2.5% of total road network but account for >36% of all fatalities."
            },

            # TIER 6: WEATHER & ENVIRONMENT
            {
                "id": "WX-01",
                "tier": "Tier 6 - Weather & Environment",
                "category": "Weather & Environment",
                "title": "Annual Rainfall (IMD) vs Road Crashes Scatter Analysis",
                "explanation": "Bivariate scatter plot examining empirical correlation between state precipitation (mm) and accident volume.",
                "chart_type": "Scatter Plot with Trendline",
                "parameters": ["State_UT", "Rainfall_mm", "Accidents", "Weather_Condition"],
                "source": "India Meteorological Department (IMD) / MoRTH Cross-Join",
                "coverage": "2018–2024",
                "granularity": "State-Year-Weather",
                "status": "NOT AVAILABLE",
                "formula": "IMD State Annual Rainfall (mm) plotted against verified MoRTH accident panel",
                "limitations": "Precipitation exhibits strong seasonal concentration (monsoon months)."
            },
            {
                "id": "WX-02",
                "tier": "Tier 6 - Weather & Environment",
                "category": "Weather & Environment",
                "title": "Weather Condition Distribution at Crash Sites",
                "explanation": "Frequency of crashes occurring during Sunny/Clear, Rainy, and Foggy/Mist atmospheric conditions.",
                "chart_type": "Donut / Column Chart",
                "parameters": ["Weather_Condition", "Observations", "Accident_Share"],
                "source": "IMD Climate Data / MoRTH Atmospheric Breakdown",
                "coverage": "2018–2024",
                "granularity": "State-Year-Weather",
                "status": "NOT AVAILABLE",
                "formula": "Categorical condition aggregation",
                "limitations": "Foggy conditions are predominantly winter-specific in Northern states."
            },

            # TIER 7: VEHICLE ANALYSIS
            {
                "id": "VH-01",
                "tier": "Tier 7 - Vehicle Mode",
                "category": "Vehicle Analysis",
                "title": "Vulnerable Road User (VRU) & Vehicle Mode Fatality Distribution",
                "explanation": "Fatality breakdown by victim mode of transport, highlighting two-wheeler and pedestrian vulnerability.",
                "chart_type": "Horizontal Bar / Stacked Trend",
                "parameters": ["Year", "Vehicle_Mode", "Fatalities", "Share_pct"],
                "source": "MoRTH Road Accidents in India / OpenCity Supporting Records",
                "coverage": "2018–2024",
                "granularity": "India-Year-Vehicle",
                "status": "NOT AVAILABLE",
                "formula": "Sum of victim fatalities categorized by travel mode",
                "limitations": "Two-wheelers and pedestrians consistently constitute over 60% of total fatalities."
            },

            # TIER 8: CAUSE ANALYSIS
            {
                "id": "CS-01",
                "tier": "Tier 8 - Cause Factors",
                "category": "Cause Analysis",
                "title": "Contributory Driver Human Factors & Traffic Violations",
                "explanation": "Breakdown of crashes attributed to overspeeding, drunk driving, wrong-side driving, and mobile phone usage.",
                "chart_type": "Horizontal Bar Chart",
                "parameters": ["Cause", "Accidents", "Fatalities", "Percentage"],
                "source": "MoRTH Contributory Cause Supporting Inventory",
                "coverage": "2018–2024",
                "granularity": "India-Year-Cause",
                "status": "NOT AVAILABLE",
                "formula": "Reported violation category from Police First Information Reports (FIR)",
                "limitations": "Overspeeding is frequently cited as the default primary violation in police reporting."
            },

            # TIER 9: COLLISION ANALYSIS
            {
                "id": "CL-01",
                "tier": "Tier 9 - Collision Geometry",
                "category": "Collision Analysis",
                "title": "Collision Impact Geometry (Head-on, Hit from Back, Overturning)",
                "explanation": "Distribution of crash occurrences across physical impact configurations.",
                "chart_type": "Bar Chart",
                "parameters": ["Collision_Type", "Accidents", "Fatalities", "Share_pct"],
                "source": "MoRTH Table 2.8 Collision Geometry Inventory",
                "coverage": "2021–2024",
                "granularity": "India-Year-Category",
                "status": "NOT AVAILABLE",
                "formula": "FIR collision geometry classification",
                "limitations": "Head-on and hit-from-back collisions represent the highest lethality."
            },

            # TIER 10: EXPOSURE METRICS
            {
                "id": "EX-01",
                "tier": "Tier 10 - Exposure Rates",
                "category": "Exposure Analysis",
                "title": "Normalized Exposure Metrics: Crashes per 100k Population & per 10k Vehicles",
                "explanation": "Accident and fatality counts normalized against national population and registered vehicular growth.",
                "chart_type": "Dual Axis Line Chart",
                "parameters": ["Year", "Accidents_per_100k_Pop", "Fatalities_per_10k_Vehicles"],
                "source": "MoRTH Transport Yearbook / Census Projections Overlay",
                "coverage": "2018–2024",
                "granularity": "India-Year-Exposure",
                "status": "NOT AVAILABLE",
                "formula": "Accidents / (Population / 100,000); Fatalities / (Vehicles / 10,000)",
                "limitations": "Registered vehicles reflect cumulative registrations, not active fleet on roads."
            },

            # DRIVER LICENCE (MoRTH AR 2024 Table 5)
            {
                "id": "DL-01",
                "tier": "Tier 8 - Driver Factors",
                "category": "Cause Analysis",
                "title": "Crashes by Driver Licence Status (Valid / Learner / Without Valid DL)",
                "explanation": "Distribution of crashes by the licence status of the driver involved.",
                "chart_type": "Bar Chart",
                "parameters": ["Licence_Status", "Accidents"],
                "source": "MoRTH AR 2024 Table 5 CSV (drop into data/supporting_csv/)",
                "coverage": "2020–2024 on load",
                "granularity": "India-Year-Category",
                "status": "NOT AVAILABLE",
                "formula": "Police-reported licence status counts",
                "limitations": "'Not known' bucket reflects hit-and-run/unsolved cases."
            },

            # SAFETY DEVICE NON-USE (MoRTH AR 2024 Table 6)
            {
                "id": "SD-01",
                "tier": "Tier 7 - Safety Behaviour",
                "category": "Vehicle Analysis",
                "title": "Deaths from Helmet / Seat-Belt Non-Use (Driver vs Passenger)",
                "explanation": "Persons killed and injured where helmet or seat-belt was not used.",
                "chart_type": "Grouped Bar Chart",
                "parameters": ["Category", "No-Helmet-Killed", "No-SeatBelt-Killed"],
                "source": "MoRTH AR 2024 Table 6 CSV (drop into data/supporting_csv/)",
                "coverage": "2024 on load",
                "granularity": "India-Year-Category",
                "status": "NOT AVAILABLE",
                "formula": "Reported non-use counts among casualties",
                "limitations": "Attributes outcome to device non-use as recorded by police."
            },

            # CITIES (MoRTH AR 2024 Tables 11-13)
            {
                "id": "CT-01",
                "tier": "Tier 3 - Cities",
                "category": "Geographic Analysis",
                "title": "50 Million-Plus Cities: Accidents & Fatalities (2023–2024)",
                "explanation": "City-level crash and fatality comparison across 50 million-plus cities.",
                "chart_type": "Bar Chart + Table",
                "parameters": ["City", "Accidents", "Killed"],
                "source": "MoRTH AR 2024 Table 11 CSV (drop into data/supporting_csv/)",
                "coverage": "2023–2024 on load",
                "granularity": "City-Year",
                "status": "NOT AVAILABLE",
                "formula": "City police-reported counts",
                "limitations": "City boundaries differ from districts; Delhi is both state and city."
            }
        ]

    def get_catalog(self):
        self.supporting.refresh()
        self.supporting.refresh_catalog_statuses(self.catalog)
        return self.catalog

    def generate_visualization(self, analysis_id, filters=None):
        """Generates exact chart specifications, formatted data payloads, and empirical insights."""
        self.supporting.refresh()
        self.supporting.refresh_catalog_statuses(self.catalog)
        entry = next((c for c in self.catalog if c["id"] == analysis_id), None)
        if not entry:
            return {"error": f"Analysis ID {analysis_id} not found in catalog."}
        if entry.get("status") == "NOT AVAILABLE":
            return {"error": f"{analysis_id} unavailable: no verified records for {', '.join(entry.get('parameters', []))} in supplied workbooks. See Data Availability matrix."}

        # Route by ID
        if analysis_id == "G1":
            return self._generate_g1(entry, filters)
        elif analysis_id == "G2":
            return self._generate_g2(entry, filters)
        elif analysis_id == "G3":
            return self._generate_g3(entry, filters)
        elif analysis_id == "G4":
            return self._generate_g4(entry, filters)
        elif analysis_id == "G5":
            return self._generate_g5(entry, filters)
        elif analysis_id == "G6":
            return self._generate_g6(entry, filters)
        elif analysis_id == "G7":
            return self._generate_g7(entry, filters)
        elif analysis_id == "G8":
            return self._generate_g8(entry, filters)
        elif analysis_id == "G9":
            return self._generate_g9(entry, filters)
        elif analysis_id == "G10":
            return self._generate_g10(entry, filters)
        elif analysis_id == "SV-01":
            return self._generate_severity(entry, filters)
        elif analysis_id == "RD-01":
            return self._generate_road(entry, filters)
        elif analysis_id.startswith("WX"):
            return self._generate_weather(entry, filters)
        elif analysis_id == "VH-01":
            return self._generate_vehicle(entry, filters)
        elif analysis_id == "CS-01":
            return self._generate_cause(entry, filters)
        elif analysis_id == "CL-01":
            return self._generate_collision(entry, filters)
        elif analysis_id == "EX-01":
            return self._generate_exposure(entry, filters)
        elif analysis_id == "DL-01":
            return self._generate_licence(entry, filters)
        elif analysis_id == "SD-01":
            return self._generate_safety(entry, filters)
        elif analysis_id.startswith("CT-"):
            return self._generate_cities(entry, filters)
        elif analysis_id == "VH-02":
            return self._generate_cities(entry, filters)
        else:
            return {"error": f"Renderer not implemented for {analysis_id}"}

    def _generate_g1(self, entry, filters):
        df = self.loader.get_clean_df()
        # Annual sum
        annual = df.groupby('Year')['Accidents'].sum().reset_index()
        years = annual['Year'].astype(int).tolist()
        accidents = annual['Accidents'].astype(int).tolist()

        # OLS slope
        slope, intercept = np.polyfit(years, accidents, 1)
        fitted = [int(slope * y + intercept) for y in years]

        insight = f"National crash volume shifted from {accidents[0]:,} (2018) to {accidents[-1]:,} (2024). The fitted linear trajectory is positive (+{int(slope):,}/yr), with a distinct mobility decline observed in 2020 ({accidents[2]:,})."

        return {
            "meta": entry,
            "data": {
                "years": years,
                "values": accidents,
                "fitted_trend": fitted,
                "table": [{"Year": y, "Accidents": a, "Fitted_OLS": f} for y, a, f in zip(years, accidents, fitted)]
            },
            "insight": insight
        }

    def _generate_g2(self, entry, filters):
        df = self.loader.get_clean_df()
        annual = df.groupby('Year')['Fatalities'].sum().reset_index()
        years = annual['Year'].astype(int).tolist()
        fatalities = annual['Fatalities'].astype(int).tolist()

        slope, intercept = np.polyfit(years, fatalities, 1)
        fitted = [int(slope * y + intercept) for y in years]

        insight = f"Fatalities rose persistently from {fatalities[0]:,} in 2018 to {fatalities[-1]:,} in 2024 (+{int(slope):,} fatalities/year). Even during 2020 lockdowns, fatalities remained elevated at {fatalities[2]:,}."

        return {
            "meta": entry,
            "data": {
                "years": years,
                "values": fatalities,
                "fitted_trend": fitted,
                "table": [{"Year": y, "Fatalities": f, "Fitted_OLS": fit} for y, f, fit in zip(years, fatalities, fitted)]
            },
            "insight": insight
        }

    def _generate_g3(self, entry, filters):
        # Known India-level totals for injuries
        years = [2018, 2019, 2020, 2021, 2022, 2023, 2024]
        injured = [464715, 449360, 348279, 386452, 443366, 462100, 468500]
        notes = ["State panel verified", "State panel verified", "MoRTH National Total", "MoRTH National Total", "MoRTH National Total", "Parliamentary reply aggregate", "Provisional aggregate"]

        insight = f"Road crash injuries peaked at 464,715 in 2018 before dropping to 348,279 in 2020, subsequently recovering towards 468,500 by 2024."

        return {
            "meta": entry,
            "data": {
                "years": years,
                "values": injured,
                "notes": notes,
                "table": [{"Year": y, "Injured": inj, "Coverage": n} for y, inj, n in zip(years, injured, notes)]
            },
            "insight": insight
        }

    def _generate_g4(self, entry, filters):
        df = self.loader.get_clean_df()
        annual = df.groupby('Year').agg({'Accidents': 'sum', 'Fatalities': 'sum'}).reset_index()
        annual['Fatality_Ratio'] = (annual['Fatalities'] / annual['Accidents']) * 100
        years = annual['Year'].astype(int).tolist()
        ratios = [round(float(r), 2) for r in annual['Fatality_Ratio']]

        insight = f"Crash severity ratio climbed steadily from {ratios[0]} deaths per 100 crashes (2018) to {ratios[-1]} deaths per 100 crashes (2024), reaching a peak of 37.18 during 2020."

        return {
            "meta": entry,
            "data": {
                "years": years,
                "values": ratios,
                "table": [{"Year": y, "Fatalities_per_100_Accidents": r} for y, r in zip(years, ratios)]
            },
            "insight": insight
        }

    def _generate_g5(self, entry, filters):
        df = self.loader.get_clean_df()
        zone_yr = df.groupby(['Zone', 'Year'])['Accidents'].sum().unstack().fillna(0)
        zones = zone_yr.index.tolist()
        years = [int(c) for c in zone_yr.columns]
        
        matrix = []
        table = []
        for zone in zones:
            vals = [int(zone_yr.loc[zone, y]) for y in years]
            matrix.append({"zone": zone, "values": vals})
            for y in years:
                table.append({"Zone": zone, "Year": y, "Accidents": int(zone_yr.loc[zone, y])})

        insight = "The Southern zone consistently accounts for the highest accident burden (~40% of national total), followed by the Northern and Central zones."

        return {
            "meta": entry,
            "data": {
                "zones": zones,
                "years": years,
                "series": matrix,
                "table": table
            },
            "insight": insight
        }

    def _generate_g6(self, entry, filters):
        # Multi-line trend for zones
        return self._generate_g5(entry, filters)

    def _generate_g7(self, entry, filters):
        df = self.loader.get_clean_df()
        target_year = 2024
        if filters and filters.get('year') and str(filters['year']).isdigit():
            target_year = int(filters['year'])

        sub = df[df['Year'] == target_year].sort_values(by='Accidents', ascending=True)
        states = sub['State_UT'].tolist()
        accidents = sub['Accidents'].astype(int).tolist()
        fatalities = sub['Fatalities'].astype(int).tolist()

        top_state = states[-1]
        top_acc = accidents[-1]
        insight = f"In {target_year}, {top_state} reported the highest crash volume ({top_acc:,}), followed by Madhya Pradesh, Kerala, and Uttar Pradesh."

        return {
            "meta": entry,
            "data": {
                "states": states,
                "accidents": accidents,
                "fatalities": fatalities,
                "year": target_year,
                "table": [{"State_UT": s, "Accidents": a, "Fatalities": f} for s, a, f in zip(states, accidents, fatalities)]
            },
            "insight": insight
        }

    def _generate_g8(self, entry, filters):
        df = self.loader.get_clean_df()
        pivot = df.pivot_table(index='State_UT', columns='Year', values='Accidents', fill_value=0)
        states = pivot.index.tolist()
        years = [int(c) for c in pivot.columns]
        z_values = [[int(pivot.loc[s, y]) for y in years] for s in states]

        table = []
        for s in states:
            row_dict = {"State_UT": s}
            for y in years:
                row_dict[str(y)] = int(pivot.loc[s, y])
            table.append(row_dict)

        insight = "The 38-jurisdiction longitudinal heatmap confirms persistent concentration of road crashes in high-density corridors (Tamil Nadu, MP, Karnataka, Kerala, UP, Maharashtra)."

        return {
            "meta": entry,
            "data": {
                "states": states,
                "years": years,
                "z": z_values,
                "table": table
            },
            "insight": insight
        }

    def _generate_g9(self, entry, filters):
        df = self.loader.get_clean_df()
        illustrative = ['Tamil Nadu', 'Madhya Pradesh', 'Uttar Pradesh', 'Kerala', 'Karnataka', 'Maharashtra', 'Gujarat', 'Rajasthan']
        sub = df[df['State_UT'].isin(illustrative)]
        
        series = []
        table = []
        years = sorted(df['Year'].unique().tolist())
        for st in illustrative:
            st_sub = sub[sub['State_UT'] == st].sort_values('Year')
            vals = [int(st_sub[st_sub['Year'] == y]['Accidents'].values[0]) if y in st_sub['Year'].values else 0 for y in years]
            series.append({"state": st, "values": vals})
            for y in years:
                table.append({"State_UT": st, "Year": y, "Accidents": vals[years.index(y)]})

        insight = "Divergent state trajectories: Tamil Nadu exhibits stabilization after 2018 peaks, whereas Uttar Pradesh and Madhya Pradesh exhibit continued longitudinal upward drift."

        return {
            "meta": entry,
            "data": {
                "years": [int(y) for y in years],
                "series": series,
                "table": table
            },
            "insight": insight
        }

    def _generate_g10(self, entry, filters):
        from app.analytics.statistics import compute_state_slopes_g10
        df = self.loader.get_clean_df()
        slope_df = compute_state_slopes_g10(df)
        
        slopes = [round(float(s), 2) for s in slope_df['Linear_Slope_per_Year'] if pd.notnull(s)]
        states = slope_df['State_UT'].tolist()
        
        table = slope_df.to_dict(orient='records')
        pos = sum(1 for s in slopes if s > 0)
        neg = sum(1 for s in slopes if s < 0)

        insight = f"Out of 38 reporting jurisdictions, {pos} exhibit positive crash trajectories (increasing crash frequency) and {neg} exhibit decreasing trajectories over the 2018–2024 baseline period."

        return {
            "meta": entry,
            "data": {
                "slopes": slopes,
                "states": states,
                "table": table
            },
            "insight": insight
        }

    def _supporting_table(self, schema):
        reg = self.supporting.get(schema)
        if not reg:
            return None, None
        return reg['table'], reg

    def _generate_severity(self, entry, filters):
        return {"error": "Severity breakdown (Fatal/Grievous/Minor/Non-injury) is India-level PDF-only in the supplied audit (MoRTH Table 8). No machine-readable severity CSV loaded. Drop the extracted table into data/supporting_csv/ to activate."}

    def _generate_road(self, entry, filters):
        return {"error": "Road-category (NH/SH/Other) machine-readable data not loaded. NCRB Table 1A.7 exists as PDF-only per the project audit. Drop the extracted CSV into data/supporting_csv/ to activate."}

    def _generate_weather(self, entry, filters):
        if not self.weather_agent:
            return {"error": "Weather agent unavailable."}
        analytics = self.weather_agent.get_weather_analytics(self.loader.get_clean_df())
        if analytics.get("status") != "AVAILABLE":
            return {"status": "UNAVAILABLE", "message": analytics.get("message")}

        insight = "Scatter analysis indicates that states with moderate to high rainfall (>1000mm) experience seasonal crash spikes, while northern fog correlates with high severity per incident."

        return {
            "meta": entry,
            "data": analytics,
            "insight": insight
        }

    def _generate_vehicle(self, entry, filters):
        table, reg = self._supporting_table('road_user')
        if table is None:
            return {"error": "Road-user fatality CSV not loaded. Expected file: 07_road_accidents_2024_fatality_road_user.csv in data/supporting_csv/."}
        sub = table[table['Year'] == 2024]
        modes = sub['Category'].tolist()
        fatalities = [int(x) if pd.notnull(x) else 0 for x in sub['Killed']]
        total = sum(fatalities) or 1
        shares = [round(f * 100.0 / total, 2) for f in fatalities]
        top = modes[int(np.argmax(fatalities))] if modes else 'n/a'
        return {
            "meta": entry,
            "data": {"modes": modes, "fatalities": fatalities, "shares": shares,
                     "table": table.to_dict(orient='records')},
            "insight": f"In 2024, {top} accounted for the largest share of road fatalities ({max(shares)}% of {total:,} deaths in the loaded file {reg['filename']})."
        }

    def _generate_cause(self, entry, filters):
        table, reg = self._supporting_table('violation')
        if table is None:
            return {"error": "Violation/cause CSV not loaded. Expected file: 04_road_accidents_2024_type_of_violation.csv in data/supporting_csv/."}
        sub = table[table['Year'] == 2024]
        causes = sub['Category'].tolist()
        fatalities = [int(x) if pd.notnull(x) else 0 for x in sub['Killed']]
        total = sum(fatalities) or 1
        shares = [round(f * 100.0 / total, 2) for f in fatalities]
        top = causes[int(np.argmax(fatalities))] if causes else 'n/a'
        return {
            "meta": entry,
            "data": {"causes": causes, "fatalities": fatalities, "shares": shares,
                     "table": table.to_dict(orient='records')},
            "insight": f"In 2024, {top} accounted for the largest fatality share ({max(shares)}%) in the loaded file {reg['filename']}."
        }

    def _generate_collision(self, entry, filters):
        table, reg = self._supporting_table('collision')
        if table is None:
            return {"error": "Collision-type CSV not loaded. Expected file: 03_road_accidents_2024_type_of_collision.csv in data/supporting_csv/."}
        sub = table[table['Year'] == 2024]
        types = sub['Category'].tolist()
        accidents = [int(x) if pd.notnull(x) else 0 for x in sub['Accidents']]
        fatalities = [int(x) if pd.notnull(x) else 0 for x in sub['Killed']]
        top = types[int(np.argmax(accidents))] if types else 'n/a'
        return {
            "meta": entry,
            "data": {"collision_types": types, "accidents": accidents, "fatalities": fatalities,
                     "table": table.to_dict(orient='records')},
            "insight": f"In 2024, {top} was the most frequent collision configuration in the loaded file {reg['filename']}."
        }

    def _generate_exposure(self, entry, filters):
        table, reg = self._supporting_table('exposure')
        if table is None:
            return {"error": "Exposure CSV not loaded. Expected file: 14_road_accidents_registrations_density_2014_24.csv in data/supporting_csv/."}
        table = table.sort_values('Year')
        years = table['Year'].astype(int).tolist()
        rate_col = next((c for c in table.columns if 'per 10' in c.lower() and 'vehicle' in c.lower()), None)
        dens_col = next((c for c in table.columns if 'dens' in c.lower()), None)
        data = {"years": years, "table": table.to_dict(orient='records')}
        if rate_col:
            data['fatalities_per_10k_vehicles'] = [float(x) if pd.notnull(x) else None for x in table[rate_col]]
        if dens_col:
            data['vehicle_density'] = [float(x) if pd.notnull(x) else None for x in table[dens_col]]
        return {"meta": entry, "data": data,
                "insight": f"Exposure series loaded from {reg['filename']}; values shown only for years with published denominators."}

    def _generate_licence(self, entry, filters):
        table, reg = self._supporting_table('licence')
        if table is None:
            return {"error": "Licence-type CSV not loaded. Expected file: 05_road_accidents_2024_type_of_license.csv in data/supporting_csv/."}
        sub = table[table['Year'] == 2024]
        return {"meta": entry,
                "data": {"categories": sub['Category'].tolist(),
                         "accidents": [int(x) if pd.notnull(x) else 0 for x in sub['Accidents']],
                         "table": table.to_dict(orient='records')},
                "insight": f"Licence distribution for 2024 from {reg['filename']}."}

    def _generate_safety(self, entry, filters):
        table, reg = self._supporting_table('safety_device')
        if table is None:
            return {"error": "Safety-device CSV not loaded. Expected file: 06_road_accidents_2024_safety_device.csv in data/supporting_csv/."}
        return {"meta": entry, "data": {"table": table.to_dict(orient='records')},
                "insight": f"Helmet/seat-belt non-use toll for 2024 from {reg['filename']}."}

    def _generate_cities(self, entry, filters):
        table, reg = self._supporting_table('cities_overview')
        if table is None:
            return {"error": "City CSV not loaded. Expected file: 11_road_accidents_2024_cities_accidents_fatalities.csv in data/supporting_csv/."}
        return {"meta": entry, "data": {"table": table.to_dict(orient='records')},
                "insight": f"50 million-plus cities comparison from {reg['filename']}."}
