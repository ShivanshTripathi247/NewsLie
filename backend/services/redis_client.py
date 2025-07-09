import redis
import json
from config.settings import REDIS_HOST, REDIS_PORT

class RedisClient:
    """Redis client wrapper with enhanced image URL support"""
    
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
        """Store headline in Redis with image URL support"""
        try:
            # Ensure news_item is a dictionary, not a JSON string
            if isinstance(news_item, str):
                news_item = json.loads(news_item)
            
            # Ensure image_url field exists for backward compatibility
            if 'image_url' not in news_item:
                news_item['image_url'] = ""
            
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
        """Retrieve headlines from Redis with image URL support"""
        key = f"headlines:{sentiment}:{category}"
        headlines_data = self.client.lrange(key, 0, limit - 1)
        
        # Parse headlines and ensure image_url field exists
        parsed_headlines = []
        for headline_json in headlines_data:
            try:
                headline = json.loads(headline_json)
                # Ensure backward compatibility for headlines without image_url
                if 'image_url' not in headline:
                    headline['image_url'] = ""
                parsed_headlines.append(headline)
            except json.JSONDecodeError:
                continue
        
        return parsed_headlines
    
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
    
    def get_image_stats(self, categories):
        """Get statistics about headlines with images"""
        image_stats = {}
        total_headlines = 0
        total_with_images = 0
        
        for category in categories:
            image_stats[category] = {'with_images': 0, 'total': 0}
            
            for sentiment in ['positive', 'negative', 'neutral']:
                key = f"headlines:{sentiment}:{category}"
                headlines_data = self.client.lrange(key, 0, -1)
                
                for headline_json in headlines_data:
                    try:
                        headline = json.loads(headline_json)
                        image_stats[category]['total'] += 1
                        total_headlines += 1
                        
                        if headline.get('image_url'):
                            image_stats[category]['with_images'] += 1
                            total_with_images += 1
                    except json.JSONDecodeError:
                        continue
        
        # Calculate percentages
        for category in image_stats:
            if image_stats[category]['total'] > 0:
                image_stats[category]['percentage'] = round(
                    (image_stats[category]['with_images'] / image_stats[category]['total']) * 100, 1
                )
            else:
                image_stats[category]['percentage'] = 0
        
        image_stats['overall'] = {
            'total': total_headlines,
            'with_images': total_with_images,
            'percentage': round((total_with_images / total_headlines) * 100, 1) if total_headlines > 0 else 0
        }
        
        return image_stats

# Global Redis client instance
redis_client = RedisClient()
