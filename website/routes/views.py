from flask import Blueprint, render_template
import os
from utils.logger import logger
from utils.read_write import read_json_file
from config import Config

# Create Blueprint for view routes
views_bp = Blueprint('views', __name__)

@views_bp.route('/')
def home():
    """Home page route"""
    logger.info("🏠 Home page requested")
    return render_template('index.html')

@views_bp.route('/health')
def health():
    """Health check endpoint"""
    logger.info("💚 Health check requested")
    return {'status': 'healthy'}, 200

@views_bp.route('/news-report')
def news_report():
    """News report page with sample data from sample_news.json"""
    logger.info("📰 News report requested (sample data)")
    
    sample_data = read_json_file('sample_news_report.json')
    if sample_data is None:
        return {'error': 'Sample news data not found'}, 404
    
    return render_template('news_report.html', **sample_data)

@views_bp.route('/<report_time>-news-report/<date>')
def news_report_by_date(report_time, date):
    """Display news report for a specific date"""
    try:
        # Look for the file in data directory
        data_dir = Config.DATA_DIR
        filename = f'{report_time}_news_report_{date}.json'
        filepath = os.path.join(data_dir, filename)
        
        if os.path.exists(filepath):
            news_data = read_json_file(filepath)
            if news_data:
                logger.info(f"📰 Displaying news report for date {date}")
                return render_template('news_report.html', **news_data)
            else:
                logger.warning(f"⚠️ Failed to read news data for date {date}")
                return {'error': 'Failed to read news data'}, 500
        else:
            logger.warning(f"⚠️ News report not found for date {date}")
            return {'error': f'News report not found for date {date}'}, 404
            
    except Exception as e:
        logger.error(f"❌ Error displaying news report for date {date}: {e}")
        return {'error': 'Failed to display news report', 'details': str(e)}, 500 