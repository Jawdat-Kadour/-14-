#!/usr/bin/env python3
"""
Simple HTTP server to run the interactive network visualization.
This script starts a local web server so you can view the application in your browser.
"""

import http.server
import socketserver
import webbrowser
import os
import sys

PORT = 8000


class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers to allow local file access
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()


def main():
    # Check if data file exists
    if not os.path.exists("governorate_networks.json"):
        print("⚠️  Warning: governorate_networks.json not found!")
        print("   Running process_data.py to generate it...")
        import subprocess

        result = subprocess.run(
            [sys.executable, "process_data.py"], capture_output=True, text=True
        )
        if result.returncode != 0:
            print("❌ Error processing data:")
            print(result.stderr)
            return
        print("✅ Data processed successfully!")

    # Start server
    handler = MyHTTPRequestHandler

    try:
        with socketserver.TCPServer(("", PORT), handler) as httpd:
            url = f"http://localhost:{PORT}/index.html"
            print(f"\n{'='*60}")
            print(f"🚀 Server started successfully!")
            print(f"{'='*60}")
            print(f"📊 Open your browser and navigate to:")
            print(f"   {url}")
            print(f"\n💡 Press Ctrl+C to stop the server")
            print(f"{'='*60}\n")

            # Try to open browser automatically
            try:
                webbrowser.open(url)
            except:
                pass

            httpd.serve_forever()

    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Goodbye!")
    except OSError as e:
        if e.errno == 98 or e.errno == 48:  # Address already in use
            print(f"\n❌ Port {PORT} is already in use!")
            print(
                f"   Please close the application using that port or change PORT in this script."
            )
        else:
            print(f"\n❌ Error starting server: {e}")


if __name__ == "__main__":
    main()
