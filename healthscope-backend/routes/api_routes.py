"""
API Routes Module
-----------------
Defines all REST API endpoints for the Disease Surveillance Dashboard.

Endpoints:
    GET /getData?disease=<name>     - Retrieve disease data and statistics
    GET /getInsights?disease=<name> - Get trend analysis and recommendations
    GET /compare?disease1=<name>&disease2=<name> - Compare two diseases
"""

from flask import Blueprint, request, jsonify
from services.covid_service import get_covid_data
from services.disease_service import get_disease_data, is_supported_disease
from services.insights_service import generate_insights, compare_diseases


api_bp = Blueprint("api", __name__)

SUPPORTED_DISEASES = ["covid", "tb", "dengue", "malaria"]


@api_bp.route("/getData", methods=["GET"])
def get_data():
    """
    Retrieve disease data including total cases, deaths, time-series,
    percentage change, and risk level.
    
    Query Parameters:
        disease (str): Name of the disease (covid, tb, dengue, malaria)
    
    Returns:
        JSON response with structured disease data
    """
    disease = request.args.get("disease", "").strip().lower()

    if not disease:
        return jsonify({
            "error": "Missing required parameter: 'disease'",
            "usage": "/getData?disease=<name>",
            "supported_diseases": SUPPORTED_DISEASES
        }), 400

    # Route to the correct data source
    if disease in ("covid", "covid-19", "covid19"):
        data = get_covid_data()
    elif is_supported_disease(disease):
        data = get_disease_data(disease)
    else:
        return jsonify({
            "error": f"Disease '{disease}' is not supported",
            "supported_diseases": SUPPORTED_DISEASES
        }), 404

    if data and "error" in data:
        return jsonify(data), 500

    return jsonify({
        "status": "success",
        "data": data
    })


@api_bp.route("/getInsights", methods=["GET"])
def get_insights():
    """
    Generate intelligent insights for a specific disease including
    trend analysis, risk assessment, and recommendations.
    
    Query Parameters:
        disease (str): Name of the disease (covid, tb, dengue, malaria)
    
    Returns:
        JSON response with insights, trends, and recommendations
    """
    disease = request.args.get("disease", "").strip().lower()

    if not disease:
        return jsonify({
            "error": "Missing required parameter: 'disease'",
            "usage": "/getInsights?disease=<name>",
            "supported_diseases": SUPPORTED_DISEASES
        }), 400

    insights = generate_insights(disease)

    if "error" in insights:
        return jsonify(insights), 404

    return jsonify({
        "status": "success",
        "insights": insights
    })


@api_bp.route("/compare", methods=["GET"])
def compare():
    """
    Compare two diseases side-by-side with relative analysis.
    
    Query Parameters:
        disease1 (str): First disease name
        disease2 (str): Second disease name
    
    Returns:
        JSON response with comparison data and relative analysis
    """
    disease1 = request.args.get("disease1", "").strip().lower()
    disease2 = request.args.get("disease2", "").strip().lower()

    if not disease1 or not disease2:
        missing = []
        if not disease1:
            missing.append("disease1")
        if not disease2:
            missing.append("disease2")
        return jsonify({
            "error": f"Missing required parameter(s): {', '.join(missing)}",
            "usage": "/compare?disease1=<name>&disease2=<name>",
            "supported_diseases": SUPPORTED_DISEASES
        }), 400

    if disease1 == disease2:
        return jsonify({
            "error": "Cannot compare a disease with itself. Please provide two different diseases.",
            "supported_diseases": SUPPORTED_DISEASES
        }), 400

    result = compare_diseases(disease1, disease2)

    if "error" in result:
        return jsonify(result), 404

    return jsonify({
        "status": "success",
        **result
    })


@api_bp.route("/", methods=["GET"])
def index():
    """API root endpoint with documentation."""
    return jsonify({
        "title": "HealthScope API",
        "version": "1.0.0",
        "description": "Backend API for HealthScope real-time and historical disease surveillance",
        "endpoints": {
            "GET /getData?disease=<name>": {
                "description": "Retrieve disease data with statistics and time-series",
                "parameters": {"disease": "covid | tb | dengue | malaria"},
                "response": "Total cases, deaths, time-series, percentage change, risk level"
            },
            "GET /getInsights?disease=<name>": {
                "description": "Get trend analysis, risk assessment, and recommendations",
                "parameters": {"disease": "covid | tb | dengue | malaria"},
                "response": "Trend analysis, risk classification, public health recommendations"
            },
            "GET /compare?disease1=<name>&disease2=<name>": {
                "description": "Compare two diseases side-by-side",
                "parameters": {
                    "disease1": "First disease name",
                    "disease2": "Second disease name"
                },
                "response": "Side-by-side comparison with relative analysis"
            }
        },
        "supported_diseases": SUPPORTED_DISEASES,
        "data_sources": {
            "covid": "disease.sh API (Real-Time)",
            "tb": "Historical Dataset (CSV)",
            "dengue": "Historical Dataset (CSV)",
            "malaria": "Historical Dataset (CSV)"
        }
    })
