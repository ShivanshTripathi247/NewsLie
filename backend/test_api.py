import requests
import json
import time
from datetime import datetime

BASE_URL = 'http://localhost:5000/api'

class NewsAPITester:
    """Comprehensive test suite for News Sentiment Analysis API"""
    
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.timeout = 30
    
    def test_health_check(self):
        """Test health check endpoint"""
        print("\n🔍 Testing Health Check...")
        try:
            response = self.session.get(f'{self.base_url}/health')
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health Status: {data.get('status')}")
                print(f"✅ Redis Status: {data.get('redis')}")
                print(f"✅ Timestamp: {data.get('timestamp')}")
                return True
            else:
                print(f"❌ Health check failed with status: {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection refused - Make sure your Flask server is running!")
            print("   Run: python app.py")
            return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    def test_categories(self):
        """Test categories endpoint"""
        print("\n📂 Testing Categories...")
        try:
            response = self.session.get(f'{self.base_url}/categories')
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                categories = data.get('categories', [])
                print(f"✅ Found {len(categories)} categories:")
                for i, category in enumerate(categories, 1):
                    print(f"   {i}. {category}")
                return categories
            else:
                print(f"❌ Categories test failed: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Categories error: {e}")
            return []
    
    def test_crawl_trigger(self):
        """Test manual crawl trigger"""
        print("\n🕷️ Testing Manual Crawl Trigger...")
        try:
            print("   Triggering news crawl (this may take a while)...")
            response = self.session.post(f'{self.base_url}/crawl')
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {data.get('message')}")
                print(f"✅ Headlines processed: {data.get('headlines_processed', 0)}")
                return True
            else:
                print(f"❌ Crawl trigger failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Crawl trigger error: {e}")
            return False
    
    def test_headlines(self, categories):
        """Test headlines endpoints for all categories and sentiments"""
        print("\n📰 Testing Headlines Endpoints...")
        
        sentiments = ['positive', 'negative', 'neutral']
        results = {}
        
        for category in categories:
            results[category] = {}
            print(f"\n   Testing {category} headlines:")
            
            for sentiment in sentiments:
                try:
                    response = self.session.get(f'{self.base_url}/headlines/{category}/{sentiment}')
                    
                    if response.status_code == 200:
                        data = response.json()
                        headline_count = len(data.get('headlines', []))
                        results[category][sentiment] = headline_count
                        print(f"      {sentiment}: {headline_count} headlines")
                        
                        # Show sample headlines if available
                        if headline_count > 0:
                            sample_headlines = data['headlines'][:2]  # Show first 2
                            for i, headline in enumerate(sample_headlines, 1):
                                confidence = headline.get('confidence', 0)
                                print(f"         Sample {i}: \"{headline['headline'][:60]}...\" (Confidence: {confidence}%)")
                    else:
                        print(f"      ❌ {sentiment}: Failed ({response.status_code})")
                        results[category][sentiment] = 0
                        
                except Exception as e:
                    print(f"      ❌ {sentiment}: Error - {e}")
                    results[category][sentiment] = 0
        
        return results
    
    def test_headlines_with_filters(self):
        """Test headlines with confidence filters"""
        print("\n🔍 Testing Headlines with Confidence Filters...")
        
        test_cases = [
            ('technology', 'positive', {'min_confidence': 80}),
            ('sports', 'negative', {'min_confidence': 50}),
            ('politics', 'neutral', {'limit': 5})
        ]
        
        for category, sentiment, params in test_cases:
            try:
                response = self.session.get(f'{self.base_url}/headlines/{category}/{sentiment}', params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    headline_count = len(data.get('headlines', []))
                    filter_desc = ', '.join([f"{k}={v}" for k, v in params.items()])
                    print(f"   ✅ {category}/{sentiment} with {filter_desc}: {headline_count} headlines")
                else:
                    print(f"   ❌ Filter test failed for {category}/{sentiment}")
                    
            except Exception as e:
                print(f"   ❌ Filter test error: {e}")
    
    def test_stats(self):
        """Test statistics endpoint"""
        print("\n📊 Testing Statistics...")
        try:
            response = self.session.get(f'{self.base_url}/stats')
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                stats = data.get('stats', {})
                
                print("✅ Statistics Summary:")
                total_headlines = 0
                
                for category, sentiments in stats.items():
                    category_total = sum(sentiments.values())
                    total_headlines += category_total
                    print(f"   {category.capitalize()}: {category_total} total")
                    print(f"      Positive: {sentiments.get('positive', 0)}")
                    print(f"      Negative: {sentiments.get('negative', 0)}")
                    print(f"      Neutral: {sentiments.get('neutral', 0)}")
                
                print(f"\n   📈 Total Headlines Stored: {total_headlines}")
                return stats
            else:
                print(f"❌ Stats test failed: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"❌ Stats error: {e}")
            return {}
    
    def test_error_handling(self):
        """Test error handling for invalid requests"""
        print("\n⚠️ Testing Error Handling...")
        
        error_tests = [
            ('Invalid category', f'{self.base_url}/headlines/invalid_category/positive'),
            ('Invalid sentiment', f'{self.base_url}/headlines/technology/invalid_sentiment'),
            ('Non-existent endpoint', f'{self.base_url}/nonexistent')
        ]
        
        for test_name, url in error_tests:
            try:
                response = self.session.get(url)
                if response.status_code in [400, 404]:
                    print(f"   ✅ {test_name}: Properly handled ({response.status_code})")
                else:
                    print(f"   ⚠️ {test_name}: Unexpected status ({response.status_code})")
            except Exception as e:
                print(f"   ❌ {test_name}: Error - {e}")
    
    def run_comprehensive_test(self):
        """Run all tests in sequence"""
        print("=" * 60)
        print("🚀 NEWS SENTIMENT ANALYSIS API - COMPREHENSIVE TEST SUITE")
        print("=" * 60)
        print(f"Testing API at: {self.base_url}")
        print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Test 1: Health Check
        if not self.test_health_check():
            print("\n❌ Health check failed - stopping tests")
            return
        
        # Test 2: Categories
        categories = self.test_categories()
        if not categories:
            print("\n❌ No categories found - stopping tests")
            return
        
        # Test 3: Manual Crawl (optional - comment out if you don't want to trigger)
        print("\n⏳ Triggering manual crawl to ensure fresh data...")
        self.test_crawl_trigger()
        time.sleep(2)  # Wait for crawl to process
        
        # Test 4: Headlines
        headline_results = self.test_headlines(categories)
        
        # Test 5: Headlines with Filters
        self.test_headlines_with_filters()
        
        # Test 6: Statistics
        stats = self.test_stats()
        
        # Test 7: Error Handling
        self.test_error_handling()
        
        # Summary
        self.print_test_summary(headline_results, stats)
    
    def print_test_summary(self, headline_results, stats):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("📋 TEST SUMMARY")
        print("=" * 60)
        
        # Check if system is working
        total_headlines = sum(sum(sentiments.values()) for sentiments in stats.values()) if stats else 0
        
        if total_headlines > 0:
            print("✅ System Status: WORKING")
            print(f"✅ Total Headlines: {total_headlines}")
            
            # Find most active categories
            if stats:
                category_totals = {cat: sum(sentiments.values()) for cat, sentiments in stats.items()}
                most_active = max(category_totals.items(), key=lambda x: x[1])
                print(f"✅ Most Active Category: {most_active[0]} ({most_active[1]} headlines)")
                
                # Sentiment distribution
                total_positive = sum(sentiments.get('positive', 0) for sentiments in stats.values())
                total_negative = sum(sentiments.get('negative', 0) for sentiments in stats.values())
                total_neutral = sum(sentiments.get('neutral', 0) for sentiments in stats.values())
                
                print(f"✅ Sentiment Distribution:")
                print(f"   Positive: {total_positive} ({total_positive/total_headlines*100:.1f}%)")
                print(f"   Negative: {total_negative} ({total_negative/total_headlines*100:.1f}%)")
                print(f"   Neutral: {total_neutral} ({total_neutral/total_headlines*100:.1f}%)")
        else:
            print("⚠️ System Status: NO DATA")
            print("   Try running the crawl again or check your news sources")
        
        print(f"\n🕒 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

def main():
    """Main test function"""
    tester = NewsAPITester()
    tester.run_comprehensive_test()

if __name__ == '__main__':
    main()
