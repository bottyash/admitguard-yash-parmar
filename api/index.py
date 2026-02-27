"""
AdmitGuard — Vercel Serverless Entrypoint
Vercel looks for `app` in api/index.py
"""

import sys
import os

# Add the backend directory to Python path so all imports work
BACKEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "backend")
sys.path.insert(0, BACKEND_DIR)

from app import create_app

app = create_app()
