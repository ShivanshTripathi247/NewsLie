from flask import Flask
from flask_cors import CORS
from datetime import datetime
import threading
import time
import schedule

# Import configuration
from config.settings import FLASK_PORT, FLASK_ENV

# Import routes
from routes.api_routes import api_bp

# Import services
from services.news_processor import NewsProcessingService
from utils.scheduler import NewsScheduler
from services.global_database import global_db  # NEW: Global database service

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(api_bp)
    
    return app

def global_news_crawl():
    """Enhanced global crawl operation for mobile sync"""
    print(f"🌍 Starting global crawl at {datetime.now()}")
    
    try:
        # Initialize news service
        news_service = NewsProcessingService()
        
        # Perform crawl and store in global database
        total_processed = news_service.crawl_and_process_news()
        print(f"✅ Global crawl completed: {total_processed} headlines processed")
        
    except Exception as e:
        print(f"❌ Global crawl failed: {e}")

def setup_global_scheduler():
    """Setup scheduled global crawls for mobile sync"""
    # Schedule global crawls twice daily
    schedule.every().day.at("06:00").do(global_news_crawl)
    schedule.every().day.at("18:00").do(global_news_crawl)
    
    print("📅 Global crawl scheduler configured (6 AM, 6 PM)")

def run_global_scheduler():
    """Run the global scheduler in background thread"""
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

def main():
    """Main application entry point"""
    # Create Flask app
    app = create_app()
    
    # Initialize services
    news_service = NewsProcessingService()
    scheduler = NewsScheduler(news_service)
    
    # Setup global crawl scheduler for mobile sync
    setup_global_scheduler()
    
    # Start global scheduler in background thread
    print("🚀 Starting global crawl scheduler...")
    global_scheduler_thread = threading.Thread(target=run_global_scheduler, daemon=True)
    global_scheduler_thread.start()
    
    # Start existing background scheduler (for live feed)
    print("Starting background scheduler...")
    scheduler.start_scheduler()
    
    # Initial crawl with global database storage
    print("Performing initial news crawl...")
    try:
        global_news_crawl()  # Use enhanced global crawl
    except Exception as e:
        print(f"Error during initial crawl: {e}")
    
    # Start Flask app
    print(f"🌐 Starting Flask server on port {FLASK_PORT}")
    app.run(
        host='0.0.0.0',
        port=FLASK_PORT,
        debug=(FLASK_ENV == 'development')
    )

if __name__ == '__main__':
    main()
