import redis
import json
from config.settings import REDIS_HOST, REDIS_PORT

class RedisClient:
    """Redis client wrapper with connection management"""
    
    def __init__(self):
        self.client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            decode_responses=True
        )
    
    def get_client(self):
        """Get Redis client instance"""
        return self.client
    
    def ping(self):
        """Test Redis connection"""
        return self.client.ping()
    
    def store_headline(self, news_item):
        """Store headline in Redis with proper categorization"""
        try:
            # Ensure news_item is a dictionary, not a JSON string
            if isinstance(news_item, str):
                news_item = json.loads(news_item)
            
            # Convert dictionary to JSON string for Redis storage
            news_item_json = json.dumps(news_item)
            
            # Store in sentiment-category specific list
            key = f"headlines:{news_item['sentiment']}:{news_item['category']}"
            self.client.lpush(key, news_item_json)
            
            # Keep only latest 50 headlines per category/sentiment
            self.client.ltrim(key, 0, 49)
            
            # Store in general category list for statistics
            general_key = f"headlines:all:{news_item['category']}"
            self.client.lpush(general_key, news_item_json)
            self.client.ltrim(general_key, 0, 99)
            
        except Exception as e:
            print(f"Error storing headline: {e}")
            print(f"News item type: {type(news_item)}")
            print(f"News item content: {news_item}")
    
    def get_headlines(self, category, sentiment, limit=20):
        """Retrieve headlines from Redis"""
        key = f"headlines:{sentiment}:{category}"
        return self.client.lrange(key, 0, limit - 1)
    
    def get_stats(self, categories):
        """Get statistics for all categories and sentiments"""
        stats = {}
        for category in categories:
            stats[category] = {}
            for sentiment in ['positive', 'negative', 'neutral']:
                key = f"headlines:{sentiment}:{category}"
                count = self.client.llen(key)
                stats[category][sentiment] = count
        return stats

# Global Redis client instance
redis_client = RedisClient()
