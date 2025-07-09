import json
from config.settings import NEWS_SOURCES
from .news_scraper import NewsScraperService
from .sentiment_analyzer import SentimentAnalyzer
from .redis_client import redis_client

class NewsProcessingService:
    """Service for processing and storing news data with enhanced image support"""
    
    def __init__(self):
        self.scraper = NewsScraperService()
        self.sentiment_analyzer = SentimentAnalyzer()
    
    def crawl_and_process_news(self):
        """Main function to crawl news and process sentiment with image extraction"""
        print("Starting enhanced news crawl with image extraction...")
        
        total_processed = 0
        total_with_images = 0
        
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
                        
                        # Combine data (now includes image_url from scraper)
                        news_item = {
                            **headline_data,
                            **sentiment_result
                        }
                        
                        # Track image statistics
                        if news_item.get('image_url'):
                            total_with_images += 1
                        
                        # Store in Redis - pass dictionary directly
                        self._store_headline(news_item)
                        total_processed += 1
                        
                    except Exception as e:
                        print(f"Error processing headline '{headline_data.get('headline', 'Unknown')}': {e}")
                        continue
        
        print(f"Enhanced news crawl completed.")
        print(f"Total headlines processed: {total_processed}")
        print(f"Headlines with images: {total_with_images}")
        print(f"Image success rate: {(total_with_images/total_processed*100):.1f}%" if total_processed > 0 else "No headlines processed")
        
        return total_processed
    
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
