from flask import Blueprint, jsonify, request
import json
from config.settings import NEWS_SOURCES
from services.redis_client import redis_client
from services.news_processor import NewsProcessingService

# Create Blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Initialize services
news_service = NewsProcessingService()

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
    """Get headlines for specific category and sentiment"""
    try:
        # Validate parameters
        if category not in NEWS_SOURCES:
            return jsonify({'error': 'Invalid category'}), 400
        
        if sentiment not in ['positive', 'negative', 'neutral']:
            return jsonify({'error': 'Invalid sentiment'}), 400
        
        # Get query parameters
        min_confidence = request.args.get('min_confidence', type=float)
        limit = request.args.get('limit', default=20, type=int)
        
        # Fetch from Redis
        headlines_data = redis_client.get_headlines(category, sentiment, limit)
        
        # Parse and filter headlines
        headlines = []
        for headline_json in headlines_data:
            try:
                headline = json.loads(headline_json)
                
                # Apply confidence filter if specified
                if min_confidence and headline['confidence'] < min_confidence:
                    continue
                
                headlines.append(headline)
            except json.JSONDecodeError:
                continue
        
        return jsonify({
            'headlines': headlines,
            'category': category,
            'sentiment': sentiment,
            'total': len(headlines)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/crawl', methods=['POST'])
def trigger_crawl():
    """Manually trigger news crawling"""
    try:
        total_processed = news_service.crawl_and_process_news()
        return jsonify({
            'message': 'News crawl completed successfully',
            'headlines_processed': total_processed
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
