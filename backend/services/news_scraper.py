import requests
import time
import random
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin, urlparse
import concurrent.futures
from config.settings import SCRAPING_DELAY_MIN, SCRAPING_DELAY_MAX, SCRAPING_TIMEOUT, MAX_HEADLINES_PER_SOURCE

class NewsScraperService:
    """Enhanced service for scraping news headlines with article URLs and images"""
    
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
        """Enhanced scraping with article URL extraction and image scraping"""
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
            
            # Extract headlines with their article URLs
            headline_data = self._extract_headlines_with_urls(soup, url, category)
            
            # Process each headline to get images
            processed_headlines = self._process_headlines_with_images(headline_data)
            
            return processed_headlines[:MAX_HEADLINES_PER_SOURCE]
            
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
    
    def _extract_headlines_with_urls(self, soup, base_url, category):
        """Extract headlines along with their article URLs"""
        headlines_data = []
        
        # Enhanced selectors that target clickable headline elements
        headline_selectors = [
            'a h1', 'a h2', 'a h3',  # Headlines inside links
            'h1 a', 'h2 a', 'h3 a',  # Links inside headlines
            'a[href*="article"]', 'a[href*="story"]', 'a[href*="news"]',
            '.headline a', '.title a', '.story-title a',
            '.entry-title a', '.post-title a',
            '.story-headline a', '.news-title a',
            'article a', '.article-link'
        ]
        
        seen_headlines = set()
        
        for selector in headline_selectors:
            elements = soup.select(selector)
            
            for element in elements:
                # Extract headline text and URL
                if element.name == 'a':
                    # Element is a link
                    headline_text = element.get_text(strip=True)
                    article_url = element.get('href')
                else:
                    # Element contains a link
                    link = element.find('a')
                    if link:
                        headline_text = element.get_text(strip=True)
                        article_url = link.get('href')
                    else:
                        continue
                
                # Validate headline and URL
                if not self._is_valid_headline(headline_text) or not article_url:
                    continue
                
                # Convert relative URLs to absolute
                article_url = self._convert_to_absolute_url(article_url, base_url)
                
                # Check if this is a valid article URL
                if not self._is_valid_article_url(article_url, base_url):
                    continue
                
                # Avoid duplicates
                if headline_text in seen_headlines:
                    continue
                
                seen_headlines.add(headline_text)
                headlines_data.append({
                    'headline': headline_text,
                    'category': category,
                    'source_url': article_url,
                    'timestamp': datetime.now().isoformat(),
                    'image_url': ""  # Will be filled later
                })
                
                if len(headlines_data) >= MAX_HEADLINES_PER_SOURCE:
                    break
            
            if len(headlines_data) >= MAX_HEADLINES_PER_SOURCE:
                break
        
        return headlines_data
    
    def _process_headlines_with_images(self, headlines_data):
        """Process headlines to extract images from article pages"""
        processed_headlines = []
        
        for headline_data in headlines_data:
            try:
                # Add delay between article visits
                time.sleep(random.uniform(0.1, 0.2))
                
                # Extract image from article page
                image_url = self._extract_article_image(headline_data['source_url'])
                headline_data['image_url'] = image_url
                
                processed_headlines.append(headline_data)
                
            except Exception as e:
                print(f"Error processing article {headline_data['source_url']}: {e}")
                # Keep headline even if image extraction fails
                headline_data['image_url'] = ""
                processed_headlines.append(headline_data)
        
        return processed_headlines
    
    def _extract_article_image(self, article_url):
        """Extract the first relevant image from an article page"""
        try:
            response = self.session.get(article_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Priority order for image extraction
            image_selectors = [
                'meta[property="og:image"]',  # Open Graph image
                'meta[name="twitter:image"]',  # Twitter card image
                '.featured-image img',  # Featured image
                '.article-image img',  # Article image
                '.hero-image img',  # Hero image
                'article img',  # First image in article
                '.content img',  # First image in content
                'img[src*="featured"]',  # Images with "featured" in URL
                'img'  # Any image as fallback
            ]
            
            for selector in image_selectors:
                if 'meta' in selector:
                    # Handle meta tags
                    meta_tag = soup.select_one(selector)
                    if meta_tag and meta_tag.get('content'):
                        image_url = meta_tag.get('content')
                        if self._is_valid_image_url(image_url):
                            return self._convert_to_absolute_url(image_url, article_url)
                else:
                    # Handle img tags
                    img_tag = soup.select_one(selector)
                    if img_tag and img_tag.get('src'):
                        image_url = img_tag.get('src')
                        if self._is_valid_image_url(image_url):
                            return self._convert_to_absolute_url(image_url, article_url)
            
            return ""  # No valid image found
            
        except Exception as e:
            print(f"Error extracting image from {article_url}: {e}")
            return ""
    
    def _convert_to_absolute_url(self, url, base_url):
        """Convert relative URLs to absolute URLs"""
        if not url:
            return ""
        
        # If already absolute, return as is
        if url.startswith(('http://', 'https://')):
            return url
        
        # Convert relative to absolute
        return urljoin(base_url, url)
    
    def _is_valid_article_url(self, url, base_url):
        """Check if URL is a valid article URL"""
        if not url:
            return False
        
        try:
            parsed_url = urlparse(url)
            parsed_base = urlparse(base_url)
            
            # Must be from the same domain
            if parsed_url.netloc != parsed_base.netloc:
                return False
            
            # Should not be the homepage or category page
            if parsed_url.path in ['/', '']:
                return False
            
            # Should not contain certain patterns that indicate non-article pages
            invalid_patterns = [
                '/tag/', '/category/', '/author/', '/search/',
                '/page/', '/feed/', '/rss/', '/sitemap/',
                '/contact', '/about', '/privacy', '/terms'
            ]
            
            return not any(pattern in url.lower() for pattern in invalid_patterns)
            
        except Exception:
            return False
    
    def _is_valid_image_url(self, url):
        """Check if URL is a valid image URL"""
        if not url:
            return False
        
        # Check for common image extensions
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']
        url_lower = url.lower()
        
        # Must have image extension or be from known image domains
        has_extension = any(ext in url_lower for ext in image_extensions)
        is_image_domain = any(domain in url_lower for domain in ['cdn.', 'images.', 'img.', 'static.'])
        
        return has_extension or is_image_domain
    
    def _is_valid_headline(self, text):
        """Check if text is a valid headline"""
        if not text or len(text) < 20 or len(text) > 200:
            return False
        
        # Filter out common non-headline text
        invalid_patterns = [
            'cookie', 'privacy policy', 'terms of service',
            'subscribe', 'newsletter', 'advertisement',
            'click here', 'read more', 'continue reading',
            'sign up', 'log in', 'follow us', 'share this',
            'comments', 'related articles'
        ]
        
        text_lower = text.lower()
        return not any(pattern in text_lower for pattern in invalid_patterns)
    
    def _try_alternative_scraping(self, url, category):
        """Try alternative scraping methods for blocked sites"""
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
                soup = BeautifulSoup(content, 'xml')
                headlines = []
                
                items = soup.find_all('item')
                for item in items[:MAX_HEADLINES_PER_SOURCE]:
                    title_tag = item.find('title')
                    link_tag = item.find('link')
                    
                    if title_tag and title_tag.text:
                        article_url = link_tag.text.strip() if link_tag else rss_url
                        
                        # Extract image from RSS item or article page
                        image_url = ""
                        enclosure = item.find('enclosure')
                        if enclosure and 'image' in enclosure.get('type', ''):
                            image_url = enclosure.get('url', '')
                        else:
                            # Try to extract from article page
                            try:
                                image_url = self._extract_article_image(article_url)
                            except:
                                image_url = ""
                        
                        headlines.append({
                            'headline': title_tag.text.strip(),
                            'category': category,
                            'source_url': article_url,
                            'image_url': image_url,
                            'timestamp': datetime.now().isoformat()
                        })
                
                return headlines
            else:
                import feedparser
                feed = feedparser.parse(rss_url)
                headlines = []
                
                for entry in feed.entries[:MAX_HEADLINES_PER_SOURCE]:
                    article_url = entry.link if hasattr(entry, 'link') else rss_url
                    
                    # Extract image from RSS or article page
                    image_url = ""
                    if hasattr(entry, 'enclosures') and entry.enclosures:
                        for enclosure in entry.enclosures:
                            if 'image' in enclosure.get('type', ''):
                                image_url = enclosure.get('href', '')
                                break
                    
                    if not image_url:
                        try:
                            image_url = self._extract_article_image(article_url)
                        except:
                            image_url = ""
                    
                    headlines.append({
                        'headline': entry.title,
                        'category': category,
                        'source_url': article_url,
                        'image_url': image_url,
                        'timestamp': datetime.now().isoformat()
                    })
                
                return headlines
        except Exception as e:
            print(f"Error parsing RSS feed {rss_url}: {e}")
            return []
