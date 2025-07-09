import requests
import time
import random
from bs4 import BeautifulSoup
from datetime import datetime
from config.settings import SCRAPING_DELAY_MIN, SCRAPING_DELAY_MAX, SCRAPING_TIMEOUT, MAX_HEADLINES_PER_SOURCE

class NewsScraperService:
    """Enhanced service for scraping news headlines"""
    
    def __init__(self):
        self.session = requests.Session()
        # More realistic headers to avoid detection
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def scrape_headlines(self, url, category):
        """Enhanced scraping with better error handling"""
        try:
            # Add random delay to avoid rate limiting
            time.sleep(random.uniform(SCRAPING_DELAY_MIN, SCRAPING_DELAY_MAX))
            
            response = self.session.get(url, timeout=SCRAPING_TIMEOUT)
            response.raise_for_status()
            
            # Handle RSS feeds differently
            if url.endswith('.xml') or 'rss' in url or 'feed' in url:
                return self._parse_rss_feed(url, category, response.content)
            
            # Parse HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            headlines = []
            
            # Common selectors for headlines
            selectors = [
                'h1', 'h2', 'h3',
                '.headline', '.title', '.story-title',
                'a[href*="article"]', 'a[href*="story"]',
                '.entry-title', '.post-title',
                '.story-headline', '.news-title'
            ]
            
            for selector in selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text(strip=True)
                    if self._is_valid_headline(text):
                        headlines.append({
                            'headline': text,
                            'category': category,
                            'source_url': url,
                            'timestamp': datetime.now().isoformat()
                        })
            
            # Remove duplicates and limit results
            unique_headlines = []
            seen_headlines = set()
            
            for headline in headlines:
                if headline['headline'] not in seen_headlines:
                    seen_headlines.add(headline['headline'])
                    unique_headlines.append(headline)
                    
                if len(unique_headlines) >= MAX_HEADLINES_PER_SOURCE:
                    break
            
            return unique_headlines
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                print(f"Access forbidden for {url} - trying alternative approach")
                return self._try_alternative_scraping(url, category)
            elif e.response.status_code == 404:
                print(f"URL not found: {url} - skipping")
                return []
            else:
                print(f"HTTP error for {url}: {e}")
                return []
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return []
    
    def _is_valid_headline(self, text):
        """Check if text is a valid headline"""
        if not text or len(text) < 20 or len(text) > 200:
            return False
        
        # Filter out common non-headline text
        invalid_patterns = [
            'cookie', 'privacy policy', 'terms of service',
            'subscribe', 'newsletter', 'advertisement',
            'click here', 'read more', 'continue reading',
            'sign up', 'log in', 'follow us'
        ]
        
        text_lower = text.lower()
        return not any(pattern in text_lower for pattern in invalid_patterns)
    
    def _try_alternative_scraping(self, url, category):
        """Try alternative scraping methods for blocked sites"""
        # Implement RSS feed parsing as fallback
        rss_urls = {
            'https://www.politico.com': 'https://www.politico.com/rss/politicopicks.xml',
            'https://www.reuters.com/world/us': 'https://feeds.reuters.com/reuters/USdomesticNews',
            'https://www.bloomberg.com': 'https://feeds.bloomberg.com/markets/news.rss'
        }
        
        if url in rss_urls:
            return self._parse_rss_feed(rss_urls[url], category)
        
        return []
    
    def _parse_rss_feed(self, rss_url, category, content=None):
        """Parse RSS feeds with proper XML handling"""
        try:
            if content:
                # Use BeautifulSoup with XML parser for RSS content
                soup = BeautifulSoup(content, 'xml')
                headlines = []
                
                # Extract items from RSS feed
                items = soup.find_all('item')
                for item in items[:MAX_HEADLINES_PER_SOURCE]:
                    title_tag = item.find('title')
                    link_tag = item.find('link')
                    
                    if title_tag and title_tag.text:
                        headlines.append({
                            'headline': title_tag.text.strip(),
                            'category': category,
                            'source_url': link_tag.text.strip() if link_tag else rss_url,
                            'timestamp': datetime.now().isoformat()
                        })
                
                return headlines
            else:
                # Fallback to feedparser
                import feedparser
                feed = feedparser.parse(rss_url)
                headlines = []
                
                for entry in feed.entries[:MAX_HEADLINES_PER_SOURCE]:
                    headlines.append({
                        'headline': entry.title,
                        'category': category,
                        'source_url': entry.link if hasattr(entry, 'link') else rss_url,
                        'timestamp': datetime.now().isoformat()
                    })
                
                return headlines
        except Exception as e:
            print(f"Error parsing RSS feed {rss_url}: {e}")
            return []
