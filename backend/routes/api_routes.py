from flask import Blueprint, jsonify, request
from datetime import datetime
import json
from config.settings import NEWS_SOURCES
from services.global_database import global_db
from services.redis_client import redis_client
from services.news_processor import NewsProcessingService
from services.live_feed_service import live_feed_service
from services.chatbot_service import production_chatbot_service
from services.fake_news_analyzer import fake_news_analyzer

# Create Blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Initialize services
news_service = NewsProcessingService()




if __name__ == '__main__':
    # Start scheduler
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    # Start Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)

@api_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all available news categories"""
    try:
        categories = list(NEWS_SOURCES.keys())
        return jsonify({
            'categories': categories,
            'total': len(categories)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/headlines/<category>/<sentiment>', methods=['GET'])
def get_headlines(category, sentiment):
    """Get headlines for specific category and sentiment with image support"""
    try:
        # Validate parameters
        if category not in NEWS_SOURCES:
            return jsonify({'error': 'Invalid category'}), 400
        
        if sentiment not in ['positive', 'negative', 'neutral']:
            return jsonify({'error': 'Invalid sentiment'}), 400
        
        # Get query parameters
        min_confidence = request.args.get('min_confidence', type=float)
        limit = request.args.get('limit', default=20, type=int)
        images_only = request.args.get('images_only', default=False, type=bool)
        
        # Fetch from Redis (now includes image URLs)
        headlines = redis_client.get_headlines(category, sentiment, limit)
        
        # Apply filters
        filtered_headlines = []
        for headline in headlines:
            # Apply confidence filter if specified
            if min_confidence and headline['confidence'] < min_confidence:
                continue
            
            # Apply images_only filter if specified
            if images_only and not headline.get('image_url'):
                continue
            
            filtered_headlines.append(headline)
        
        # Calculate image statistics for this response
        total_headlines = len(filtered_headlines)
        headlines_with_images = sum(1 for h in filtered_headlines if h.get('image_url'))
        
        return jsonify({
            'headlines': filtered_headlines,
            'category': category,
            'sentiment': sentiment,
            'total': total_headlines,
            'with_images': headlines_with_images,
            'image_percentage': round((headlines_with_images / total_headlines) * 100, 1) if total_headlines > 0 else 0
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/crawl', methods=['POST'])
def trigger_crawl():
    """Manually trigger news crawling with enhanced image extraction"""
    try:
        total_processed = news_service.crawl_and_process_news()
        
        # Get image statistics after crawl
        image_stats = redis_client.get_image_stats(NEWS_SOURCES.keys())
        
        return jsonify({
            'message': 'Enhanced news crawl completed successfully',
            'headlines_processed': total_processed,
            'image_stats': image_stats
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get statistics about stored headlines"""
    try:
        stats = redis_client.get_stats(NEWS_SOURCES.keys())
        return jsonify({'stats': stats})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/image-stats', methods=['GET'])
def get_image_stats():
    """Get detailed statistics about headlines with images"""
    try:
        image_stats = redis_client.get_image_stats(NEWS_SOURCES.keys())
        return jsonify({'image_stats': image_stats})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test Redis connection
        redis_client.ping()
        return jsonify({
            'status': 'healthy',
            'redis': 'connected',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@api_bp.route('/live-feed', methods=['GET'])
def get_live_feed():
    """Get live feed headlines for immediate display"""
    try:
        force_refresh = request.args.get('refresh', default=False, type=bool)
        
        result = live_feed_service.get_live_feed(force_refresh=force_refresh)
        
        if result['success']:
            data = result['data']
            return jsonify({
                'headlines': data.get('headlines', []),
                'total': data.get('total', 0),
                'timestamp': data.get('timestamp'),
                'from_cache': result.get('from_cache', False),
                'status': 'success'
            })
        else:
            return jsonify({
                'headlines': [],
                'total': 0,
                'error': result.get('error'),
                'status': 'error'
            }), 500
            
    except Exception as e:
        return jsonify({
            'headlines': [],
            'total': 0,
            'error': str(e),
            'status': 'error'
        }), 500

@api_bp.route('/live-feed/refresh', methods=['POST'])
def refresh_live_feed():
    """Manually refresh live feed"""
    try:
        # Start background refresh
        live_feed_service.refresh_async()
        
        return jsonify({
            'message': 'Live feed refresh started',
            'status': 'refreshing'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@api_bp.route('/live-feed/status', methods=['GET'])
def get_live_feed_status():
    """Get live feed status"""
    try:
        status = live_feed_service.get_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500
    
# Update the chat endpoint
# Add these imports at the top
from services.fake_news_analyzer import fake_news_analyzer

# Add these new endpoints

@api_bp.route('/analyze-news', methods=['POST'])
def analyze_news():
    """Analyze news for fake news detection"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        source_url = data.get('source_url', '')
        
        if not text:
            return jsonify({
                'error': 'Text is required for analysis'
            }), 400
        
        if len(text) > 5000:
            return jsonify({
                'error': 'Text too long. Maximum 5000 characters.'
            }), 400
        
        # Analyze the news text
        analysis = fake_news_analyzer.analyze_news(text, source_url)
        
        return jsonify(analysis)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'credibility_score': 50,
            'risk_level': 'UNKNOWN'
        }), 500
    
# Add these new endpoints

@api_bp.route('/check-updates/<client_update_id>', methods=['GET'])
def check_for_updates(client_update_id):
    """Check if mobile app needs to sync new data"""
    try:
        latest_update_id = global_db.get_latest_update_id()
        
        has_update = (client_update_id != latest_update_id) if client_update_id != 'none' else True
        
        return jsonify({
            'hasUpdate': has_update,
            'latestUpdateId': latest_update_id,
            'clientUpdateId': client_update_id,
            'serverTime': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/bulk-download/<update_id>', methods=['GET'])
def download_bulk_update(update_id):
    """Download complete dataset for mobile local storage"""
    try:
        if update_id == 'latest':
            update_id = global_db.get_latest_update_id()
        
        if not update_id:
            return jsonify({'error': 'No updates available'}), 404
        
        headlines = global_db.get_bulk_data_for_sync(update_id)
        
        return jsonify({
            'updateId': update_id,
            'headlines': headlines,
            'totalCount': len(headlines),
            'downloadTime': datetime.now().isoformat(),
            'dataSize': f"{len(str(headlines)) / 1024:.1f} KB"
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/database-stats', methods=['GET'])
def get_database_stats():
    """Get database statistics for monitoring"""
    try:
        stats = global_db.get_database_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/model-info', methods=['GET'])
def get_model_info():
    """Get information about the loaded fake news detection model"""
    try:
        info = fake_news_analyzer.get_model_info()
        return jsonify(info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
