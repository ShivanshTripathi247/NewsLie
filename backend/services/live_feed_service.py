from .live_feed_scraper import LiveFeedScraperService
from .live_feed_redis import live_feed_redis
import threading
import time

class LiveFeedService:
    """Service to manage live feed operations"""
    
    def __init__(self):
        self.scraper = LiveFeedScraperService()
        self.is_fetching = False
    
    def get_live_feed(self, force_refresh=False):
        """Get live feed headlines with caching"""
        try:
            # Check cache first unless force refresh
            if not force_refresh and live_feed_redis.is_cache_valid():
                cached_data = live_feed_redis.get_live_headlines()
                if cached_data:
                    return {
                        'success': True,
                        'data': cached_data,
                        'from_cache': True
                    }
            
            # Fetch fresh data
            return self._fetch_fresh_headlines()
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'data': None
            }
    
    def _fetch_fresh_headlines(self):
        """Fetch fresh headlines from sources"""
        try:
            live_feed_redis.update_status('fetching', 'Fetching latest headlines...')
            
            # Get headlines from scraper
            headlines = self.scraper.get_quick_headlines(limit=30)
            
            if headlines:
                # Store in Redis
                live_feed_redis.store_live_headlines(headlines)
                
                return {
                    'success': True,
                    'data': {
                        'headlines': headlines,
                        'timestamp': time.time(),
                        'total': len(headlines)
                    },
                    'from_cache': False
                }
            else:
                live_feed_redis.update_status('error', 'No headlines found')
                return {
                    'success': False,
                    'error': 'No headlines found',
                    'data': None
                }
                
        except Exception as e:
            live_feed_redis.update_status('error', str(e))
            return {
                'success': False,
                'error': str(e),
                'data': None
            }
    
    def refresh_async(self):
        """Refresh live feed in background"""
        if not self.is_fetching:
            self.is_fetching = True
            thread = threading.Thread(target=self._background_refresh)
            thread.daemon = True
            thread.start()
    
    def _background_refresh(self):
        """Background refresh method"""
        try:
            self._fetch_fresh_headlines()
        finally:
            self.is_fetching = False
    
    def get_status(self):
        """Get current live feed status"""
        return live_feed_redis.get_status()

# Global live feed service
live_feed_service = LiveFeedService()
