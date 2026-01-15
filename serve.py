#!/usr/bin/env python3
"""
Modified HTTP server for the dashboard.
Serves from the project root to ensure absolute paths (e.g., /dashboard/...) work,
while automatically redirecting the root URL to the dashboard.
"""

import http.server
import socketserver
import os
import sys

PORT = 8000

# 1. Calculate paths
# base_dir is the project root (where serve.py is located)
base_dir = os.path.dirname(os.path.abspath(__file__))
# target_dir is the actual folder we want to view
target_dir = os.path.join(base_dir, "dashboard")

if not os.path.exists(target_dir):
    print(f"Error: The directory '{target_dir}' does not exist.")
    sys.exit(1)

# 2. Custom Handler to handle the root redirect and serve from project root
class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # We tell the handler to use the project root as its base directory
        super().__init__(*args, directory=base_dir, **kwargs)

    def do_GET(self):
        # If the user hits the base URL (localhost:8000), redirect to the dashboard
        if self.path == '/' or self.path == '':
            self.send_response(301)
            self.send_header('Location', '/dashboard/')
            self.end_headers()
        else:
            # Otherwise, serve files normally from the project root
            super().do_GET()

# 3. Start the server
with socketserver.TCPServer(("", PORT), DashboardHandler) as httpd:
    print(f"Serving project from: {base_dir}")
    print(f"Dashboard URL: http://localhost:{PORT}/dashboard/")
    print("Press Ctrl+C to stop")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        httpd.server_close()