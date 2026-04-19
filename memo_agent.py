from typing import Dict, Any
from datetime import datetime

class MemoAgent:
    """
    Agent responsible for synthesizing data from all other agents into a
    comprehensive, easy-to-read, structured markdown stock research memo.
    """
    
    def __init__(self):
        """Initialize the MemoAgent."""
        pass
        
    def generate_memo(self, symbol: str, memory: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a comprehensive research memo based on the aggregated data in memory.
        """
        symbol = symbol.upper()
        date_today = datetime.now().strftime("%Y-%m-%d")
        
        market_res = memory.get("price_data", {}).get("result", {})
        fund_res = memory.get("fundamentals", {}).get("result", {})
        news_res = memory.get("sentiment", {}).get("result", {})
        risk_res = memory.get("risk_score", {}).get("result", {})
        
        market_conf = memory.get("price_data", {}).get("confidence", 0)
        fund_conf = memory.get("fundamentals", {}).get("confidence", 0)
        news_conf = memory.get("sentiment", {}).get("confidence", 0)
        risk_conf = memory.get("risk_score", {}).get("confidence", 0)
        overall_conf = memory.get("overall_confidence", 0)
        
        latest_price = market_res.get("latest_price", "N/A")
        if isinstance(latest_price, (int, float)):
            latest_price = f"${latest_price:,.2f}"
            
        trend = market_res.get("trend", "unknown")
        volatility = market_res.get("volatility")
        vol_str = f"{volatility:.2%}" if volatility else "N/A"
        
        pe_ratio = fund_res.get("pe_ratio", "N/A")
        market_cap = fund_res.get("market_cap", "N/A")
        valuation_summary = fund_res.get("valuation_summary", "unknown")
        
        sentiment = news_res.get("sentiment", "neutral")
        headlines = news_res.get("headlines", [])
        
        risk_score = risk_res.get("risk_score", "N/A")
        risk_category = risk_res.get("risk_category", "unknown")
        risk_explanation = risk_res.get("explanation", "No risk explanation provided.")
        
        bull_case = self._generate_bull_case(trend, valuation_summary, sentiment)
        bear_case = self._generate_bear_case(trend, valuation_summary, sentiment)
        recommendation = self._generate_recommendation(risk_score, trend, valuation_summary)
        
        memo = f"# AI Stock Research Memo: {symbol}\n"
        memo += f"**Date:** {date_today} | **Current Price:** {latest_price} | **Overall System Confidence:** {overall_conf}%\n\n"
        
        # SUMMARY
        memo += "## 1. Executive Summary\n"
        memo += f"Overall, {symbol} is exhibiting a **{trend}** market trend with **{sentiment}** news sentiment. "
        memo += f"From a fundamental perspective, it appears **{valuation_summary}**. "
        memo += f"The calculated risk profile is **{risk_category}** (Score: {risk_score}/10).\n\n"
        
        # AGENT CONFIDENCE
        memo += "## 2. Agent Confidence & Data Quality\n"
        memo += f"- **Market Agent:** {market_conf}% (Trend & Volatility)\n"
        memo += f"- **Fundamentals Agent:** {fund_conf}% (Valuation)\n"
        memo += f"- **News Agent:** {news_conf}% (Sentiment)\n"
        memo += f"- **Risk Agent:** {risk_conf}% (Scoring)\n\n"
        
        # TREND
        memo += "## 3. Market Action\n"
        memo += f"- **Direction:** Technical moving average analysis indicates a {trend} trend.\n"
        memo += f"- **Volatility:** {vol_str}\n\n"
        
        # FUNDAMENTALS
        memo += "## 4. Fundamentals\n"
        memo += f"- **P/E Ratio:** {pe_ratio}\n"
        memo += f"- **Market Cap (M):** {market_cap}\n"
        memo += f"- **Valuation Assessment:** {valuation_summary.title()}\n\n"
        
        # SENTIMENT
        memo += "## 5. Sentiment\n"
        memo += f"- **Overall News Sentiment:** {sentiment.title()}\n"
        if headlines:
            memo += "- **Top Headlines:**\n"
            for hl in headlines[:3]:
                title = hl.get("title", "Unknown Title")
                memo += f"  - {title}\n"
        memo += "\n"
        
        # RISK
        memo += "## 6. Risk Profile\n"
        memo += f"- **Risk Score:** {risk_score}/10 ({risk_category})\n"
        formatted_risk = risk_explanation.replace("\n-", "\n  -")
        memo += f"- **Risk Breakdown:** {formatted_risk}\n\n"
        
        # BULL CASE
        memo += "## 7. Bull Case\n"
        memo += f"{bull_case}\n\n"
        
        # BEAR CASE
        memo += "## 8. Bear Case\n"
        memo += f"{bear_case}\n\n"
        
        # RECOMMENDATION & REASONING
        memo += "## 9. Recommendation & Reasoning Path\n"
        memo += f"### **{recommendation.upper()}**\n"
        memo += f"**Reasoning Path:** The system arrived at this recommendation by first observing a {trend} price trend, "
        memo += f"which was then contextualized by the company's {valuation_summary} status. Finally, the {sentiment} news sentiment "
        memo += f"and a computed risk score of {risk_score}/10 confirmed the decision to {recommendation.upper()}. "
        if overall_conf < 70:
            memo += "However, due to lower system confidence, this recommendation carries higher uncertainty and requires human validation."
            
        return {
            "status": "success",
            "confidence": 100,
            "result": {
                "markdown": memo,
                "recommendation": recommendation,
                "risk_score": risk_score
            }
        }
        
    def _generate_bull_case(self, trend: str, valuation: str, sentiment: str) -> str:
        points = []
        if "bullish" in trend.lower():
            points.append("Strong positive price momentum is actively driving the stock upward.")
        if "undervalued" in valuation.lower():
            points.append("The stock currently trades at an attractive discount relative to its fundamentals.")
        if "positive" in sentiment.lower():
            points.append("A favorable news cycle and public sentiment are creating strong tailwinds.")
            
        if not points:
            return "The bull case relies heavily on an unexpected fundamental turnaround or broader macroeconomic recovery, as current metrics are unsupportive."
        return " ".join(points)
        
    def _generate_bear_case(self, trend: str, valuation: str, sentiment: str) -> str:
        points = []
        if "bearish" in trend.lower():
            points.append("Persistent technical weakness and selling pressure continue to drive the price lower.")
        if "overvalued" in valuation.lower() or "unprofitable" in valuation.lower():
            points.append("Stretched valuation multiples leave very little room for error and a high risk of a sharp correction.")
        if "negative" in sentiment.lower():
            points.append("A challenging news cycle is actively eroding investor confidence.")
            
        if not points:
            return "The bear case assumes that current positive metrics are fully priced in, and any slight operational miss will trigger a selloff."
        return " ".join(points)
        
    def _generate_recommendation(self, risk_score: Any, trend: str, valuation: str) -> str:
        try:
            score = float(risk_score)
        except (ValueError, TypeError):
            return "HOLD (Insufficient Data)"
            
        trend_lower = trend.lower()
        val_lower = valuation.lower()
        
        if score <= 4 and ("bullish" in trend_lower or "undervalued" in val_lower):
            return "BUY"
        elif score >= 7 and ("bearish" in trend_lower or "overvalued" in val_lower or "unprofitable" in val_lower):
            return "SELL"
        else:
            return "HOLD"
