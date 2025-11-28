"""
Main application entry point for DO GenAI API.
"""
import os
from dotenv import load_dotenv
from flask import Flask
from middleware.auth import require_auth
from routes.health import health_bp
from routes.files import files_bp
from routes.knowledge_bases import knowledge_bases_bp
from routes.agents import agents_bp
from routes.models import models_bp
from routes.databases import databases_bp
from routes.buckets import buckets_bp

# Load environment variables
load_dotenv()

# API Bearer Token for authentication
API_BEARER_TOKEN = os.getenv('API_BEARER_TOKEN')


def create_app() -> Flask:
    """
    Application factory pattern for creating Flask app instances.
    
    Returns:
        Flask: Configured Flask application instance
    """
    if not API_BEARER_TOKEN:
        raise ValueError("API_BEARER_TOKEN environment variable is required")

    app = Flask(__name__)
    
    # Load configuration from environment variables
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Register authentication middleware - requires Bearer token for all requests
    app.before_request(require_auth)
    
    # Register blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(files_bp)
    app.register_blueprint(knowledge_bases_bp)
    app.register_blueprint(agents_bp)
    app.register_blueprint(models_bp)
    app.register_blueprint(databases_bp)
    app.register_blueprint(buckets_bp)
    
    return app


# Create app instance for uWSGI and other WSGI servers
app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
