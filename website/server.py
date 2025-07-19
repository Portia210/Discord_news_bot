from flask import Flask, render_template
import os
import threading
import time
from werkzeug.serving import make_server
import queue
from utils.logger import logger

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/health')
def health():
    return {'status': 'healthy'}, 200

def start_web_server(host='0.0.0.0', port=5000, debug=False):
    """Start the Flask web server in a background thread"""
    def run_server():
        try:
            server = make_server(host, port, app)
            logger.info(f"🌐 Flask server starting on http://{host}:{port}")
            server.serve_forever()
        except Exception as e:
            logger.error(f"Flask server error: {e}")
    
    # Create and start the thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    return server_thread

if __name__ == '__main__':
    # Development server - only run when script is executed directly
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False) 