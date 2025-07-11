import json
from config.settings import NEWS_SOURCES
from .news_scraper import NewsScraperService
from .redis_client import redis_client
from .sentiment_analyzer import SentimentAnalyzer

from services.global_database import global_db

class NewsProcessingService:
    """Service for processing and storing news data with enhanced image support"""
    
    def __init__(self):
        self.scraper = NewsScraperService()
        self.sentiment_analyzer = SentimentAnalyzer()
    
    def crawl_and_process_news(self):
        """Enhanced crawl that stores in global database"""
        print("Starting global news crawl with database storage...")
        
        all_headlines = []
        
        # Your existing crawling logic...
        for category, sources in NEWS_SOURCES.items():
            print(f"Processing {category} news...")
            
            for source in sources:
                headlines = self.scraper.scrape_headlines(source, category)
                
                if headlines:
                    for headline_data in headlines:
                        try:
                            # Your existing sentiment analysis
                            sentiment_result = self.sentiment_analyzer.analyze_sentiment(
                                headline_data['headline']
                            )
                            
                            # Combine data for global storage
                            news_item = {
                                'headline': headline_data['headline'],
                                'category': category,
                                'sentiment': sentiment_result['sentiment'],
                                'confidence': sentiment_result['confidence'],
                                'source_url': headline_data.get('source_url', ''),
                                'image_url': headline_data.get('image_url', '')
                            }
                            
                            all_headlines.append(news_item)
                            
                            # Still store in Redis for immediate API access
                            self._store_headline(news_item)
                            
                        except Exception as e:
                            print(f"Error processing headline: {e}")
                            continue
    
        # Store in global database for mobile sync
        if all_headlines:
            try:
                update_id = global_db.store_global_update(all_headlines)
                print(f"✅ Global database updated with ID: {update_id}")
            except Exception as e:
                print(f"❌ Global database storage failed: {e}")
        
        print(f"Global crawl completed. Total headlines: {len(all_headlines)}")
        return len(all_headlines)
    def _store_headline(self, news_item):
        """Store headline in Redis with image URL support"""
        try:
            # Ensure image_url field exists (backward compatibility)
            if 'image_url' not in news_item:
                news_item['image_url'] = ""
            
            # Pass the dictionary directly to Redis client
            redis_client.store_headline(news_item)
        except Exception as e:
            print(f"Error storing headline: {e}")
