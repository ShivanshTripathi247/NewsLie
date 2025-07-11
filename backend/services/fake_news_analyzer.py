import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductionFakeNewsAnalyzer:
    """Production-ready fake news analyzer with trained model"""
    
    def __init__(self, model_path="./models/production_fake_news_model"):
        self.model_path = model_path
        self.model = None
        self.tokenizer = None
        self.classifier = None
        self.performance_metrics = {}
        self.fact_checker = EnhancedFactChecker()
        
        # Load the model
        self._load_production_model()
    
    def _load_production_model(self):
        """Load the production-trained model with corrected labels"""
        try:
            if os.path.exists(self.model_path):
                logger.info("Loading production fake news detection model...")
                
                # Load tokenizer
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
                
                # Load model with CORRECTED label mapping
                self.model = AutoModelForSequenceClassification.from_pretrained(
                    self.model_path,
                    num_labels=2,
                    id2label={0: "REAL", 1: "FAKE"},  # SWAPPED: 0=REAL, 1=FAKE
                    label2id={"REAL": 0, "FAKE": 1}   # SWAPPED: REAL=0, FAKE=1
                )
                
                # Create pipeline with updated parameters
                device = 0 if torch.cuda.is_available() else -1
                self.classifier = pipeline(
                    "text-classification",
                    model=self.model,
                    tokenizer=self.tokenizer,
                    device=device,
                    top_k=None  # Updated parameter instead of return_all_scores
                )
                
                # Load performance metrics if available
                metrics_path = os.path.join(self.model_path, 'model_performance.json')
                if os.path.exists(metrics_path):
                    with open(metrics_path, 'r') as f:
                        self.performance_metrics = json.load(f)
                
                logger.info("✅ Production model loaded successfully with corrected labels")
                logger.info(f"📊 Model accuracy: {self.performance_metrics.get('test_accuracy', 'N/A')}")
                
            else:
                logger.warning(f"❌ Model path {self.model_path} not found")
                self._use_fallback_system()
            
        except Exception as e:
            logger.error(f"❌ Error loading production model: {e}")
            self._use_fallback_system()

    
    def _use_fallback_system(self):
        """Use rule-based fallback when model loading fails"""
        logger.info("🔄 Using rule-based fallback system")
        self.classifier = None
    
    def analyze_news(self, text, source_url=""):
        """Analyze news text for credibility with production model"""
        try:
            # Step 1: ML Model Analysis (50% weight)
            if self.classifier:
                ml_result = self._analyze_with_model(text)
                ml_score = ml_result['credibility_score']
                ml_confidence = ml_result['confidence']
                ml_prediction = ml_result['prediction']
            else:
                # Fallback to rule-based analysis
                ml_result = self._rule_based_analysis(text)
                ml_score = ml_result['credibility_score']
                ml_confidence = ml_result['confidence']
                ml_prediction = ml_result['prediction']
            
            # Step 2: Fact-checking Analysis (50% weight)
            fact_result = self.fact_checker.comprehensive_analysis(text, source_url)
            fact_score = fact_result['score']
            fact_sources = fact_result['sources']
            
            # Calculate composite credibility score
            composite_score = (ml_score * 0.5) + (fact_score * 0.5)
            
            # Generate comprehensive response
            return {
                'credibility_score': round(composite_score, 1),
                'risk_level': self._get_risk_level(composite_score),
                'ml_analysis': {
                    'prediction': ml_prediction,
                    'confidence': round(ml_confidence, 1),
                    'score': round(ml_score, 1)
                },
                'fact_check': {
                    'score': round(fact_score, 1),
                    'sources': fact_sources
                },
                'explanation': self._generate_explanation(
                    composite_score, ml_score, fact_score, ml_confidence, ml_prediction
                ),
                'recommendation': self._get_recommendation(composite_score),
                'metadata': {
                    'model_type': 'Production RoBERTa' if self.classifier else 'Rule-based Fallback',
                    'model_accuracy': self.performance_metrics.get('test_accuracy', 'N/A'),
                    'analysis_timestamp': datetime.now().isoformat(),
                    'text_length': len(text)
                }
            }
            
        except Exception as e:
            logger.error(f"Error in news analysis: {e}")
            return {
                'error': str(e),
                'credibility_score': 50,
                'risk_level': 'UNKNOWN',
                'recommendation': 'Analysis failed. Please verify manually with trusted sources.'
            }
    
    def _analyze_with_model(self, text):
        """Analyze text with the trained model"""
        try:
            # Get model prediction
            results = self.classifier(text)
            
            # Handle both old and new pipeline formats
            if isinstance(results[0], list):
                # New format: list of dictionaries
                fake_score = next((r['score'] for r in results[0] if r['label'] == 'FAKE'), 0)
                real_score = next((r['score'] for r in results[0] if r['label'] == 'REAL'), 0)
            else:
                # Old format: single dictionary
                if results[0]['label'] == 'FAKE':
                    fake_score = results[0]['score']
                    real_score = 1 - fake_score
                else:
                    real_score = results[0]['score']
                    fake_score = 1 - real_score
            
            # Determine prediction and confidence
            if real_score > fake_score:
                prediction = 'REAL'
                confidence = real_score * 100
                credibility_score = confidence
            else:
                prediction = 'FAKE'
                confidence = fake_score * 100
                credibility_score = 100 - confidence
            
            return {
                'prediction': prediction,
                'confidence': confidence,
                'credibility_score': credibility_score,
                'raw_scores': {'real': real_score, 'fake': fake_score}
            }
            
        except Exception as e:
            logger.error(f"Model analysis error: {e}")
            return self._rule_based_analysis(text)

    
    def _rule_based_analysis(self, text):
        """Fallback rule-based analysis"""
        text_lower = text.lower()
        
        # Credibility indicators
        credible_patterns = [
            'according to study', 'research shows', 'data indicates',
            'experts say', 'official statement', 'peer-reviewed',
            'reuters reports', 'ap news', 'government data'
        ]
        
        # Misinformation indicators
        fake_patterns = [
            'secret cure', 'doctors hate this', 'miracle breakthrough',
            'government cover-up', 'they don\'t want you to know',
            'shocking truth', 'one weird trick', 'big pharma conspiracy'
        ]
        
        credible_count = sum(1 for pattern in credible_patterns if pattern in text_lower)
        fake_count = sum(1 for pattern in fake_patterns if pattern in text_lower)
        
        if fake_count > credible_count:
            prediction = 'FAKE'
            confidence = min(60 + (fake_count * 10), 85)
            credibility_score = 100 - confidence
        elif credible_count > fake_count:
            prediction = 'REAL'
            confidence = min(60 + (credible_count * 10), 85)
            credibility_score = confidence
        else:
            prediction = 'UNCERTAIN'
            confidence = 45
            credibility_score = 50
        
        return {
            'prediction': prediction,
            'confidence': confidence,
            'credibility_score': credibility_score
        }
    
    def _get_risk_level(self, score):
        """Get risk level for content sharing"""
        if score >= 85:
            return "VERY LOW RISK"
        elif score >= 70:
            return "LOW RISK"
        elif score >= 55:
            return "MODERATE RISK"
        elif score >= 35:
            return "HIGH RISK"
        else:
            return "VERY HIGH RISK"
    
    def _generate_explanation(self, composite_score, ml_score, fact_score, ml_confidence, ml_prediction):
        """Generate detailed explanation"""
        explanation = "🔍 **COMPREHENSIVE ANALYSIS**\n\n"
        
        # Overall assessment
        if composite_score >= 80:
            explanation += "✅ **HIGHLY CREDIBLE**: This content appears to be legitimate and trustworthy.\n\n"
        elif composite_score >= 65:
            explanation += "⚠️ **LIKELY CREDIBLE**: This content appears mostly reliable with good indicators.\n\n"
        elif composite_score >= 50:
            explanation += "❓ **UNCERTAIN**: Mixed signals detected, exercise caution.\n\n"
        elif composite_score >= 30:
            explanation += "⚠️ **LIKELY MISINFORMATION**: Multiple warning signs detected.\n\n"
        else:
            explanation += "❌ **HIGHLY LIKELY MISINFORMATION**: Strong indicators of false information.\n\n"
        
        # Detailed breakdown
        explanation += "📊 **ANALYSIS BREAKDOWN**:\n"
        explanation += f"• AI Model Assessment: {ml_prediction} ({ml_confidence:.1f}% confidence)\n"
        explanation += f"• AI Credibility Score: {ml_score:.1f}/100\n"
        explanation += f"• Fact-Check Score: {fact_score:.1f}/100\n"
        explanation += f"• Overall Score: {composite_score:.1f}/100\n"
        
        return explanation
    
    def _get_recommendation(self, score):
        """Get actionable recommendation"""
        if score >= 80:
            return "✅ **HIGHLY TRUSTWORTHY** - Safe to trust and share with confidence"
        elif score >= 65:
            return "⚠️ **LIKELY RELIABLE** - Generally trustworthy, minimal additional verification needed"
        elif score >= 50:
            return "❓ **VERIFY FIRST** - Check with additional trusted sources before sharing"
        elif score >= 30:
            return "⚠️ **HIGH CAUTION** - Multiple red flags detected, verify thoroughly"
        else:
            return "❌ **DO NOT SHARE** - Strong indicators of misinformation, avoid sharing"
    
    def get_model_info(self):
        """Get information about the loaded model"""
        return {
            'model_loaded': self.classifier is not None,
            'model_path': self.model_path,
            'performance_metrics': self.performance_metrics,
            'device': 'GPU' if torch.cuda.is_available() else 'CPU'
        }

class EnhancedFactChecker:
    """Enhanced fact-checking service for production use"""
    
    def __init__(self):
        self.credible_domains = [
            'reuters.com', 'bbc.com', 'cnn.com', 'npr.org', 'apnews.com',
            'washingtonpost.com', 'nytimes.com', 'theguardian.com', 'wsj.com'
        ]
        
        self.questionable_domains = [
            'infowars.com', 'naturalnews.com', 'beforeitsnews.com'
        ]
    
    def comprehensive_analysis(self, text, source_url=""):
        """Perform comprehensive fact-checking analysis"""
        
        # Multiple analysis layers
        keyword_score = self._analyze_keywords(text)
        source_score = self._analyze_source(source_url)
        language_score = self._analyze_language_patterns(text)
        temporal_score = self._analyze_temporal_consistency(text)
        
        # Calculate weighted composite score
        composite_score = (
            keyword_score * 0.3 +
            source_score * 0.3 +
            language_score * 0.2 +
            temporal_score * 0.2
        )
        
        # Generate verification sources
        sources = self._generate_sources(composite_score, text)
        
        return {
            'score': composite_score,
            'sources': sources,
            'breakdown': {
                'keywords': keyword_score,
                'source': source_score,
                'language': language_score,
                'temporal': temporal_score
            }
        }
    
    def _analyze_keywords(self, text):
        """Analyze keywords for credibility indicators"""
        text_lower = text.lower()
        
        # High credibility patterns
        high_credible = [
            'peer-reviewed study', 'published research', 'clinical trial',
            'government data', 'official statistics'
        ]
        
        # High misinformation patterns
        high_fake = [
            'secret government', 'big pharma conspiracy', 'miracle cure',
            'doctors hate this', 'they don\'t want you to know'
        ]
        
        # Medium patterns
        medium_credible = ['study shows', 'research indicates', 'experts say']
        medium_fake = ['shocking truth', 'unbelievable', 'you won\'t believe']
        
        score = 50  # Start neutral
        
        for pattern in high_credible:
            if pattern in text_lower:
                score += 25
        
        for pattern in high_fake:
            if pattern in text_lower:
                score -= 25
        
        for pattern in medium_credible:
            if pattern in text_lower:
                score += 15
        
        for pattern in medium_fake:
            if pattern in text_lower:
                score -= 15
        
        return max(0, min(100, score))
    
    def _analyze_source(self, source_url):
        """Analyze source credibility"""
        if not source_url:
            return 40
        
        url_lower = source_url.lower()
        
        # Tier 1: Highly credible
        if any(domain in url_lower for domain in self.credible_domains[:4]):
            return 90
        
        # Tier 2: Generally credible
        if any(domain in url_lower for domain in self.credible_domains[4:]):
            return 75
        
        # Known questionable sources
        if any(domain in url_lower for domain in self.questionable_domains):
            return 15
        
        return 45  # Unknown source
    
    def _analyze_language_patterns(self, text):
        """Analyze language patterns"""
        text_lower = text.lower()
        
        professional_patterns = [
            'according to', 'data shows', 'research indicates',
            'officials say', 'spokesperson stated'
        ]
        
        sensational_patterns = [
            'absolutely incredible', 'mind-blowing', 'shocking',
            'unbelievable', 'amazing discovery'
        ]
        
        professional_count = sum(1 for p in professional_patterns if p in text_lower)
        sensational_count = sum(1 for p in sensational_patterns if p in text_lower)
        
        if professional_count > sensational_count:
            return 75
        elif sensational_count > professional_count:
            return 35
        else:
            return 55
    
    def _analyze_temporal_consistency(self, text):
        """Check temporal consistency"""
        current_year = datetime.now().year
        
        # Check for impossible future dates
        future_years = [str(current_year + i) for i in range(1, 5)]
        if any(year in text for year in future_years):
            return 25
        
        return 70
    
    def _generate_sources(self, score, text):
        """Generate verification sources"""
        sources = []
        
        if score >= 70:
            sources.extend([
                "Content shows strong credibility indicators",
                "Language patterns consistent with professional journalism",
                "No significant misinformation markers detected"
            ])
        elif score >= 50:
            sources.extend([
                "Mixed credibility signals detected",
                "Some professional indicators present",
                "Recommend additional source verification"
            ])
        else:
            sources.extend([
                "Multiple misinformation indicators detected",
                "Language patterns raise credibility concerns",
                "Similar claims often associated with false information"
            ])
        
        return sources

# Global analyzer instance
fake_news_analyzer = ProductionFakeNewsAnalyzer()
