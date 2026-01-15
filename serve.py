#!/usr/bin/env python3
"""
Simple HTTP server to test the visualization locally.
Pointing to the 'dashboard' directory.
"""

import http.server
import socketserver
import os
import sys

PORT = 8000

# 1. Calculate the path to the 'dashboard' directory
# (Assumes 'dashboard' is in the same folder as this script)
base_dir = os.path.dirname(os.path.abspath(__file__))
target_dir = os.path.join(base_dir, "dashboard")

# 2. Check if the directory exists before trying to serve it
if not os.path.exists(target_dir):
    print(f"Error: The directory '{target_dir}' does not exist.")
    print("Please make sure you have created the 'dashboard' folder.")
    sys.exit(1)

# 3. Change the working directory to the dashboard folder
os.chdir(target_dir)

Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving visualization from: {target_dir}")
    print(f"URL: http://localhost:{PORT}")
    print("Press Ctrl+C to stop")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        httpd.server_close()