#!/usr/bin/env python3
"""
IDWeek 2025 PWA - Simple Development Server
Serves the PWA for local testing and development
"""

import http.server
import socketserver
import os
import json
import urllib.parse
from datetime import datetime

class PWAHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.dirname(os.path.abspath(__file__)), **kwargs)
    
    def end_headers(self):
        # Add PWA-friendly headers
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        
        # CORS headers for development
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        
        # Service Worker headers
        if self.path.endswith('sw.js'):
            self.send_header('Service-Worker-Allowed', '/')
            self.send_header('Content-Type', 'application/javascript')
        
        super().end_headers()
    
    def do_GET(self):
        # Handle root path
        if self.path == '/':
            self.path = '/index.html'
        
        # Handle API requests
        elif self.path.startswith('/api/'):
            self.handle_api_request()
            return
        
        # Serve static files
        super().do_GET()
    
    def handle_api_request(self):
        """Handle API requests for PWA functionality"""
        try:
            if self.path == '/api/sessions':
                self.serve_sessions_data()
            elif self.path == '/api/health':
                self.serve_health_check()
            else:
                self.send_error(404, "API endpoint not found")
        except Exception as e:
            print(f"API Error: {e}")
            self.send_error(500, "Internal server error")
    
    def serve_sessions_data(self):
        """Serve session data from the validated Firecrawl results"""
        try:
            data_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'batch1_firecrawl_validated.json')
            if os.path.exists(data_file):
                with open(data_file, 'r', encoding='utf-8') as f:
                    data = f.read()
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(data.encode('utf-8'))
            else:
                # Return empty array if no data file
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(b'[]')
        except Exception as e:
            print(f"Error serving sessions data: {e}")
            self.send_error(500, "Failed to load session data")
    
    def serve_health_check(self):
        """Serve health check for PWA status"""
        health_data = {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "services": {
                "pwa": "running",
                "data": "available" if os.path.exists(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'batch1_firecrawl_validated.json')) else "missing"
            }
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(health_data).encode('utf-8'))
    
    def log_message(self, format, *args):
        # Custom logging for PWA requests
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {format % args}")

def main():
    PORT = 8080
    
    print(f"🚀 IDWeek 2025 PWA Development Server")
    print(f"=" * 50)
    print(f"📱 PWA URL: http://localhost:{PORT}")
    print(f"🔧 API Health: http://localhost:{PORT}/api/health")
    print(f"📊 API Sessions: http://localhost:{PORT}/api/sessions")
    print(f"⚠️  Press Ctrl+C to stop server")
    print(f"=" * 50)
    
    try:
        with socketserver.TCPServer(("", PORT), PWAHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print(f"\n🛑 Server stopped")
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ Port {PORT} is already in use")
            print(f"💡 Try running: lsof -ti:{PORT} | xargs kill -9")
        else:
            print(f"❌ Server error: {e}")

if __name__ == "__main__":
    main()