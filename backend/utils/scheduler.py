import schedule
import time
import threading

class NewsScheduler:
    """Background scheduler for automatic news crawling"""
    
    def __init__(self, news_service):
        self.news_service = news_service
        self.running = False
    
    def start_scheduler(self):
        """Start the background scheduler"""
        schedule.every(30).minutes.do(self.news_service.crawl_and_process_news)
        
        def run_scheduler():
            while self.running:
                schedule.run_pending()
                time.sleep(60)
        
        self.running = True
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        return scheduler_thread
    
    def stop_scheduler(self):
        """Stop the background scheduler"""
        self.running = False
        schedule.clear()
