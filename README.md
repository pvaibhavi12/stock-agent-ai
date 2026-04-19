# Agentic AI Stock Research Copilot

Agentic AI Stock Research Copilot is an autonomous multi-agent stock analysis platform built with **Python** and **Streamlit**. Instead of relying on a rigid linear workflow, it uses an **Agentic AI architecture** where specialized agents collaborate, adapt, recover from failures, and improve outputs based on real-time conditions.

When a user enters a stock ticker, a central **Supervisor Agent** creates a dynamic execution plan based on the selected research depth (Quick or Full) and risk profile. It then coordinates multiple expert agents:

- **Market Agent** – Analyzes price trends, momentum, and volatility using market data APIs such as Alpha Vantage and Finnhub.  
- **Fundamentals Agent** – Reviews valuation metrics, revenue growth, profitability, and financial health.  
- **News Agent** – Collects recent headlines and applies NLP sentiment analysis using TextBlob.  
- **Risk Agent** – Combines signals from all agents to generate a weighted Risk Score (1–10).  
- **Memo Agent** – Produces a professional research report with recommendation and rationale.

## Why It’s Agentic

This project goes beyond simple automation by adding autonomous decision-making:

- **Dynamic Planning** – The Supervisor adjusts tasks depending on user inputs and missing data.  
- **Reflection & Self-Correction** – If confidence is low or data is incomplete, new tasks are triggered automatically (e.g., fetch more news).  
- **Self-Healing Tools** – If one API fails or rate-limits, fallback providers are used automatically.  
- **Memory System** – Agents share runtime context and store completed analyses for future review.  
- **Confidence Scoring** – Each agent scores output quality, contributing to an overall confidence rating.  
- **Reasoned Recommendations** – Final Buy / Hold / Sell decisions include transparent explanations and bull/bear cases.

## Tech Stack

- Python  
- Streamlit  
- Pandas / NumPy  
- Alpha Vantage API  
- Finnhub API  
- TextBlob  
- SQLite / Local Storage

## Use Cases

- Retail investor research  
- Rapid stock screening  
- Educational finance projects  
- Demonstrating real-world Agentic AI systems
