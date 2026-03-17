"""
Disease Service Module
----------------------
Handles loading and processing of historical disease datasets (TB, Dengue, Malaria)
from CSV files. Provides aggregated statistics, time-series data, and risk classification.
"""

import os
import pandas as pd
from datetime import datetime


# Base path for data files
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

# Mapping of disease names to their CSV files
DISEASE_FILES = {
    "tb": "tb_data.csv",
    "tuberculosis": "tb_data.csv",
    "dengue": "dengue_data.csv",
    "malaria": "malaria_data.csv"
}

# Disease display names
DISEASE_NAMES = {
    "tb": "Tuberculosis (TB)",
    "tuberculosis": "Tuberculosis (TB)",
    "dengue": "Dengue",
    "malaria": "Malaria"
}


def load_disease_data(disease_name):
    """
    Load disease data from CSV file and return as a pandas DataFrame.
    
    Args:
        disease_name (str): Name of the disease (tb, dengue, malaria)
    
    Returns:
        pd.DataFrame or None: DataFrame with disease data, or None if not found.
    """
    disease_key = disease_name.lower().strip()

    if disease_key not in DISEASE_FILES:
        return None

    file_path = os.path.join(DATA_DIR, DISEASE_FILES[disease_key])

    if not os.path.exists(file_path):
        return None

    try:
        df = pd.read_csv(file_path)
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").reset_index(drop=True)
        return df
    except Exception as e:
        print(f"Error loading {disease_name} data: {e}")
        return None


def calculate_percentage_change(df, periods=3):
    """
    Calculate percentage change in cases over the specified number of recent periods.
    
    Args:
        df (pd.DataFrame): Disease data with 'cases' column
        periods (int): Number of periods to look back for comparison
    
    Returns:
        tuple: (percentage_change, trend_direction)
    """
    if df is None or len(df) < periods + 1:
        return 0.0, "insufficient_data"

    recent_cases = df.iloc[-1]["cases"]
    older_cases = df.iloc[-(periods + 1)]["cases"]

    if older_cases == 0:
        return 0.0, "stable"

    pct_change = round(((recent_cases - older_cases) / older_cases) * 100, 2)

    if pct_change > 0:
        trend = "increasing"
    elif pct_change < 0:
        trend = "decreasing"
    else:
        trend = "stable"

    return pct_change, trend


def classify_risk_level(percentage_change):
    """
    Classify risk level based on percentage change.
    
    - High: >20% increase
    - Medium: 5–20% increase
    - Low: <5% increase or stable/decreasing
    
    Args:
        percentage_change (float): Percentage change in cases
    
    Returns:
        str: Risk level classification
    """
    if percentage_change > 20:
        return "High"
    elif percentage_change >= 5:
        return "Medium"
    else:
        return "Low"


def get_disease_data(disease_name):
    """
    Get complete processed data for a historical disease.
    
    Args:
        disease_name (str): Name of the disease
    
    Returns:
        dict: Complete disease data with statistics, time-series, and risk level
    """
    disease_key = disease_name.lower().strip()
    
    if disease_key not in DISEASE_FILES:
        return None

    df = load_disease_data(disease_key)
    if df is None:
        return {"error": f"Failed to load data for {disease_name}"}

    # Build time-series
    time_series = []
    for _, row in df.iterrows():
        time_series.append({
            "date": row["date"].strftime("%Y-%m-%d"),
            "cases": int(row["cases"]),
            "deaths": int(row["deaths"]),
            "recovered": int(row["recovered"])
        })

    # Calculate statistics
    total_cases = int(df["cases"].iloc[-1])
    total_deaths = int(df["deaths"].iloc[-1])
    total_recovered = int(df["recovered"].iloc[-1])

    # Percentage change (last 3 months)
    pct_change, trend = calculate_percentage_change(df, periods=3)
    risk_level = classify_risk_level(pct_change)

    # Year-over-year comparison (last 12 months vs previous 12)
    yoy_change = 0.0
    if len(df) >= 24:
        current_year_cases = df.iloc[-1]["cases"]
        prev_year_cases = df.iloc[-13]["cases"]
        if prev_year_cases > 0:
            yoy_change = round(
                ((current_year_cases - prev_year_cases) / prev_year_cases) * 100, 2
            )

    display_name = DISEASE_NAMES.get(disease_key, disease_name.title())

    return {
        "disease": display_name,
        "source": f"Historical Dataset ({DISEASE_FILES[disease_key]})",
        "data_type": "historical",
        "time_series": time_series,
        "statistics": {
            "total_cases": total_cases,
            "deaths": total_deaths,
            "recovered": total_recovered,
            "mortality_rate": round((total_deaths / total_cases) * 100, 2) if total_cases > 0 else 0,
            "recovery_rate": round((total_recovered / total_cases) * 100, 2) if total_cases > 0 else 0,
            "percentage_change_3m": pct_change,
            "year_over_year_change": yoy_change,
            "trend": trend,
            "risk_level": risk_level,
            "data_points": len(df),
            "date_range": {
                "start": df["date"].iloc[0].strftime("%Y-%m-%d"),
                "end": df["date"].iloc[-1].strftime("%Y-%m-%d")
            }
        }
    }


def get_supported_diseases():
    """Return list of supported historical diseases."""
    return ["tb", "dengue", "malaria"]


def is_supported_disease(disease_name):
    """Check if a disease name is supported for historical data."""
    return disease_name.lower().strip() in DISEASE_FILES
