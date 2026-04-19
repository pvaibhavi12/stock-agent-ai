import time
import os
import json
import math
from typing import List, Optional, Any, Callable, Dict

def validate_ticker(symbol: str) -> bool:
    """
    Validate that a stock ticker symbol is formatted correctly.
    """
    if not isinstance(symbol, str) or not symbol.strip():
        return False
        
    symbol = symbol.strip().upper()
    if 1 <= len(symbol) <= 10 and all(c.isalnum() or c in ".-^" for c in symbol):
        return True
    return False

def calculate_moving_average(prices: List[float], window: int) -> Optional[float]:
    """
    Calculate the simple moving average for a given list of prices and window size.
    """
    if not prices or window <= 0 or len(prices) < window:
        return None
        
    recent_prices = prices[-window:]
    return sum(recent_prices) / window

def calculate_volatility(prices: List[float]) -> Optional[float]:
    """
    Calculate the historical volatility (standard deviation of daily returns)
    for a given list of prices.
    """
    if not prices or len(prices) < 2:
        return None
        
    returns = []
    for i in range(1, len(prices)):
        prev = prices[i-1]
        curr = prices[i]
        if prev != 0:
            returns.append((curr - prev) / prev)
            
    if not returns:
        return None
        
    mean_return = sum(returns) / len(returns)
    variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
    std_dev = math.sqrt(variance)
    return std_dev

def safe_float(value: Any) -> Optional[float]:
    """
    Safely attempt to convert a value to a float.
    """
    if value is None:
        return None
        
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def format_currency(value: Any) -> str:
    """
    Format a given numeric value into a standard US currency string.
    """
    val = safe_float(value)
    if val is None:
        return "N/A"
        
    if val < 0:
        return f"-${abs(val):,.2f}"
    return f"${val:,.2f}"

def retry_request(func: Callable, *args, retries: int = 3, delay: int = 1, **kwargs) -> Any:
    """
    Execute a function and retry it upon failure.
    """
    last_exception = None
    
    for attempt in range(retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            if attempt < retries - 1:
                time.sleep(delay)
                
    if last_exception:
        raise last_exception

def load_memory_file() -> List[Dict[str, Any]]:
    """
    Load the historical analysis runs from memory.json.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    mem_path = os.path.join(base_dir, "memory.json")
    
    if not os.path.exists(mem_path):
        return []
        
    try:
        with open(mem_path, "r") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []

def save_memory_file(run_data: Dict[str, Any]) -> None:
    """
    Save a new historical analysis run to memory.json.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    mem_path = os.path.join(base_dir, "memory.json")
    
    history = load_memory_file()
    history.insert(0, run_data) # Add newest at the beginning
    
    # Keep only the last 50 runs to manage file size
    history = history[:50]
    
    try:
        with open(mem_path, "w") as f:
            json.dump(history, f, indent=4)
    except Exception as e:
        print(f"Failed to save to memory.json: {e}")
