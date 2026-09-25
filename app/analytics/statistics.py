"""
Statistical Analysis and OriginPro Table Computation Engine.
Calculates Ordinary Least Squares (OLS) linear regressions, state slopes (G10),
correlation matrices, and longitudinal CAGR without fabrication.
"""
import pandas as pd
import numpy as np
from scipy import stats

def compute_linear_trend(years, values):
    """
    Computes rigorous Ordinary Least Squares (OLS) regression:
    y = slope * x + intercept
    Returns slope, intercept, R^2, p-value, standard error.
    """
    # Filter non-null pairs
    mask = ~np.isnan(years) & ~np.isnan(values)
    x = np.array(years)[mask]
    y = np.array(values)[mask]
    
    if len(x) < 3:
        return {
            "status": "INSUFFICIENT_DATA",
            "slope": None, "intercept": None, "r_squared": None,
            "p_value": None, "std_err": None, "n": len(x)
        }
        
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    
    return {
        "status": "COMPUTED",
        "slope": float(slope),
        "intercept": float(intercept),
        "r_squared": float(r_value ** 2),
        "p_value": float(p_value),
        "std_err": float(std_err),
        "n": int(len(x))
    }

def compute_state_slopes_g10(clean_df, metric="Accidents"):
    """
    Computes OriginPro G10 Linear Regression Slope Table across all reporting states/UTs.
    Models: Metric ~ Year (2018–2024).
    """
    results = []
    states = sorted(clean_df['State_UT'].unique())
    
    for state in states:
        sub = clean_df[clean_df['State_UT'] == state].sort_values('Year')
        sub = sub.dropna(subset=[metric, 'Year'])
        
        # Exclude administrative blank years (e.g. Ladakh 2018-2020 where values were NV)
        x = sub['Year'].values
        y = sub[metric].values
        
        reg = compute_linear_trend(x, y)
        if reg['status'] == "COMPUTED":
            slope = reg['slope']
            if slope > 50:
                trend_type = "Increasing fitted trend"
            elif slope < -50:
                trend_type = "Decreasing fitted trend"
            else:
                trend_type = "Relatively flat fitted trend"
                
            results.append({
                "State_UT": state,
                "N": reg['n'],
                "Slope": round(reg['slope'], 2),
                "Intercept": round(reg['intercept'], 2),
                "R2": round(reg['r_squared'], 4),
                "p_value": round(reg['p_value'], 5),
                "Std_Err": round(reg['std_err'], 2),
                "Trend_Type": trend_type,
                "Status": "COMPUTED"
            })
        else:
            results.append({
                "State_UT": state,
                "N": reg['n'],
                "Slope": None,
                "Intercept": None,
                "R2": None,
                "p_value": None,
                "Std_Err": None,
                "Trend_Type": "Insufficient Observations",
                "Status": reg['status']
            })
            
    df_res = pd.DataFrame(results)
    df_res['Linear_Slope_per_Year'] = df_res['Slope']
    df_res['N_Observations'] = df_res['N']
    df_res['Fitted_Trajectory'] = df_res['Trend_Type']
    return df_res

def compute_cagr(start_val, end_val, num_years):
    """
    Calculates Compound Annual Growth Rate (CAGR).
    CAGR = (End / Start) ** (1 / n) - 1
    """
    if start_val is None or end_val is None or num_years <= 0 or start_val <= 0:
        return None
    try:
        cagr = ((end_val / start_val) ** (1.0 / num_years)) - 1.0
        return float(cagr * 100.0)
    except:
        return None

def compute_correlation_matrix(clean_df):
    """
    Computes Pearson and Spearman correlation matrices across numeric panel columns.
    """
    numeric_cols = ['Accidents', 'Fatalities']
    if 'Fatalities_per_100_Accidents_calc' in clean_df.columns:
        numeric_cols.append('Fatalities_per_100_Accidents_calc')
    if 'Injured' in clean_df.columns and pd.to_numeric(clean_df['Injured'], errors='coerce').notnull().sum() > 50:
        numeric_cols.append('Injured_num')

    sub = clean_df[numeric_cols].apply(pd.to_numeric, errors='coerce').dropna()
    
    if sub.empty or len(sub) < 5:
        return {"pearson": {}, "spearman": {}, "n": 0}
        
    pearson = sub.corr(method='pearson').round(3).to_dict()
    spearman = sub.corr(method='spearman').round(3).to_dict()
    
    return {
        "pearson": pearson,
        "spearman": spearman,
        "n": len(sub)
    }

def compute_time_to_threshold(clean_df, threshold=10000):
    """
    Determines the earliest year in which a state reached or surpassed the given crash threshold.
    """
    df = clean_df.sort_values(['State_UT', 'Year'])
    exceeded = df[df['Accidents'] >= threshold]
    
    first_reached = exceeded.groupby('State_UT').first().reset_index()
    results = []
    for _, r in first_reached.iterrows():
        results.append({
            "State_UT": r['State_UT'],
            "Earliest_Year_Reached": int(r['Year']),
            "Accidents_At_Arrival": int(r['Accidents'])
        })
    return sorted(results, key=lambda x: (x['Earliest_Year_Reached'], -x['Accidents_At_Arrival']))
