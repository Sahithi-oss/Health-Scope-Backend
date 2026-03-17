"""
Insights Service Module
-----------------------
Generates intelligent insights, trend analysis, and comparison
reports for disease data. Provides risk assessments and recommendations.
"""

from services.covid_service import get_covid_data
from services.disease_service import get_disease_data, is_supported_disease


def _get_data_for_disease(disease_name):
    """
    Unified data fetcher that routes to the correct service.
    
    Args:
        disease_name (str): Disease name (covid, tb, dengue, malaria)
    
    Returns:
        dict or None: Disease data dictionary
    """
    key = disease_name.lower().strip()

    if key in ("covid", "covid-19", "covid19"):
        return get_covid_data()
    elif is_supported_disease(key):
        return get_disease_data(key)
    else:
        return None


def generate_insights(disease_name):
    """
    Generate comprehensive insights for a specific disease.
    
    Includes trend analysis, risk assessment, key metrics,
    and public health recommendations.
    
    Args:
        disease_name (str): Name of the disease
    
    Returns:
        dict: Insights report with analysis and recommendations
    """
    data = _get_data_for_disease(disease_name)

    if data is None:
        return {
            "error": f"Disease '{disease_name}' not found. Supported diseases: covid, tb, dengue, malaria"
        }

    if "error" in data:
        return data

    stats = data.get("statistics", {})
    total_cases = stats.get("total_cases", 0)
    deaths = stats.get("deaths", 0)
    recovered = stats.get("recovered", 0)
    risk_level = stats.get("risk_level", "Unknown")
    trend = stats.get("trend", "unknown")

    # Get percentage change (use whichever is available)
    pct_change = stats.get("percentage_change_3m", stats.get("percentage_change_30d", 0))

    # Mortality and recovery rates
    mortality_rate = round((deaths / total_cases) * 100, 2) if total_cases > 0 else 0
    recovery_rate = round((recovered / total_cases) * 100, 2) if total_cases > 0 else 0

    # Generate trend analysis text
    if trend == "increasing":
        if pct_change > 20:
            trend_analysis = (
                f"{data['disease']} cases are rising sharply with a {pct_change}% increase. "
                f"This indicates a potential outbreak situation requiring immediate attention."
            )
        elif pct_change > 5:
            trend_analysis = (
                f"{data['disease']} cases show a moderate increase of {pct_change}%. "
                f"Enhanced monitoring and preventive measures are recommended."
            )
        else:
            trend_analysis = (
                f"{data['disease']} cases show a slight upward trend of {pct_change}%. "
                f"Continued surveillance is advised."
            )
    elif trend == "decreasing":
        trend_analysis = (
            f"{data['disease']} cases are declining with a {abs(pct_change)}% decrease. "
            f"Current intervention strategies appear to be effective."
        )
    else:
        trend_analysis = (
            f"{data['disease']} cases remain relatively stable. "
            f"Baseline monitoring should continue."
        )

    # Generate risk assessment
    risk_descriptions = {
        "High": (
            "CRITICAL: Significant case increase detected. Immediate public health intervention "
            "recommended. Consider activating emergency response protocols."
        ),
        "Medium": (
            "WARNING: Moderate case increase observed. Enhanced surveillance and targeted "
            "intervention measures should be implemented."
        ),
        "Low": (
            "STABLE: Disease activity is within expected levels. Continue routine monitoring "
            "and standard prevention protocols."
        )
    }

    # Generate recommendations based on risk level
    recommendations = _generate_recommendations(data["disease"], risk_level, trend, pct_change)

    return {
        "disease": data["disease"],
        "source": data.get("source", "Unknown"),
        "data_type": data.get("data_type", "unknown"),
        "generated_at": __import__("datetime").datetime.utcnow().isoformat() + "Z",
        "summary": {
            "total_cases": total_cases,
            "deaths": deaths,
            "recovered": recovered,
            "mortality_rate": mortality_rate,
            "recovery_rate": recovery_rate
        },
        "trend_analysis": {
            "direction": trend,
            "percentage_change": pct_change,
            "description": trend_analysis
        },
        "risk_assessment": {
            "level": risk_level,
            "description": risk_descriptions.get(risk_level, "Unknown risk level"),
            "percentage_change": pct_change
        },
        "recommendations": recommendations
    }


def _generate_recommendations(disease, risk_level, trend, pct_change):
    """Generate public health recommendations based on disease metrics."""
    recommendations = []

    # Risk-level based recommendations
    if risk_level == "High":
        recommendations.extend([
            "Activate emergency response protocols",
            "Increase testing and surveillance capacity",
            "Issue public health advisories",
            "Coordinate with healthcare facilities for surge capacity",
            "Deploy rapid response teams to hotspot areas"
        ])
    elif risk_level == "Medium":
        recommendations.extend([
            "Enhance disease surveillance in affected areas",
            "Increase public awareness campaigns",
            "Ensure adequate medical supply stockpiles",
            "Monitor for potential outbreak escalation"
        ])
    else:
        recommendations.extend([
            "Continue routine surveillance and monitoring",
            "Maintain current prevention protocols",
            "Conduct periodic risk assessments"
        ])

    # Disease-specific recommendations
    disease_lower = disease.lower()
    if "covid" in disease_lower:
        recommendations.append("Promote vaccination and booster programs")
        recommendations.append("Encourage respiratory hygiene and mask usage in high-risk settings")
    elif "tb" in disease_lower or "tuberculosis" in disease_lower:
        recommendations.append("Screen high-risk populations (immunocompromised, close contacts)")
        recommendations.append("Ensure completion of treatment regimens to prevent drug resistance")
    elif "dengue" in disease_lower:
        recommendations.append("Implement vector control measures (mosquito breeding site elimination)")
        recommendations.append("Distribute mosquito nets and repellents in endemic areas")
    elif "malaria" in disease_lower:
        recommendations.append("Distribute insecticide-treated bed nets")
        recommendations.append("Ensure availability of antimalarial medications")
        recommendations.append("Implement indoor residual spraying programs")

    return recommendations


def compare_diseases(disease1_name, disease2_name):
    """
    Compare two diseases side-by-side with relative analysis.
    
    Args:
        disease1_name (str): First disease name
        disease2_name (str): Second disease name
    
    Returns:
        dict: Comparison report with both diseases' data and relative analysis
    """
    data1 = _get_data_for_disease(disease1_name)
    data2 = _get_data_for_disease(disease2_name)

    errors = []
    if data1 is None:
        errors.append(f"Disease '{disease1_name}' not found")
    if data2 is None:
        errors.append(f"Disease '{disease2_name}' not found")

    if errors:
        return {
            "error": ". ".join(errors) + ". Supported diseases: covid, tb, dengue, malaria"
        }

    if "error" in data1:
        return data1
    if "error" in data2:
        return data2

    stats1 = data1.get("statistics", {})
    stats2 = data2.get("statistics", {})

    # Extract metrics for comparison
    cases1 = stats1.get("total_cases", 0)
    cases2 = stats2.get("total_cases", 0)
    deaths1 = stats1.get("deaths", 0)
    deaths2 = stats2.get("deaths", 0)
    risk1 = stats1.get("risk_level", "Unknown")
    risk2 = stats2.get("risk_level", "Unknown")
    trend1 = stats1.get("trend", "unknown")
    trend2 = stats2.get("trend", "unknown")
    pct1 = stats1.get("percentage_change_3m", stats1.get("percentage_change_30d", 0))
    pct2 = stats2.get("percentage_change_3m", stats2.get("percentage_change_30d", 0))

    # Mortality rates
    mort1 = round((deaths1 / cases1) * 100, 2) if cases1 > 0 else 0
    mort2 = round((deaths2 / cases2) * 100, 2) if cases2 > 0 else 0

    # Determine which disease is more severe
    risk_order = {"High": 3, "Medium": 2, "Low": 1, "Unknown": 0}
    higher_risk = data1["disease"] if risk_order.get(risk1, 0) >= risk_order.get(risk2, 0) else data2["disease"]

    # Generate comparison summary
    comparison_summary = (
        f"Comparing {data1['disease']} and {data2['disease']}: "
        f"{data1['disease']} has {cases1:,} total cases with a {mort1}% mortality rate, "
        f"while {data2['disease']} has {cases2:,} total cases with a {mort2}% mortality rate. "
        f"{higher_risk} currently poses a higher risk level."
    )

    return {
        "comparison": {
            "generated_at": __import__("datetime").datetime.utcnow().isoformat() + "Z",
            "summary": comparison_summary,
            "diseases": {
                data1["disease"]: {
                    "source": data1.get("source", "Unknown"),
                    "data_type": data1.get("data_type", "unknown"),
                    "total_cases": cases1,
                    "deaths": deaths1,
                    "mortality_rate": mort1,
                    "percentage_change": pct1,
                    "trend": trend1,
                    "risk_level": risk1,
                    "time_series": data1.get("time_series", [])
                },
                data2["disease"]: {
                    "source": data2.get("source", "Unknown"),
                    "data_type": data2.get("data_type", "unknown"),
                    "total_cases": cases2,
                    "deaths": deaths2,
                    "mortality_rate": mort2,
                    "percentage_change": pct2,
                    "trend": trend2,
                    "risk_level": risk2,
                    "time_series": data2.get("time_series", [])
                }
            },
            "relative_analysis": {
                "higher_cases": data1["disease"] if cases1 > cases2 else data2["disease"],
                "higher_mortality": data1["disease"] if mort1 > mort2 else data2["disease"],
                "higher_risk": higher_risk,
                "case_ratio": round(cases1 / cases2, 2) if cases2 > 0 else "N/A",
                "mortality_difference": round(abs(mort1 - mort2), 2)
            }
        }
    }
