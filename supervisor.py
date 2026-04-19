from typing import Dict, Any, List
from datetime import datetime

from agents.market_agent import MarketAgent
from agents.fundamentals_agent import FundamentalsAgent
from agents.news_agent import NewsAgent
from agents.risk_agent import RiskAgent
from agents.memo_agent import MemoAgent
from utils.helpers import validate_ticker, save_memory_file

class SupervisorAgent:
    """
    The central orchestrator of the AI Stock Research Copilot.
    Uses an agentic loop: Goal -> Plan -> Execute Step -> Evaluate Result -> Decide Next Action -> Loop -> Final Memo.
    """
    
    def __init__(self):
        self.market_agent = MarketAgent()
        self.fundamentals_agent = FundamentalsAgent()
        self.news_agent = NewsAgent()
        self.risk_agent = RiskAgent()
        self.memo_agent = MemoAgent()
        
    def _create_plan(self, mode: str, risk_profile: str) -> List[str]:
        """Dynamically create the initial execution plan."""
        plan = ["fetch_price", "fetch_news", "compute_risk"]
        
        if mode in ["full", "compare"]:
            plan.insert(1, "fetch_fundamentals")
            
        if risk_profile == "high":
            plan.append("deep_risk_analysis")
            
        plan.append("generate_memo")
        return plan
        
    def _execute_step(self, step: str, symbol: str, memory: Dict[str, Any], logs: List[str]) -> None:
        """Execute a single step in the plan, updating memory."""
        logs.append(f"Executing step: {step}")
        
        if step == "fetch_price":
            res = self.market_agent.analyze(symbol)
            memory["price_data"] = res
            
        elif step == "fetch_price_fallback":
            res = self.market_agent.analyze(symbol, use_fallback=True)
            memory["price_data"] = res
            
        elif step == "fetch_fundamentals":
            res = self.fundamentals_agent.analyze(symbol)
            memory["fundamentals"] = res
            
        elif step == "fetch_news":
            res = self.news_agent.analyze(symbol)
            memory["sentiment"] = res
            
        elif step == "fetch_more_news":
            res = self.news_agent.analyze(symbol, fetch_more=True)
            memory["sentiment"] = res
            
        elif step == "compute_risk" or step == "deep_risk_analysis":
            trend = memory.get("price_data", {}).get("result", {}).get("trend", "unknown")
            valuation = memory.get("fundamentals", {}).get("result", {}).get("valuation_summary", "unknown")
            sentiment = memory.get("sentiment", {}).get("result", {}).get("sentiment", "unknown")
            
            res = self.risk_agent.analyze(trend=trend, valuation=valuation, sentiment=sentiment)
            memory["risk_score"] = res
            
        elif step == "generate_memo":
            # Memo logic is run outside the loop at the very end
            pass
            
    def _evaluate_and_reflect(self, step: str, memory: Dict[str, Any], plan: List[str], logs: List[str]) -> None:
        """Evaluate the output of the last step and dynamically alter the plan if necessary."""
        if step == "fetch_price":
            data = memory.get("price_data", {})
            if data.get("status") == "error":
                logs.append("Reflection: Price fetch failed. Injecting fallback fetch.")
                plan.insert(0, "fetch_price_fallback")
                
        elif step == "fetch_news":
            data = memory.get("sentiment", {})
            if data.get("confidence", 0) < 50:
                logs.append("Reflection: Low confidence in news sentiment. Fetching more news.")
                plan.insert(0, "fetch_more_news")
                
        elif step == "compute_risk":
            conf = memory.get("risk_score", {}).get("confidence", 100)
            if conf < 60 and "fetch_fundamentals" not in plan and "fundamentals" not in memory:
                logs.append("Reflection: High uncertainty in risk score due to missing fundamentals. Adding fundamentals fetch.")
                plan.insert(0, "compute_risk") # Re-evaluate risk later
                plan.insert(0, "fetch_fundamentals")

    def research_stock(self, symbol: str, mode: str = "quick", risk_profile: str = "medium") -> Dict[str, Any]:
        """
        Run the agentic multi-agent research pipeline.
        """
        logs = []
        if not validate_ticker(symbol):
            return {"success": False, "error": f"Invalid ticker symbol: '{symbol}'"}
            
        symbol = symbol.upper()
        logs.append(f"Goal received: Analyze {symbol} (Mode: {mode}, Risk Profile: {risk_profile})")
        
        # Initialize Runtime Memory
        memory = {}
        
        # Goal -> Plan
        plan = self._create_plan(mode, risk_profile)
        logs.append(f"Initial Plan generated: {plan}")
        
        # Execution Loop
        max_iterations = 15
        iterations = 0
        
        while plan and iterations < max_iterations:
            step = plan.pop(0)
            
            if step == "generate_memo":
                break # Memo is generated after loop
                
            # Execute Step
            self._execute_step(step, symbol, memory, logs)
            
            # Evaluate & Reflect (Conditional Nodes)
            self._evaluate_and_reflect(step, memory, plan, logs)
            
            iterations += 1
            
        if iterations >= max_iterations:
            logs.append("Warning: Max iterations reached. Forcing loop exit.")
            
        # Compile Overall Confidence
        conf_scores = [
            memory.get("price_data", {}).get("confidence", 0),
            memory.get("sentiment", {}).get("confidence", 0),
            memory.get("risk_score", {}).get("confidence", 0)
        ]
        if "fundamentals" in memory:
            conf_scores.append(memory.get("fundamentals", {}).get("confidence", 0))
            
        overall_conf = int(sum(conf_scores) / len(conf_scores)) if conf_scores else 0
        memory["overall_confidence"] = overall_conf
        logs.append(f"Calculated overall system confidence: {overall_conf}%")
        
        # Final Synthesis
        logs.append("Executing step: generate_memo")
        memo_output = self.memo_agent.generate_memo(symbol, memory)
        
        # Save to historical memory file
        try:
            run_data = {
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "mode": mode,
                "risk_profile": risk_profile,
                "recommendation": memo_output.get("result", {}).get("recommendation"),
                "risk_score": memo_output.get("result", {}).get("risk_score"),
                "confidence": overall_conf
            }
            save_memory_file(run_data)
            logs.append("Successfully saved run to memory.json")
        except Exception as e:
            logs.append(f"Failed to save history: {str(e)}")

        return {
            "success": True,
            "symbol": symbol,
            "memory": memory,
            "logs": logs,
            "research_memo": memo_output.get("result", {}).get("markdown", "")
        }
