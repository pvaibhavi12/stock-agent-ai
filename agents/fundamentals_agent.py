from typing import Dict, Any

from utils.api import choose_data_source
from utils.helpers import validate_ticker, safe_float

class FundamentalsAgent:
    """
    Agent responsible for analyzing the fundamental financial metrics of a company,
    such as P/E ratio, market capitalization, and revenue growth.
    """
    
    def __init__(self):
        """Initialize the FundamentalsAgent."""
        pass
        
    def analyze(self, symbol: str) -> Dict[str, Any]:
        """
        Analyze the fundamental data for the given symbol to evaluate valuation.
        """
        if not validate_ticker(symbol):
            return {"status": "error", "error": f"Invalid ticker symbol: {symbol}", "confidence": 0}
            
        fundamentals_data = choose_data_source("fundamentals", symbol)
        
        if "error" in fundamentals_data:
            return {
                "status": "error", 
                "error": f"FundamentalsAgent failed to fetch data: {fundamentals_data['error']}",
                "confidence": 0
            }
            
        pe_ratio = safe_float(fundamentals_data.get("pe_ratio"))
        market_cap = safe_float(fundamentals_data.get("market_cap"))
        revenue_growth = safe_float(fundamentals_data.get("revenue_growth"))
        source = fundamentals_data.get("source", "Unknown")
        
        confidence = 100
        
        if pe_ratio is None:
            confidence -= 30
        if revenue_growth is None:
            confidence -= 20
        if market_cap is None:
            confidence -= 10
            
        valuation_summary = "neutral (fairly valued or insufficient data)"
        
        if pe_ratio is not None:
            if pe_ratio <= 0:
                valuation_summary = "unprofitable (negative earnings)"
            elif pe_ratio < 15:
                valuation_summary = "potentially undervalued"
            elif pe_ratio > 30:
                valuation_summary = "potentially overvalued"
            else:
                valuation_summary = "fairly valued"
                
        return {
            "status": "success",
            "confidence": max(0, confidence),
            "result": {
                "symbol": symbol.upper(),
                "pe_ratio": pe_ratio,
                "market_cap": market_cap,
                "revenue_growth": revenue_growth,
                "valuation_summary": valuation_summary,
                "source": source
            }
        }
