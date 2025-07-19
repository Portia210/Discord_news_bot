# Routes package
from .api import api_bp
from .views import views_bp
from .admin import admin_bp

# Export all blueprints for easy access
__all__ = ['api_bp', 'views_bp', 'admin_bp', 'register_all_blueprints']

def register_all_blueprints(app):
    """Register all blueprints with the Flask app"""
    app.register_blueprint(api_bp)
    app.register_blueprint(views_bp)
    app.register_blueprint(admin_bp) 