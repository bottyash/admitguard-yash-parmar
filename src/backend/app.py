"""
AdmitGuard — Flask Application Entry Point
Sprint 3+: Strict + Soft Rules + Frontend + SQLite Database

Run with: python app.py
  API + Frontend at: http://localhost:5000
"""

import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from routes.candidates import candidates_bp
from db import init_db

# Resolve path to frontend directory (../frontend relative to backend/)
FRONTEND_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "frontend")
)


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")

    # Initialize SQLite database (creates tables on first run)
    init_db()

    # Enable CORS for all API routes
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register API blueprints
    app.register_blueprint(candidates_bp)

    # Health check endpoint
    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify({
            "status": "healthy",
            "version": "3.1.0",
            "sprint": "3+",
            "storage": "SQLite",
            "description": "AdmitGuard — Admission Data Validation API"
        }), 200

    # Serve frontend (index.html at root and any static assets)
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_frontend(path):
        if path and os.path.exists(os.path.join(FRONTEND_DIR, path)):
            return send_from_directory(FRONTEND_DIR, path)
        return send_from_directory(FRONTEND_DIR, "index.html")

    return app


if __name__ == "__main__":
    import signal
    import sys

    def handle_exit(sig, frame):
        """Ensure the server exits cleanly with no background processes."""
        print("\n  Shutting down AdmitGuard server...")
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    app = create_app()
    print("=" * 60)
    print("  AdmitGuard — Sprint 3")
    print("  Frontend + API at: http://localhost:5000")
    print("  Endpoints:")
    print("    GET  /                       — Frontend UI")
    print("    POST /api/validate           — Validate all fields")
    print("    POST /api/validate/<field>   — Validate single field")
    print("    POST /api/candidates         — Submit candidate")
    print("    GET  /api/candidates         — List all candidates")
    print("    GET  /api/audit-log          — Audit log")
    print("    GET  /api/dashboard          — Dashboard stats")
    print("    GET  /api/health             — Health check")
    print("  Press Ctrl+C to stop the server cleanly.")
    print("=" * 60)
    app.run(debug=True, port=5000, use_reloader=False)
