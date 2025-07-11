from .fake_news_analyzer import fake_news_analyzer
import json
from datetime import datetime

class ProductionChatbotService:
    """Enhanced chatbot service with production fake news detection"""
    
    def __init__(self):
        self.analyzer = fake_news_analyzer
        self.conversation_history = {}
    
    def process_message(self, user_id, message):
        """Process user message with production model"""
        
        # Initialize conversation if new user
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        # Add user message to history
        self.conversation_history[user_id].append({
            'type': 'user',
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
        
        # Generate response using production model
        response = self._generate_production_response(user_id, message)
        
        # Add bot response to history
        self.conversation_history[user_id].append({
            'type': 'bot',
            'message': response['message'],
            'analysis': response.get('analysis'),
            'timestamp': datetime.now().isoformat()
        })
        
        return response
    
    def _generate_production_response(self, user_id, message):
        """Generate response using production model"""
        
        message_lower = message.lower()
        
        # Greeting responses
        if any(greeting in message_lower for greeting in ['hello', 'hi', 'hey']):
            return {
                'message': "Hello! I'm your **Production AI Fact-Checker** 🤖\n\nI've been trained on real datasets to detect misinformation with high accuracy. Share any news headline or article with me and I'll provide a detailed credibility analysis!\n\n**Try:** 'Analyze this: [paste your news text here]'",
                'type': 'greeting'
            }
        
        # Analysis requests
        elif any(keyword in message_lower for keyword in ['analyze', 'check', 'verify', 'real', 'fake']):
            news_text = self._extract_news_text(message)
            
            if news_text:
                # Use production model for analysis
                analysis = self.analyzer.analyze_news(news_text)
                response_message = self._format_production_response(analysis)
                
                return {
                    'message': response_message,
                    'analysis': analysis,
                    'type': 'analysis'
                }
            else:
                return {
                    'message': "Please share the news text you'd like me to analyze. You can copy and paste any headline or article content.",
                    'type': 'request_text'
                }
        
        # Default response
        else:
            return {
                'message': "I'm your **Production AI Fact-Checker**! 🧠\n\nI can analyze news content for credibility using advanced machine learning. Share any news with me like:\n\n• 'Check this: [news headline]'\n• 'Is this real: [article text]'\n• 'Analyze: [news content]'",
                'type': 'default'
            }
    
    def _extract_news_text(self, message):
        """Extract news text from user message"""
        patterns = [
            'analyze this:', 'check this:', 'verify this:',
            'is this real:', 'is this fake:', 'analyze:',
            'check:', 'verify:'
        ]
        
        message_lower = message.lower()
        
        for pattern in patterns:
            if pattern in message_lower:
                start_index = message_lower.find(pattern) + len(pattern)
                news_text = message[start_index:].strip()
                if len(news_text) > 15:
                    return news_text
        
        # If no pattern found, check if entire message looks like news
        if len(message) > 30 and not any(word in message_lower for word in ['hello', 'hi', 'help']):
            return message
        
        return None
    
    def _format_production_response(self, analysis):
        """Format production model analysis into user-friendly response"""
        
        if analysis.get('model_info', {}).get('error'):
            return "❌ **Analysis Unavailable**\n\nMy analysis model is currently unavailable. Please verify this content manually with trusted news sources."
        
        score = analysis['credibility_score']
        risk_level = analysis['risk_level']
        
        # Create response with production model indicators
        if score >= 85:
            emoji = "✅"
            assessment = "HIGHLY CREDIBLE"
        elif score >= 70:
            emoji = "⚠️"
            assessment = "GENERALLY CREDIBLE"
        elif score >= 55:
            emoji = "❓"
            assessment = "UNCERTAIN CREDIBILITY"
        elif score >= 35:
            emoji = "⚠️"
            assessment = "LIKELY MISINFORMATION"
        else:
            emoji = "❌"
            assessment = "HIGHLY LIKELY MISINFORMATION"
        
        response = f"{emoji} **PRODUCTION AI ANALYSIS COMPLETE**\n\n"
        response += f"🎯 **Credibility Score: {score}/100**\n"
        response += f"📊 **Assessment: {assessment}**\n"
        response += f"⚠️ **Risk Level: {risk_level}**\n\n"
        
        response += f"🤖 **AI Model Details:**\n"
        response += f"• Prediction: {analysis['model_prediction']}\n"
        response += f"• Confidence: {analysis['model_confidence']}%\n"
        response += f"• Model Accuracy: {analysis['model_info'].get('accuracy', 'N/A')}\n\n"
        
        response += f"💡 **Recommendation:**\n{analysis['recommendation']}\n\n"
        response += f"🔍 **Detailed Analysis:**\n{analysis['explanation']}\n\n"
        response += f"⏰ **Analyzed:** {datetime.now().strftime('%H:%M:%S')}"
        
        return response

# Global chatbot service
production_chatbot_service = ProductionChatbotService()
