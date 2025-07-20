from flask import Blueprint, request, jsonify
import os
from datetime import datetime
from utils.logger import logger
from utils.read_write import read_json_file, write_json_file
from functools import wraps
from config import Config


# Create Blueprint for API routes
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Simple auth decorator
def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        expected = os.environ.get('API_TOKEN', 'your-secret-token')
        
        if token != expected:
            logger.warning("⚠️ Invalid auth token")
            return {'error': 'Unauthorized'}, 401
            
        return f(*args, **kwargs)
    return decorated_function

@api_bp.route('/news-report', methods=['POST'])
@require_auth
def create_news_report():
    """Create news report with JSON data (authenticated endpoint)"""
    try:
        data = request.get_json()
        logger.info("📰 Creating news report with provided data")
        
        # Validate required fields
        if 'news_data' not in data:
            return {'error': 'Missing required field: news_data'}, 400
        
        # Create data directory if it doesn't exist
        
        os.makedirs(Config.DATA_DIR, exist_ok=True)
        
        # Generate date from current time or use provided date
        date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        # Prepare the complete data structure
        news_data = {
            'date': date,
            'title': data.get('title', f'דוח חדשות פיננסיות - {date}'),
            'report_title': data.get('report_title', 'דוח חדשות'),
            'report_subtitle': data.get('report_subtitle', 'עדכוני שוק ופיננסים אחרונים'),
            'report_time': data.get('report_time', 'auto'),
            'generation_time': data.get('generation_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            'news_data': data['news_data'],
            'price_symbols': data.get('price_symbols', [])
        }
        
        # Save to file
        filename = f'news_report_{date}.json'
        filepath = os.path.join(Config.DATA_DIR, filename)
        
        success = write_json_file(filepath, news_data)
        if success:
            logger.info(f"✅ News report saved for date {date}")
            return {
                'status': 'success',
                'message': f'News report created for date {date}',
                'file': filename,
                'date': date,
                'link_to_report': f'http://{Config.SERVER.CURRENT_SERVER_IP}:{Config.SERVER.PORT}/news-report/{date}'
            }, 201
        else:
            logger.error(f"❌ Failed to save news report for date {date}")
            return {'error': 'Failed to save news report'}, 500
            
    except Exception as e:
        logger.error(f"❌ Error creating news report: {e}")
        return {'error': 'Failed to create news report', 'details': str(e)}, 500


@api_bp.route('/bot-status', methods=['POST'])
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

@api_bp.route('/analytics', methods=['GET'])
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