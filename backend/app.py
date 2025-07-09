from flask import Flask
from flask_cors import CORS
from datetime import datetime

# Import configuration
from config.settings import FLASK_PORT, FLASK_ENV

# Import routes
from routes.api_routes import api_bp

# Import services
from services.news_processor import NewsProcessingService
from utils.scheduler import NewsScheduler

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(api_bp)
    
    return app

def main():
    """Main application entry point"""
    # Create Flask app
    app = create_app()
    
    # Initialize services
    news_service = NewsProcessingService()
    scheduler = NewsScheduler(news_service)
    
    # Start background scheduler
    print("Starting background scheduler...")
    scheduler.start_scheduler()
    
    # Initial crawl
    print("Performing initial news crawl...")
    try:
        news_service.crawl_and_process_news()
    except Exception as e:
        print(f"Error during initial crawl: {e}")
    
    # Start Flask app
    print(f"Starting Flask server on port {FLASK_PORT}")
    app.run(
        host='0.0.0.0',
        port=FLASK_PORT,
        debug=(FLASK_ENV == 'development')
    )

if __name__ == '__main__':
    main()
