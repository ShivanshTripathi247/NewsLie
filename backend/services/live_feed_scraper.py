import requests
import time
import random
from bs4 import BeautifulSoup
from datetime import datetime
import concurrent.futures
from urllib.parse import urljoin
import feedparser

class LiveFeedScraperService:
    """Lightweight scraper for instant headlines without analysis"""
    
    def __init__(self):
        self.session = requests.Session()
        # Minimal headers for speed
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })
        
        # Fast RSS sources for immediate content
        self.live_sources = {
            'general': [
                'https://feeds.reuters.com/reuters/topNews',
                'https://feeds.bbci.co.uk/news/rss.xml',
                'https://rss.cnn.com/rss/edition.rss'
            ],
            'technology': [
                'https://feeds.feedburner.com/TechCrunch',
                'https://www.theverge.com/rss/index.xml',
                'https://feeds.arstechnica.com/arstechnica/index'
            ],
            'business': [
                'https://feeds.reuters.com/reuters/businessNews',
                'https://feeds.bloomberg.com/markets/news.rss'
            ],
            'sports': [
                'https://www.espn.com/espn/rss/news',
                'https://feeds.bbci.co.uk/sport/rss.xml'
            ]
        }
    
    def get_quick_headlines(self, limit=30):
        """Get headlines quickly without analysis"""
        print("Fetching live feed headlines...")
        all_headlines = []
        
        # Use concurrent processing for speed
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            future_to_category = {}
            
            for category, sources in self.live_sources.items():
                for source in sources:
                    future = executor.submit(self._fetch_from_source, source, category)
                    future_to_category[future] = (source, category)
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_category, timeout=10):
                source, category = future_to_category[future]
                try:
                    headlines = future.result()
                    all_headlines.extend(headlines)
                except Exception as e:
                    print(f"Error fetching from {source}: {e}")
        
        # Remove duplicates and limit results
        unique_headlines = self._remove_duplicates(all_headlines)
        return unique_headlines[:limit]
    
    def _fetch_from_source(self, source_url, category):
        """Fetch headlines from a single source"""
        try:
            # Minimal delay for responsiveness
            time.sleep(random.uniform(0.05, 0.1))
            
            response = self.session.get(source_url, timeout=5)
            response.raise_for_status()
            
            # Parse RSS feed
            if source_url.endswith('.xml') or 'rss' in source_url or 'feed' in source_url:
                return self._parse_rss_quick(response.content, category, source_url)
            else:
                # Fallback to HTML parsing
                return self._parse_html_quick(response.content, category, source_url)
                
        except Exception as e:
            print(f"Error fetching from {source_url}: {e}")
            return []
    
    def _parse_rss_quick(self, content, category, source_url):
        """Quick RSS parsing without detailed analysis"""
        headlines = []
        
        try:
            # Use feedparser for reliable RSS parsing
            feed = feedparser.parse(content)
            
            for entry in feed.entries[:8]:  # Limit per source for speed
                if hasattr(entry, 'title') and entry.title:
                    headline_text = entry.title.strip()
                    
                    if self._is_valid_quick_headline(headline_text):
                        headlines.append({
                            'headline': headline_text,
                            'source': self._extract_source_name(source_url),
                            'category': category,
                            'timestamp': datetime.now().isoformat(),
                            'source_url': entry.link if hasattr(entry, 'link') else source_url,
                            'quick_id': f"live_{len(headlines)}_{int(time.time())}"
                        })
            
        except Exception as e:
            print(f"Error parsing RSS from {source_url}: {e}")
        
        return headlines
    
    def _parse_html_quick(self, content, category, source_url):
        """Quick HTML parsing for non-RSS sources"""
        headlines = []
        
        try:
            soup = BeautifulSoup(content, 'html.parser')
            
            # Simple selectors for quick extraction
            selectors = ['h1', 'h2', 'h3', '.headline', '.title']
            
            for selector in selectors:
                elements = soup.select(selector)[:10]  # Limit for speed
                
                for element in elements:
                    headline_text = element.get_text(strip=True)
                    
                    if self._is_valid_quick_headline(headline_text):
                        headlines.append({
                            'headline': headline_text,
                            'source': self._extract_source_name(source_url),
                            'category': category,
                            'timestamp': datetime.now().isoformat(),
                            'source_url': source_url,
                            'quick_id': f"live_{len(headlines)}_{int(time.time())}"
                        })
                        
                        if len(headlines) >= 5:  # Limit per source
                            break
                
                if len(headlines) >= 5:
                    break
                    
        except Exception as e:
            print(f"Error parsing HTML from {source_url}: {e}")
        
        return headlines
    
    def _is_valid_quick_headline(self, text):
        """Quick validation for headlines"""
        if not text or len(text) < 15 or len(text) > 150:
            return False
        
        # Quick filter for obvious non-headlines
        invalid_patterns = ['cookie', 'privacy', 'subscribe', 'newsletter', 'click here']
        text_lower = text.lower()
        
        return not any(pattern in text_lower for pattern in invalid_patterns)
    
    def _extract_source_name(self, url):
        """Extract readable source name from URL"""
        source_names = {
            'reuters.com': 'Reuters',
            'bbc.co.uk': 'BBC',
            'cnn.com': 'CNN',
            'techcrunch.com': 'TechCrunch',
            'theverge.com': 'The Verge',
            'arstechnica.com': 'Ars Technica',
            'bloomberg.com': 'Bloomberg',
            'espn.com': 'ESPN'
        }
        
        for domain, name in source_names.items():
            if domain in url:
                return name
        
        # Fallback to domain extraction
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            return domain.replace('www.', '').replace('feeds.', '').title()
        except:
            return 'News Source'
    
    def _remove_duplicates(self, headlines):
        """Remove duplicate headlines based on text similarity"""
        unique_headlines = []
        seen_headlines = set()
        
        for headline in headlines:
            headline_text = headline['headline'].lower().strip()
            
            # Simple duplicate detection
            if headline_text not in seen_headlines:
                seen_headlines.add(headline_text)
                unique_headlines.append(headline)
        
        # Sort by timestamp (newest first)
        unique_headlines.sort(key=lambda x: x['timestamp'], reverse=True)
        return unique_headlines
