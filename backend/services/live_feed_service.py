from .live_feed_scraper import LiveFeedScraperService
from .supabase_client import supabase_db
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
            # The original code had Redis cache checks, which are removed.
            # For now, we'll just fetch fresh data.
            
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
            # The original code had Redis status updates, which are removed.
            # For now, we'll just proceed with fetching.
            
            # Get headlines from scraper
            headlines = self.scraper.get_quick_headlines(limit=30)
            
            if headlines:
                # Store in Redis
                supabase_db.store_live_headlines(headlines)
                
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
                # The original code had Redis status updates, which are removed.
                # For now, we'll just return an error.
                return {
                    'success': False,
                    'error': 'No headlines found',
                    'data': None
                }
                
        except Exception as e:
            # The original code had Redis status updates, which are removed.
            # For now, we'll just return an error.
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
        # The original code had Redis status retrieval, which is removed.
        # For now, we'll return a placeholder.
        return {
            'status': 'Service is running',
            'last_refresh': 'N/A'
        }

# Global live feed service
live_feed_service = LiveFeedService()
