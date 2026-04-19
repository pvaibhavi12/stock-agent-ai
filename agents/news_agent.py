from typing import Dict, Any

from utils.api import choose_data_source
from utils.helpers import validate_ticker

try:
    from textblob import TextBlob
except ImportError:
    raise ImportError("TextBlob is required. Please install it using: pip install textblob")

class NewsAgent:
    """
    Agent responsible for fetching the latest news headlines and using natural language
    processing to analyze sentiment and thematic topics.
    """
    
    def __init__(self):
        """Initialize the NewsAgent."""
        pass
        
    def analyze(self, symbol: str, fetch_more: bool = False) -> Dict[str, Any]:
        """
        Fetch news for the symbol and perform NLP sentiment analysis.
        If fetch_more is True, we might use a deeper search or different source (simulated here).
        """
        if not validate_ticker(symbol):
            return {"status": "error", "error": f"Invalid ticker symbol: {symbol}", "confidence": 0}
            
        news_data = choose_data_source("news", symbol)
        
        if "error" in news_data:
            return {
                "status": "error", 
                "error": f"NewsAgent failed to fetch data: {news_data['error']}",
                "confidence": 0
            }
            
        headlines = news_data.get("headlines", [])
        source = news_data.get("source", "Unknown")
        
        if not headlines:
            return {
                "status": "success",
                "confidence": 10, # Very low confidence if no news
                "result": {
                    "sentiment": "neutral",
                    "sentiment_score": 0.0,
                    "positive_themes": [],
                    "negative_themes": [],
                    "headline_summary": "No recent news headlines found.",
                    "headlines": [],
                    "source": source
                }
            }
            
        total_polarity = 0.0
        positive_themes = []
        negative_themes = []
        
        for item in headlines:
            title = item.get("title", "")
            if not title:
                continue
                
            blob = TextBlob(title)
            polarity = blob.sentiment.polarity
            total_polarity += polarity
            
            words = [word.lower() for word in blob.words if len(word) > 4]
            if polarity > 0.1:
                positive_themes.extend(words)
            elif polarity < -0.1:
                negative_themes.extend(words)
                
        valid_headlines_count = len(headlines)
        avg_score = total_polarity / valid_headlines_count if valid_headlines_count > 0 else 0.0
        
        sentiment = "neutral"
        if avg_score >= 0.15:
            sentiment = "positive"
        elif avg_score <= -0.15:
            sentiment = "negative"
            
        pos_unique = list(dict.fromkeys(positive_themes))[:5]
        neg_unique = list(dict.fromkeys(negative_themes))[:5]
        
        summary_lines = [f"- {hl.get('title')}" for hl in headlines[:5]]
        headline_summary = "\n".join(summary_lines)
        
        # Calculate confidence
        confidence = min(100, valid_headlines_count * 10)
        if fetch_more and valid_headlines_count > 5:
            confidence += 10 # More context = higher confidence
            
        return {
            "status": "success",
            "confidence": min(100, max(0, confidence)),
            "result": {
                "sentiment": sentiment,
                "sentiment_score": round(avg_score, 3),
                "positive_themes": pos_unique,
                "negative_themes": neg_unique,
                "headline_summary": headline_summary,
                "headlines": headlines,
                "source": source
            }
        }
