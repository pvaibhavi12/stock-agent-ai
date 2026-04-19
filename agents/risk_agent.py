from typing import Dict, Any

class RiskAgent:
    """
    Agent responsible for calculating an overall risk score (1-10) for a potential investment
    based on aggregated market trend, fundamental valuation, and news sentiment.
    """
    
    def __init__(self):
        """Initialize the RiskAgent."""
        pass
        
    def analyze(self, trend: str, valuation: str, sentiment: str) -> Dict[str, Any]:
        """
        Evaluate risk based on the aggregated inputs from the other agents.
        """
        score = 5
        explanation_points = []
        confidence = 100
        
        if not trend or trend == "unknown":
            confidence -= 30
            explanation_points.append("Missing trend data increases uncertainty (+1 risk).")
            score += 1
            trend = "neutral"
            
        if not valuation or "unknown" in valuation.lower():
            confidence -= 30
            explanation_points.append("Missing valuation data increases uncertainty (+1 risk).")
            score += 1
            valuation = "fairly valued"
            
        if not sentiment or sentiment == "unknown":
            confidence -= 30
            explanation_points.append("Missing sentiment data increases uncertainty (+1 risk).")
            score += 1
            sentiment = "neutral"
        
        trend_lower = str(trend).lower()
        valuation_lower = str(valuation).lower()
        sentiment_lower = str(sentiment).lower()
        
        # Trend
        if "bearish" in trend_lower:
            score += 2
            explanation_points.append("Bearish market trend indicates downside momentum (+2 risk).")
        elif "bullish" in trend_lower:
            score -= 1
            explanation_points.append("Bullish market trend provides positive momentum (-1 risk).")
        else:
            explanation_points.append("Neutral trend provides average market risk (+0 risk).")
            
        # Valuation
        if "overvalued" in valuation_lower:
            score += 2
            explanation_points.append("Overvaluation increases the risk of a sharp price correction (+2 risk).")
        elif "undervalued" in valuation_lower:
            score -= 2
            explanation_points.append("Undervaluation provides a margin of safety against market shocks (-2 risk).")
        elif "unprofitable" in valuation_lower or "negative" in valuation_lower:
            score += 3
            explanation_points.append("Unprofitable operations significantly increase long-term risk (+3 risk).")
        else:
            explanation_points.append("Fair valuation indicates standard fundamental risk (+0 risk).")
            
        # Sentiment
        if "negative" in sentiment_lower:
            score += 2
            explanation_points.append("Negative news sentiment can drive near-term volatility and selloffs (+2 risk).")
        elif "positive" in sentiment_lower:
            score -= 1
            explanation_points.append("Positive news sentiment supports price stability (-1 risk).")
        else:
            explanation_points.append("Neutral sentiment indicates lack of major news-driven catalysts (+0 risk).")
            
        final_score = max(1, min(10, score))
        explanation_str = "Risk Evaluation Breakdown:\n- " + "\n- ".join(explanation_points)
        
        if final_score <= 3:
            category = "Low Risk"
        elif final_score <= 6:
            category = "Moderate Risk"
        elif final_score <= 8:
            category = "High Risk"
        else:
            category = "Extreme Risk"
            
        return {
            "status": "success",
            "confidence": max(0, confidence),
            "result": {
                "risk_score": final_score,
                "risk_category": category,
                "explanation": explanation_str,
                "inputs_evaluated": {
                    "trend": trend,
                    "valuation": valuation,
                    "sentiment": sentiment
                }
            }
        }
