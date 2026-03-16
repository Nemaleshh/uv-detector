from flask import Flask
from flask_cors import CORS
import os
from config import config

def create_app(config_name=None):
    """Application factory"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    # Auto-detect free tier for Render
    if 'onrender.com' in os.getenv('RENDER', '') or os.getenv('RENDER_FREE_TIER') == 'true':
        config_name = 'free_tier'
    
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config.get(config_name, config['development']))
    
    # Enable CORS for frontend access
    CORS(app, resources={
        r"/api/*": {
            "origins": [
                "http://localhost:3000",
                "http://localhost:5000",
                "http://*",
                "https://*.vercel.app"
            ],
            "methods": ["GET", "POST", "OPTIONS", "DELETE"],
            "allow_headers": ["Content-Type"]
        }
    })
    
    # Create upload folder
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Register blueprints
    from routes import api
    app.register_blueprint(api)
    
    # Basic route
    @app.route('/', methods=['GET'])
    def index():
        return {
            'message': 'UV Oil Leak Detection API',
            'version': '1.0.0',
            'config': config_name,
            'docs': '/api/docs'
        }
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=app.config['DEBUG']
    )
