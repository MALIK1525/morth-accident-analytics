"""
Weather Data Agent for MoRTH Road Accident Research Platform.
Manages discovery, validation, join compatibility, and analytical generation for atmospheric
and precipitation variables (IMD rainfall, weather conditions, fog, monsoon).
"""
import os
import pandas as pd
import numpy as np

class WeatherAgent:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.weather_file = os.path.join(data_dir, "supporting_imd_weather.csv")
        self.is_loaded = False
        self.weather_df = None
        self.merged_df = None

    def check_status(self):
        """Checks if verified weather data is loaded into the active analytical session."""
        return {
            "loaded": self.is_loaded,
            "file_available": os.path.exists(self.weather_file),
            "source": "India Meteorological Department (IMD) / India-WRIS",
            "granularity": "State-Year",
            "coverage": "2018–2024 (13 Key Meteorologically Diverse States)",
            "message": "Weather dataset loaded and verified." if self.is_loaded else "Weather analysis is currently unavailable because verified weather records are not loaded."
        }

    def load_weather_dataset(self, primary_df=None):
        """Loads and validates the supporting IMD weather records."""
        if not os.path.exists(self.weather_file):
            return {
                "success": False,
                "error": "Supporting weather file supporting_imd_weather.csv not found in data directory."
            }
            
        try:
            df = pd.read_csv(self.weather_file)
            # Basic validation
            required_cols = ["State_UT", "Year", "Weather_Condition", "Rainfall_mm"]
            if not all(col in df.columns for col in required_cols):
                return {"success": False, "error": f"Missing required weather schema: {required_cols}"}

            self.weather_df = df
            self.is_loaded = True

            # If primary dataset provided, perform safe composite join on (State_UT, Year)
            if primary_df is not None:
                self.merged_df = pd.merge(
                    primary_df,
                    self.weather_df,
                    on=["State_UT", "Year"],
                    how="inner"
                )
                
            return {
                "success": True,
                "records_loaded": len(self.weather_df),
                "states_covered": int(self.weather_df["State_UT"].nunique()),
                "years_covered": f"{int(self.weather_df['Year'].min())}–{int(self.weather_df['Year'].max())}",
                "variables_registered": ["Weather_Condition", "Rainfall_mm", "Accident_Weather_Share_pct", "Visibility_km"],
                "message": "IMD Weather dataset successfully loaded and validated."
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_weather_analytics(self, primary_df=None):
        """Produces verified analytical summaries for weather visualizations."""
        if not self.is_loaded:
            if os.path.exists(self.weather_file):
                self.load_weather_dataset(primary_df)
            else:
                return {"status": "UNAVAILABLE", "message": "Weather records not loaded."}

        if self.merged_df is None and primary_df is not None:
            self.merged_df = pd.merge(primary_df, self.weather_df, on=["State_UT", "Year"], how="inner")

        df = self.merged_df if self.merged_df is not None else self.weather_df

        # 1. Weather condition distribution
        cond_counts = df.groupby("Weather_Condition").agg(
            Observations=("Year", "count"),
            Avg_Rainfall=("Rainfall_mm", "mean")
        ).reset_index()
        
        # 2. Rainfall vs Accidents Scatter Points
        scatter_acc = []
        scatter_fat = []
        if "Accidents" in df.columns:
            for _, r in df.iterrows():
                scatter_acc.append({
                    "state": str(r["State_UT"]),
                    "year": int(r["Year"]),
                    "rainfall_mm": round(float(r["Rainfall_mm"]), 1),
                    "accidents": int(r["Accidents"]),
                    "weather": str(r["Weather_Condition"])
                })
                scatter_fat.append({
                    "state": str(r["State_UT"]),
                    "year": int(r["Year"]),
                    "rainfall_mm": round(float(r["Rainfall_mm"]), 1),
                    "fatalities": int(r["Fatalities"]),
                    "weather": str(r["Weather_Condition"])
                })

        # 3. Weather impact by state
        state_weather = df.groupby("State_UT").agg(
            Avg_Rainfall=("Rainfall_mm", "mean"),
            Dominant_Weather=("Weather_Condition", lambda x: x.mode()[0] if not x.empty else "N/A")
        ).reset_index()

        return {
            "status": "AVAILABLE",
            "condition_distribution": cond_counts.to_dict(orient="records"),
            "rainfall_vs_accidents": scatter_acc,
            "rainfall_vs_fatalities": scatter_fat,
            "state_weather_summary": state_weather.to_dict(orient="records"),
            "methodology_note": "Precipitation data compiled from IMD state weather summaries. Correlated strictly for states with matching annual recording periods."
        }
