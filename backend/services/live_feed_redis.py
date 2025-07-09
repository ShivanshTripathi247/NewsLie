import redis
import json
from datetime import datetime, timedelta
from config.settings import REDIS_HOST, REDIS_PORT

class LiveFeedRedisClient:
    """Redis client specifically for live feed data"""
    
    def __init__(self):
        self.client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            decode_responses=True
        )
        self.live_feed_key = "live_feed:headlines"
        self.status_key = "live_feed:status"
        self.cache_duration = 1800  # 30 minutes
    
    def store_live_headlines(self, headlines):
        """Store live feed headlines with timestamp"""
        try:
            # Add metadata
            live_feed_data = {
                'headlines': headlines,
                'timestamp': datetime.now().isoformat(),
                'total': len(headlines)
            }
            
            # Store as JSON
            self.client.set(self.live_feed_key, json.dumps(live_feed_data))
            self.client.expire(self.live_feed_key, self.cache_duration)
            
            # Update status
            self.update_status('ready', f'{len(headlines)} headlines available')
            
        except Exception as e:
            print(f"Error storing live headlines: {e}")
            self.update_status('error', str(e))
    
    def get_live_headlines(self):
        """Retrieve live feed headlines"""
        try:
            data = self.client.get(self.live_feed_key)
            if data:
                live_feed_data = json.loads(data)
                return live_feed_data
            return None
        except Exception as e:
            print(f"Error retrieving live headlines: {e}")
            return None
    
    def update_status(self, status, message):
        """Update live feed status"""
        try:
            status_data = {
                'status': status,
                'message': message,
                'timestamp': datetime.now().isoformat()
            }
            self.client.set(self.status_key, json.dumps(status_data))
        except Exception as e:
            print(f"Error updating status: {e}")
    
    def get_status(self):
        """Get current live feed status"""
        try:
            data = self.client.get(self.status_key)
            if data:
                return json.loads(data)
            return {'status': 'idle', 'message': 'Ready', 'timestamp': datetime.now().isoformat()}
        except Exception as e:
            print(f"Error getting status: {e}")
            return {'status': 'error', 'message': str(e), 'timestamp': datetime.now().isoformat()}
    
    def is_cache_valid(self):
        """Check if cached data is still valid"""
        try:
            ttl = self.client.ttl(self.live_feed_key)
            return ttl > 0
        except:
            return False

# Global live feed Redis client
live_feed_redis = LiveFeedRedisClient()
