import streamlit as st
import plotly.graph_objects as go
from agents.supervisor import SupervisorAgent
from utils.helpers import load_memory_file

st.set_page_config(
    page_title="AI Stock Research Copilot",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header { font-size: 2.5rem; font-weight: 700; color: #1E3A8A; margin-bottom: 0; }
    .sub-header { font-size: 1.1rem; color: #6B7280; margin-bottom: 2rem; }
    .metric-container { background-color: #F3F4F6; border-radius: 8px; padding: 1rem; }
    .log-panel { background-color: #111827; color: #10B981; font-family: monospace; padding: 10px; border-radius: 5px; max-height: 200px; overflow-y: auto; }
</style>
""", unsafe_allow_html=True)

if 'supervisor' not in st.session_state:
    st.session_state.supervisor = SupervisorAgent()

with st.sidebar:
    st.markdown("### 🤖 Copilot Settings")
    st.markdown("Configure the autonomous AI agent system.")
    
    ticker_input = st.text_input("Stock Ticker Symbol", placeholder="e.g., TSLA").upper()
    print(f"[DEBUG] Streamlit UI - Input Ticker: '{ticker_input}'")
    
    analysis_mode = st.selectbox(
        "Analysis Mode",
        options=["quick", "full"],
        index=1,
        help="Quick mode skips fundamentals. Full mode runs the complete pipeline."
    )
    
    risk_profile = st.selectbox(
        "User Risk Profile",
        options=["low", "medium", "high"],
        index=1,
        help="Adjusts how deep the risk analysis goes."
    )
    
    analyze_button = st.button("🚀 Dispatch Agents", use_container_width=True)
    
    st.markdown("---")
    st.markdown("### 🗃️ Analysis History")
    history = load_memory_file()
    if history:
        for idx, run in enumerate(history[:5]):
            with st.expander(f"{run['symbol']} - {run.get('timestamp', '')[:10]}"):
                st.write(f"**Recommendation:** {run.get('recommendation', 'N/A')}")
                st.write(f"**Risk Score:** {run.get('risk_score', 'N/A')}/10")
                st.write(f"**Confidence:** {run.get('confidence', 'N/A')}%")
    else:
        st.write("No history available.")

st.markdown("<h1 class='main-header'>📈 Agentic AI Stock Copilot</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>Goal-Driven Autonomous Multi-Agent Orchestration</p>", unsafe_allow_html=True)

if analyze_button:
    if not ticker_input:
        st.warning("⚠️ Please enter a valid stock ticker symbol.")
    else:
        with st.spinner(f"🔍 Orchestrating agents to analyze {ticker_input}..."):
            print(f"[DEBUG] Streamlit UI - Passing '{ticker_input}' to SupervisorAgent")
            result = st.session_state.supervisor.research_stock(
                symbol=ticker_input,
                mode=analysis_mode,
                risk_profile=risk_profile
            )
            
            if not result.get("success"):
                st.error(f"❌ Error: {result.get('error', 'An unknown error occurred.')}")
            else:
                logs = result.get("logs", [])
                memory = result.get("memory", {})
                
                # Execution Logs Panel
                st.markdown("### 🖥️ Agent Execution Logs")
                log_html = "<div class='log-panel'>" + "<br>".join([f"> {log}" for log in logs]) + "</div>"
                st.markdown(log_html, unsafe_allow_html=True)
                
                st.markdown("---")
                
                # Extracted Memory Output
                market_data = memory.get("price_data", {}).get("result", {})
                fundamentals = memory.get("fundamentals", {}).get("result", {})
                risk = memory.get("risk_score", {}).get("result", {})
                overall_conf = memory.get("overall_confidence", 0)
                
                st.success(f"✅ Agentic analysis completed with **{overall_conf}%** confidence!")
                
                col1, col2, col3, col4 = st.columns(4)
                
                latest_price = market_data.get("latest_price")
                price_str = f"${latest_price:,.2f}" if isinstance(latest_price, (int, float)) else "N/A"
                
                pe_ratio = fundamentals.get("pe_ratio")
                pe_str = f"{pe_ratio:.2f}" if isinstance(pe_ratio, (int, float)) else "N/A"
                
                market_cap = fundamentals.get("market_cap")
                mc_str = f"${market_cap:,.0f}M" if isinstance(market_cap, (int, float)) else "N/A"
                
                risk_score = risk.get("risk_score", "N/A")
                
                with col1:
                    st.metric(label="Latest Price", value=price_str, delta=f"Data: {market_data.get('source', 'N/A')}", delta_color="off")
                with col2:
                    st.metric(label="P/E Ratio", value=pe_str, delta=f"Data: {fundamentals.get('source', 'N/A')}", delta_color="off")
                with col3:
                    st.metric(label="Market Cap", value=mc_str)
                with col4:
                    st.metric(label="Risk Score", value=f"{risk_score}/10")
                    
                st.markdown("---")
                
                col_chart, col_memo = st.columns([1.2, 1])
                
                with col_chart:
                    st.markdown(f"### 📊 Price Action & Trend")
                    prices = market_data.get("prices", [])
                    dates = market_data.get("dates", [])
                    
                    if len(prices) > 1 and len(dates) > 1:
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=dates, y=prices, mode='lines+markers', name='Price',
                            line=dict(color='#2563EB', width=2), marker=dict(size=3, color='#1E3A8A'),
                            fill='tozeroy', fillcolor='rgba(37, 99, 235, 0.1)'
                        ))
                        fig.update_layout(
                            xaxis_title="Date", yaxis_title="Price (USD)",
                            template="plotly_white", margin=dict(l=0, r=0, t=10, b=0),
                            hovermode="x unified", plot_bgcolor='rgba(0,0,0,0)'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Insufficient historical price data for charting.")
                        
                with col_memo:
                    st.markdown("### 📝 Synthesized Research Memo")
                    with st.container(height=550, border=True):
                        st.markdown(result.get("research_memo", "Memo generation failed."))

else:
    st.info("👈 Configure your copilot in the sidebar and dispatch the agents!")
    
    st.markdown("### 🧠 Agentic Architecture")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown("#### 🎯 Planning Phase")
        st.markdown("The Supervisor parses the user's goal, risk profile, and desired depth to formulate a dynamic execution plan.")
    with col_b:
        st.markdown("#### 🔄 Iterative Execution")
        st.markdown("Agents are deployed to fetch data. Results are evaluated mid-flight to trigger reflection and self-correction.")
    with col_c:
        st.markdown("#### 🛠️ Self-Healing & Memory")
        st.markdown("If a primary data source fails, the system switches to a fallback. All runs are logged into a persistent memory store.")
