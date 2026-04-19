from typing import Dict, Any

from utils.api import choose_data_source
from utils.helpers import calculate_moving_average, calculate_volatility, validate_ticker

class MarketAgent:
    """
    Agent responsible for analyzing the market data, calculating moving averages,
    volatility, and determining the short-term market trend for a given stock symbol.
    """
    
    def __init__(self):
        """Initialize the MarketAgent."""
        pass
        
    def analyze(self, symbol: str, use_fallback: bool = False) -> Dict[str, Any]:
        """
        Analyze the market data for the given symbol to identify pricing trends.
        """
        if not validate_ticker(symbol):
            return {"status": "error", "error": f"Invalid ticker symbol: {symbol}", "confidence": 0}
            
        market_data = choose_data_source("price", symbol, use_fallback)
        
        if "error" in market_data:
            return {
                "status": "error", 
                "error": f"MarketAgent failed to fetch data: {market_data['error']}",
                "confidence": 0
            }
            
        latest_price = market_data.get("latest_price")
        prices = market_data.get("prices", [])
        source = market_data.get("source", "Unknown")
        
        if not prices or latest_price is None:
            return {"status": "error", "error": "Insufficient market data.", "confidence": 0}
            
        ma_7 = calculate_moving_average(prices, 7)
        ma_30 = calculate_moving_average(prices, 30)
        volatility = calculate_volatility(prices)
        
        trend = "neutral"
        if ma_7 is not None and ma_30 is not None:
            if latest_price > ma_7 and ma_7 > ma_30:
                trend = "bullish"
            elif latest_price < ma_7 and ma_7 < ma_30:
                trend = "bearish"
                
        # Calculate confidence
        confidence = 100
        if len(prices) < 30:
            confidence -= 30 # Less data means less confidence in MA and Volatility
        if use_fallback:
            confidence -= 20 # Fallback usually means limited historical data
            
        return {
            "status": "success",
            "confidence": max(0, confidence),
            "result": {
                "symbol": symbol.upper(),
                "latest_price": latest_price,
                "prices": prices,
                "dates": market_data.get("dates", []),
                "moving_averages": {
                    "7_day": ma_7,
                    "30_day": ma_30
                },
                "volatility": volatility,
                "trend": trend,
                "total_data_points": len(prices),
                "source": source
            }
        }
