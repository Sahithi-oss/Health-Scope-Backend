"""
HealthScope - Backend Server
===========================

A Flask-based backend system that integrates real-time COVID-19 data
with historical datasets for Tuberculosis, Dengue, and Malaria.

Features:
    - Real-time COVID-19 data fetching via disease.sh API
    - Historical disease data loading from CSV datasets
    - Trend analysis and risk classification
    - Disease comparison capabilities
    - RESTful API endpoints

Usage:
    python app.py
    
    Server runs on http://localhost:5001
"""

import os
import sys

# Ensure project root is in Python path for module imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_cors import CORS
from routes.api_routes import api_bp


def create_app():
    """
    Application factory - creates and configures the Flask application.
    
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Enable CORS for all routes (allows frontend integration)
    CORS(app)
    
    # Configuration
    app.config["JSON_SORT_KEYS"] = False
    
    # Register API blueprint
    app.register_blueprint(api_bp)
    
    return app


if __name__ == "__main__":
    app = create_app()
    
    print("=" * 40)
    print("  HealthScope - Backend Server")
    print("=" * 40)
    print()
    print("  Server starting on http://localhost:5001")
    print()
    print("  Available endpoints:")
    print("    GET /                                    - API Documentation")
    print("    GET /getData?disease=<name>              - Disease Data")
    print("    GET /getInsights?disease=<name>          - Disease Insights")
    print("    GET /compare?disease1=<x>&disease2=<y>   - Compare Diseases")
    print()
    print("  Supported diseases: covid, tb, dengue, malaria")
    print("=" * 60)
    
    app.run(debug=True, host="0.0.0.0", port=5001)
