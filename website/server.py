from flask import Flask, render_template, request, jsonify
import os
from utils.logger import logger

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

@app.route('/')
def home():
    """Home page route"""
    logger.info("🏠 Home page requested")
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint"""
    logger.info("💚 Health check requested")
    return {'status': 'healthy'}, 200

# Add API endpoints for bot communication
@app.route('/api/bot-status', methods=['POST'])
def update_bot_status():
    """API endpoint for bot to update its status"""
    try:
        data = request.get_json()
        logger.info(f"🤖 Bot status update received: {data}")
        
        # TODO: Add database integration for storing bot status
        # For now, just log the data
        
        return {'status': 'updated', 'message': 'Bot status received'}, 200
    except Exception as e:
        logger.error(f"❌ Error updating bot status: {e}")
        return {'error': 'Failed to update status', 'details': str(e)}, 500

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """API endpoint to get bot analytics"""
    try:
        logger.info("📊 Analytics requested")
        
        # TODO: Add database integration for analytics
        analytics = {
            'status': 'online',
            'guilds': 0,
            'users': 0,
            'messages_today': 0,
            'uptime': '0h 0m'
        }
        
        logger.info(f"📊 Returning analytics: {analytics}")
        return analytics, 200
    except Exception as e:
        logger.error(f"❌ Error getting analytics: {e}")
        return {'error': 'Failed to get analytics', 'details': str(e)}, 500

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
    
    app.run(debug=True, host='0.0.0.0', port=port, use_reloader=False) 