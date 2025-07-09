from textblob import TextBlob

class SentimentAnalyzer:
    """Enhanced sentiment analysis using TextBlob"""
    
    @staticmethod
    def analyze_sentiment(text):
        """
        Analyze sentiment of text and return sentiment label, confidence, and raw score
        """
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            
            # Convert polarity (-1 to 1) to confidence percentage
            confidence = min(abs(polarity) * 100, 100)
            
            # Determine sentiment label
            if polarity > 0.1:
                sentiment = 'positive'
            elif polarity < -0.1:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            return {
                'sentiment': sentiment,
                'confidence': round(confidence, 1),
                'raw_score': round(polarity, 3)
            }
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return {
                'sentiment': 'neutral',
                'confidence': 0,
                'raw_score': 0
            }
