import json
from config.settings import NEWS_SOURCES
from .news_scraper import NewsScraperService
from .sentiment_analyzer import SentimentAnalyzer
from .redis_client import redis_client

class NewsProcessingService:
    """Service for processing and storing news data"""
    
    def __init__(self):
        self.scraper = NewsScraperService()
        self.sentiment_analyzer = SentimentAnalyzer()
    
    def crawl_and_process_news(self):
        """Main function to crawl news and process sentiment"""
        print("Starting news crawl and processing...")
        
        total_processed = 0
        
        for category, sources in NEWS_SOURCES.items():
            print(f"Processing {category} news...")
            
            for source in sources:
                headlines = self.scraper.scrape_headlines(source, category)
                
                # Add null check to prevent TypeError
                if headlines is None:
                    print(f"No headlines returned from {source}")
                    continue
                    
                if not headlines:  # Empty list
                    print(f"No valid headlines found from {source}")
                    continue
                
                for headline_data in headlines:
                    try:
                        # Analyze sentiment
                        sentiment_result = self.sentiment_analyzer.analyze_sentiment(
                            headline_data['headline']
                        )
                        
                        # Combine data
                        news_item = {
                            **headline_data,
                            **sentiment_result
                        }
                        
                        # Store in Redis - pass dictionary directly, not JSON string
                        self._store_headline(news_item)
                        total_processed += 1
                        
                    except Exception as e:
                        print(f"Error processing headline '{headline_data.get('headline', 'Unknown')}': {e}")
                        continue
        
        print(f"News crawl completed. Processed {total_processed} headlines.")
        return total_processed
    
    def _store_headline(self, news_item):
        """Store headline in Redis with proper categorization"""
        try:
            # Pass the dictionary directly to Redis client
            # Do NOT convert to JSON here - let Redis client handle it
            redis_client.store_headline(news_item)
        except Exception as e:
            print(f"Error storing headline: {e}")
