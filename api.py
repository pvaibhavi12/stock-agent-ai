import os
import requests
import logging
from typing import Dict, Any
from dotenv import load_dotenv, find_dotenv

from utils.helpers import retry_request

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv(find_dotenv())

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=ENV_PATH, override=False)

ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

TIMEOUT = 10

def choose_data_source(task: str, symbol: str, use_fallback: bool = False) -> Dict[str, Any]:
    """
    Dynamically select the API tool to use for a given task.
    Supports primary and fallback sources.
    """
    if task == "price":
        if use_fallback:
            logger.info(f"Using fallback data source for {task} ({symbol})")
            return get_stock_price_finnhub(symbol)
        return get_stock_price(symbol)
        
    elif task == "fundamentals":
        return get_fundamentals(symbol)
        
    elif task == "news":
        return get_news(symbol)
        
    return {"error": f"Unknown task {task}"}

def get_stock_price(symbol: str) -> Dict[str, Any]:
    """Fetch stock daily prices from Alpha Vantage."""
    if not ALPHA_VANTAGE_API_KEY:
        return {"error": "ALPHA_VANTAGE_API_KEY is missing."}

    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol.upper(),
        "apikey": ALPHA_VANTAGE_API_KEY
    }

    try:
        response = retry_request(
            requests.get, url, retries=3, delay=2, params=params, timeout=TIMEOUT
        )
        response.raise_for_status()
        data = response.json()

        if "Error Message" in data:
            return {"error": data["Error Message"]}
        if "Information" in data:
            return {"error": data["Information"]}

        time_series = data.get("Time Series (Daily)", {})
        if not time_series:
            return {"error": "No stock data found."}

        dates = sorted(time_series.keys())
        prices = [float(time_series[d]["4. close"]) for d in dates]

        return {
            "latest_price": prices[-1],
            "prices": prices,
            "dates": dates,
            "source": "Alpha Vantage"
        }
    except Exception as e:
        logger.exception("Stock API Error")
        return {"error": str(e)}

def get_stock_price_finnhub(symbol: str) -> Dict[str, Any]:
    """Fallback: Fetch current price from Finnhub."""
    if not FINNHUB_API_KEY:
        return {"error": "FINNHUB_API_KEY is missing."}
        
    url = "https://finnhub.io/api/v1/quote"
    params = {
        "symbol": symbol.upper(),
        "token": FINNHUB_API_KEY
    }
    
    try:
        response = retry_request(
            requests.get, url, retries=3, delay=2, params=params, timeout=TIMEOUT
        )
        response.raise_for_status()
        data = response.json()
        
        current_price = data.get("c")
        if current_price is None or current_price == 0:
            return {"error": "Invalid quote data from Finnhub."}
            
        return {
            "latest_price": current_price,
            "prices": [current_price], # Mock history
            "dates": ["Latest"],
            "source": "Finnhub (Fallback)"
        }
    except Exception as e:
        logger.exception("Finnhub Quote API Error")
        return {"error": str(e)}

def get_fundamentals(symbol: str) -> Dict[str, Any]:
    """Fetch fundamentals from Finnhub."""
    if not FINNHUB_API_KEY:
        return {"error": "FINNHUB_API_KEY is missing."}

    url = "https://finnhub.io/api/v1/stock/metric"
    params = {
        "symbol": symbol.upper(),
        "metric": "all",
        "token": FINNHUB_API_KEY
    }

    try:
        response = retry_request(
            requests.get, url, retries=3, delay=2, params=params, timeout=TIMEOUT
        )
        response.raise_for_status()
        data = response.json()

        metric = data.get("metric", {})

        return {
            "pe_ratio": metric.get("peExclExtraTTM"),
            "market_cap": metric.get("marketCapitalization"),
            "revenue_growth": metric.get("revenueGrowthTTMYoy"),
            "source": "Finnhub"
        }
    except Exception as e:
        logger.exception("Fundamentals API Error")
        return {"error": str(e)}

def get_news(symbol: str) -> Dict[str, Any]:
    """Fetch latest stock news from NewsData.io."""
    if not NEWS_API_KEY:
        return {"error": "NEWS_API_KEY is missing."}

    url = "https://newsdata.io/api/1/news"
    params = {
        "q": symbol.upper(),
        "language": "en",
        "apikey": NEWS_API_KEY
    }

    try:
        response = retry_request(
            requests.get, url, retries=3, delay=2, params=params, timeout=TIMEOUT
        )
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "success":
            return {"error": data.get("message", "News API failed.")}

        results = data.get("results", [])
        headlines = []
        seen_titles = set()

        for article in results:
            title = article.get("title")
            if not title or title in seen_titles:
                continue
                
            seen_titles.add(title)

            headlines.append({
                "title": title,
                "source": article.get("source_id", "Unknown"),
                "url": article.get("link"),
                "published_at": article.get("pubDate")
            })

        return {"headlines": headlines[:10], "source": "NewsData.io"}
    except Exception as e:
        logger.exception("News API Error")
        return {"error": str(e)}