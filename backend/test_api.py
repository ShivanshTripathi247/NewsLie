import requests
import json
import time
from datetime import datetime

BASE_URL = 'http://localhost:5000/api'

class NewsAPITester:
    """Enhanced test suite for News Sentiment Analysis API with image support"""
    
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
        """Test manual crawl trigger with image extraction"""
        print("\n🕷️ Testing Enhanced Crawl Trigger...")
        try:
            print("   Triggering enhanced news crawl with image extraction...")
            response = self.session.post(f'{self.base_url}/crawl')
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {data.get('message')}")
                print(f"✅ Headlines processed: {data.get('headlines_processed', 0)}")
                
                # Display image statistics
                image_stats = data.get('image_stats', {})
                if image_stats:
                    overall = image_stats.get('overall', {})
                    print(f"✅ Headlines with images: {overall.get('with_images', 0)}")
                    print(f"✅ Image success rate: {overall.get('percentage', 0)}%")
                
                return True
            else:
                print(f"❌ Crawl trigger failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Crawl trigger error: {e}")
            return False
    
    def test_headlines_with_images(self, categories):
        """Test headlines endpoints with image support"""
        print("\n📰 Testing Headlines with Image Support...")
        
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
                        with_images = data.get('with_images', 0)
                        image_percentage = data.get('image_percentage', 0)
                        
                        results[category][sentiment] = {
                            'total': headline_count,
                            'with_images': with_images,
                            'percentage': image_percentage
                        }
                        
                        print(f"      {sentiment}: {headline_count} headlines ({with_images} with images - {image_percentage}%)")
                        
                        # Show sample headlines with image status
                        if headline_count > 0:
                            sample_headlines = data['headlines'][:2]
                            for i, headline in enumerate(sample_headlines, 1):
                                confidence = headline.get('confidence', 0)
                                has_image = "🖼️" if headline.get('image_url') else "📝"
                                print(f"         {has_image} Sample {i}: \"{headline['headline'][:50]}...\" (Confidence: {confidence}%)")
                    else:
                        print(f"      ❌ {sentiment}: Failed ({response.status_code})")
                        results[category][sentiment] = {'total': 0, 'with_images': 0, 'percentage': 0}
                        
                except Exception as e:
                    print(f"      ❌ {sentiment}: Error - {e}")
                    results[category][sentiment] = {'total': 0, 'with_images': 0, 'percentage': 0}
        
        return results
    
    def test_image_stats(self):
        """Test image statistics endpoint"""
        print("\n📊 Testing Image Statistics...")
        try:
            response = self.session.get(f'{self.base_url}/image-stats')
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                image_stats = data.get('image_stats', {})
                
                print("✅ Image Statistics by Category:")
                for category, stats in image_stats.items():
                    if category != 'overall':
                        total = stats.get('total', 0)
                        with_images = stats.get('with_images', 0)
                        percentage = stats.get('percentage', 0)
                        print(f"   {category.capitalize()}: {with_images}/{total} ({percentage}%)")
                
                overall = image_stats.get('overall', {})
                print(f"\n✅ Overall Image Statistics:")
                print(f"   Total Headlines: {overall.get('total', 0)}")
                print(f"   With Images: {overall.get('with_images', 0)}")
                print(f"   Success Rate: {overall.get('percentage', 0)}%")
                
                return image_stats
            else:
                print(f"❌ Image stats test failed: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"❌ Image stats error: {e}")
            return {}
    
    def run_comprehensive_test(self):
        """Run all tests including image functionality"""
        print("=" * 60)
        print("🚀 ENHANCED NEWS SENTIMENT ANALYSIS API - COMPREHENSIVE TEST SUITE")
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
        
        # Test 3: Enhanced Crawl
        print("\n⏳ Triggering enhanced crawl with image extraction...")
        self.test_crawl_trigger()
        time.sleep(3)  # Wait for crawl to process
        
        # Test 4: Headlines with Images
        headline_results = self.test_headlines_with_images(categories)
        
        # Test 5: Image Statistics
        image_stats = self.test_image_stats()
        
        # Summary
        self.print_enhanced_summary(headline_results, image_stats)
    
    def print_enhanced_summary(self, headline_results, image_stats):
        """Print comprehensive test summary with image statistics"""
        print("\n" + "=" * 60)
        print("📋 ENHANCED TEST SUMMARY")
        print("=" * 60)
        
        overall = image_stats.get('overall', {})
        total_headlines = overall.get('total', 0)
        total_with_images = overall.get('with_images', 0)
        image_success_rate = overall.get('percentage', 0)
        
        if total_headlines > 0:
            print("✅ System Status: WORKING WITH IMAGE SUPPORT")
            print(f"✅ Total Headlines: {total_headlines}")
            print(f"✅ Headlines with Images: {total_with_images}")
            print(f"✅ Image Success Rate: {image_success_rate}%")
            
            # Category breakdown
            print(f"\n📊 Image Success by Category:")
            for category, stats in image_stats.items():
                if category != 'overall':
                    total = stats.get('total', 0)
                    with_images = stats.get('with_images', 0)
                    percentage = stats.get('percentage', 0)
                    print(f"   {category.capitalize()}: {percentage}% ({with_images}/{total})")
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
