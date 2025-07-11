import requests
import json

BASE_URL = 'http://localhost:5000/api'

def test_fake_news_integration():
    """Test the integrated fake news detection system"""
    
    print("🧪 TESTING FAKE NEWS DETECTION BACKEND INTEGRATION")
    print("=" * 60)
    
    # Test 1: Model Info
    print("\n1. Testing Model Info Endpoint...")
    try:
        response = requests.get(f'{BASE_URL}/model-info')
        if response.status_code == 200:
            info = response.json()
            print(f"✅ Model loaded: {info['model_loaded']}")
            print(f"✅ Model type: {info.get('model_path', 'N/A')}")
            print(f"✅ Device: {info.get('device', 'N/A')}")
            if info.get('performance_metrics'):
                print(f"✅ Model accuracy: {info['performance_metrics'].get('test_accuracy', 'N/A')}")
        else:
            print(f"❌ Model info failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Model info error: {e}")
    
    # Test 2: Credible News Analysis
    print("\n2. Testing Credible News Analysis...")
    credible_text = "Federal Reserve announces 0.25% interest rate increase following comprehensive economic analysis, according to official Fed statement released today."
    
    try:
        response = requests.post(f'{BASE_URL}/analyze-news', json={
            'text': credible_text,
            'source_url': 'https://www.reuters.com/markets/fed-announces-rate-hike'
        })
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Credibility Score: {result['credibility_score']}/100")
            print(f"✅ Risk Level: {result['risk_level']}")
            print(f"✅ ML Prediction: {result['ml_analysis']['prediction']}")
            
            if result['credibility_score'] >= 60:
                print("✅ Correctly identified as credible")
            else:
                print("⚠️ Unexpected low credibility score")
        else:
            print(f"❌ Analysis failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Analysis error: {e}")
    
    # Test 3: Fake News Analysis
    print("\n3. Testing Fake News Analysis...")
    fake_text = "BREAKING: Scientists discover that drinking lemon water mixed with baking soda can completely cure cancer in just 30 days! Doctors hate this one weird trick that big pharma doesn't want you to know!"
    
    try:
        response = requests.post(f'{BASE_URL}/analyze-news', json={
            'text': fake_text
        })
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Credibility Score: {result['credibility_score']}/100")
            print(f"✅ Risk Level: {result['risk_level']}")
            print(f"✅ ML Prediction: {result['ml_analysis']['prediction']}")
            
            if result['credibility_score'] <= 40:
                print("✅ Correctly identified as likely fake")
            else:
                print("⚠️ Unexpected high credibility score")
        else:
            print(f"❌ Analysis failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Analysis error: {e}")
    
    # Test 4: Error Handling
    print("\n4. Testing Error Handling...")
    try:
        response = requests.post(f'{BASE_URL}/analyze-news', json={
            'text': ''  # Empty text
        })
        
        if response.status_code == 400:
            print("✅ Empty text properly rejected")
        else:
            print(f"⚠️ Unexpected response for empty text: {response.status_code}")
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Backend integration testing completed!")

if __name__ == '__main__':
    test_fake_news_integration()
