"""
Flask Application Factory
Main application initialization
"""

from flask import Flask, jsonify
from flask_cors import CORS
from flask_mail import Mail
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from config.config import config
import os

# Import database and models
from models.models import db, User
from utils.security import limiter

# Import blueprints
from routes.auth import auth_bp
from routes.properties import property_bp
from routes.user import user_bp
from routes.messages import message_bp
from routes.contact import contact_bp
from routes.admin import admin_bp


def create_app(config_name=None):
    """Application factory function"""
    
    # Determine config name
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config.get(config_name, config['development']))
    
    # Initialize extensions
    db.init_app(app)
    CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)
    Mail().init_app(app)
    JWTManager(app)
    limiter.init_app(app)
    
    # Initialize login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Create upload folder
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(property_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(message_bp)
    app.register_blueprint(contact_bp)
    app.register_blueprint(admin_bp)
    
    # Error handlers
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'message': 'Bad request'}), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({'message': 'Unauthorized'}), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({'message': 'Forbidden'}), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'message': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'message': 'Internal server error'}), 500
    
    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({'status': 'ok', 'message': 'Server is running'}), 200
    
    # API info endpoint
    @app.route('/api/info', methods=['GET'])
    def api_info():
        return jsonify({
            'app_name': 'Prince Property Deal',
            'version': '1.0.0',
            'environment': config_name
        }), 200
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
