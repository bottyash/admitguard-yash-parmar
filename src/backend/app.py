"""
AdmitGuard — Flask Application Entry Point
Sprint 1: Core Backend with Strict Validation

Run with: python app.py
Server starts at http://localhost:5000
"""

from flask import Flask, jsonify
from flask_cors import CORS
from routes.candidates import candidates_bp


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Enable CORS for frontend access
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register blueprints
    app.register_blueprint(candidates_bp)

    # Health check endpoint
    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify({
            "status": "healthy",
            "version": "1.0.0",
            "sprint": 1,
            "description": "AdmitGuard — Admission Data Validation API"
        }), 200

    return app


if __name__ == "__main__":
    app = create_app()
    print("=" * 60)
    print("  AdmitGuard API — Sprint 1")
    print("  Server running at http://localhost:5000")
    print("  Endpoints:")
    print("    POST /api/validate          — Validate all fields")
    print("    POST /api/validate/<field>   — Validate single field")
    print("    POST /api/candidates         — Submit candidate")
    print("    GET  /api/candidates         — List all candidates")
    print("    GET  /api/candidates/<id>    — Get candidate by ID")
    print("    GET  /api/health             — Health check")
    print("=" * 60)
    app.run(debug=True, port=5000)
