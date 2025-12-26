#!/usr/bin/env python3
"""
Production startup script for Baja 1000 Chassis Optimizer
Uses Werkzeug production server (or can be used with gunicorn)
"""

import os
from app import app

if __name__ == '__main__':
    # Ensure outputs directory exists
    os.makedirs('outputs', exist_ok=True)
    
    # Production configuration
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    
    print("=" * 60)
    print("Baja 1000 Chassis Optimizer - Production Mode")
    print("=" * 60)
    print(f"Starting server on {host}:{port}")
    print("Access the application at: http://localhost:{port}")
    print("")
    print("To stop the server, press Ctrl+C")
    print("=" * 60)
    
    # Run with production settings
    from werkzeug.serving import run_simple
    run_simple(host, port, app, use_reloader=False, use_debugger=False)
