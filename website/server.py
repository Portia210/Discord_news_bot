from flask import Flask, request
import os
from utils.logger import logger
# Register blueprints
from routes import register_all_blueprints

app = Flask(__name__)

# Add request logging middleware
@app.before_request
def log_request():
    """Log all incoming requests"""
    logger.info(f"📥 {request.method} {request.path} - IP: {request.remote_addr}")

@app.after_request
def log_response(response):
    """Log all outgoing responses"""
    logger.info(f"📤 {request.method} {request.path} - Status: {response.status_code}")
    return response

# Register all blueprints
register_all_blueprints(app)

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    logger.warning(f"⚠️ 404 Not Found: {request.path}")
    return {'error': 'Not found', 'path': request.path}, 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"❌ 500 Internal Server Error: {error}")
    return {'error': 'Internal server error'}, 500

if __name__ == '__main__':
    # Development server - only run when script is executed directly
    port = int(os.environ.get('PORT', 8000))
    
    logger.info(f"🚀 Starting Flask development server on port {port}")
    logger.info(f"🌐 Server will be available at: http://localhost:{port}")
    logger.info("📝 All requests and responses will be logged")
    
    app.run(debug=True, host='0.0.0.0', port=port, use_reloader=True) 