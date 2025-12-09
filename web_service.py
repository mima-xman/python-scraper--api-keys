"""
Web Service wrapper for Bytez API Key Scraper
Runs a Flask HTTP server to satisfy Render's Web Service requirements
while running the scraper in a background thread
"""

import asyncio
import threading
import os
import sys
import traceback
from flask import Flask, jsonify
from datetime import datetime
from core import BytezAPIKeyScraper

app = Flask(__name__)

# Global status tracking
scraper_status = {
    "status": "starting",
    "started_at": datetime.now().isoformat(),
    "keys_scraped": 0,
    "last_error": None,
    "last_success": None,
    "thread_alive": False
}

def run_scraper():
    """Run the scraper in the background"""
    global scraper_status
    
    print("=" * 60)
    print("SCRAPER THREAD STARTED")
    print("=" * 60)
    sys.stdout.flush()
    
    scraper_status["thread_alive"] = True
    
    async def scrape():
        try:
            print("Initializing scraper status to 'running'...")
            sys.stdout.flush()
            scraper_status["status"] = "running"
            
            print("Creating BytezAPIKeyScraper instance...")
            sys.stdout.flush()
            scraper = BytezAPIKeyScraper()
            
            print("Starting scraper.scrape_keys()...")
            sys.stdout.flush()
            await scraper.scrape_keys()
            
        except KeyboardInterrupt:
            scraper_status["status"] = "stopped"
            print("\n[SCRAPER] Stopped by user")
            sys.stdout.flush()
        except Exception as e:
            scraper_status["status"] = "error"
            scraper_status["last_error"] = str(e)
            error_trace = traceback.format_exc()
            print(f"\n[SCRAPER ERROR] {e}")
            print(f"[SCRAPER ERROR TRACEBACK]\n{error_trace}")
            sys.stdout.flush()
    
    try:
        # Run the async scraper
        print("Starting asyncio.run(scrape())...")
        sys.stdout.flush()
        asyncio.run(scrape())
    except Exception as e:
        scraper_status["status"] = "error"
        scraper_status["last_error"] = f"Asyncio error: {str(e)}"
        error_trace = traceback.format_exc()
        print(f"\n[ASYNCIO ERROR] {e}")
        print(f"[ASYNCIO ERROR TRACEBACK]\n{error_trace}")
        sys.stdout.flush()
    finally:
        scraper_status["thread_alive"] = False
        print("=" * 60)
        print("SCRAPER THREAD ENDED")
        print("=" * 60)
        sys.stdout.flush()

@app.route('/')
def home():
    """Health check endpoint"""
    return jsonify({
        "service": "Bytez API Key Scraper",
        "status": scraper_status["status"],
        "started_at": scraper_status["started_at"],
        "thread_alive": scraper_status["thread_alive"],
        "uptime": "running"
    })

@app.route('/health')
def health():
    """Health check for Render"""
    return jsonify({"status": "healthy"}), 200

@app.route('/status')
def status():
    """Get scraper status"""
    return jsonify(scraper_status)

if __name__ == '__main__':
    print("=" * 60)
    print("WEB SERVICE INITIALIZATION")
    print("=" * 60)
    
    # Get port from environment (Render provides this)
    port = int(os.environ.get('PORT', 10000))
    print(f"Port: {port}")
    
    # Check environment variables
    mongodb_url = os.environ.get('MONGODB_URL', 'NOT SET')
    mongodb_db = os.environ.get('MONGODB_DATABASE', 'NOT SET')
    print(f"MongoDB URL: {mongodb_url[:50]}..." if len(mongodb_url) > 50 else f"MongoDB URL: {mongodb_url}")
    print(f"MongoDB Database: {mongodb_db}")
    
    # Start scraper in background thread
    print("\nStarting scraper thread...")
    sys.stdout.flush()
    scraper_thread = threading.Thread(target=run_scraper, daemon=True)
    scraper_thread.start()
    print(f"Scraper thread started: {scraper_thread.is_alive()}")
    
    print(f"\nStarting Flask web service on port {port}...")
    print("=" * 60)
    sys.stdout.flush()
    
    # Run Flask app
    app.run(host='0.0.0.0', port=port)
