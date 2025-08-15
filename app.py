import streamlit as st
import pandas as pd
import numpy as np
import requests
import ta
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# Configurazione della pagina con tema professionale
st.set_page_config(
    page_title="Finora Pro Trading Terminal",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Iniezione CSS per stile Finora premium
st.markdown(f"""
<style>
    /* Font professionali */
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap');
    
    :root {{
        --primary: #2e86de;
        --secondary: #0c2461;
        --success: #27ae60;
        --danger: #e74c3c;
        --warning: #f39c12;
        --dark: #2c3e50;
        --light: #ecf0f1;
    }}
    
    * {{
        font-family: 'Montserrat', sans-serif;
    }}
    
    .stApp {{
        background: linear-gradient(135deg, #0c2461 0%, #1e3799 100%);
        color: #fff;
    }}
    
    .finora-header {{
        background: linear-gradient(90deg, var(--secondary) 0%, var(--primary) 100%);
        padding: 1.5rem 2rem;
        border-radius: 0 0 20px 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.25);
        margin-bottom: 2rem;
    }}
    
    .card {{
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.18);
        border: 1px solid rgba(255,255,255,0.1);
        margin-bottom: 1.5rem;
    }}
    
    .stButton>button {{
        background: linear-gradient(90deg, var(--primary) 0%, #1e90ff 100%);
        border: none;
        color: white;
        font-weight: 600;
        border-radius: 12px;
        padding: 0.8rem 1.5rem;
        transition: all 0.3s ease;
    }}
    
    .stButton>button:hover {{
        transform: translateY(-3px);
        box-shadow: 0 7px 14px rgba(30, 144, 255, 0.3);
    }}
    
    .stSelectbox, .stTextInput, .stSlider {{
        background: rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 0.5rem 1rem;
    }}
    
    .trading-signal-buy {{
        background: linear-gradient(90deg, rgba(39, 174, 96, 0.2) 0%, rgba(46, 204, 113, 0.2) 100%);
        border-left: 4px solid var(--success);
    }}
    
    .trading-signal-sell {{
        background: linear-gradient(90deg, rgba(231, 76, 60, 0.2) 0%, rgba(192, 57, 43, 0.2) 100%);
        border-left: 4px solid var(--danger);
    }}
    
    .trading-signal-wait {{
        background: linear-gradient(90deg, rgba(243, 156, 18, 0.2) 0%, rgba(241, 196, 15, 0.2) 100%);
        border-left: 4px solid var(--warning);
    }}
    
    .st-bb {{
        border-bottom: 1px solid rgba(255,255,255,0.1);
        padding-bottom: 1rem;
        margin-bottom: 1.5rem;
    }}
    
    .indicator-card {{
        background: rgba(0,0,0,0.2);
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
    }}
    
    .positive {{
        color: var(--success);
        font-weight: 700;
    }}
    
    .negative {{
        color: var(--danger);
        font-weight: 700;
    }}
</style>
""", unsafe_allow_html=True)

# Header con branding Finora
st.markdown("""
<div class="finora-header">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h1 style="margin: 0; color: white; font-weight: 700;">🚀 FINORA PRO TRADING TERMINAL</h1>
            <p style="margin: 0; font-size: 1.2rem; opacity: 0.9;">Smarter trades, less stress. Let Finora lead the way in all markets!</p>
        </div>
        <a href="https://t.me/FinoraEN_Bot" target="_blank">
            <button style="background: linear-gradient(90deg, #f39c12 0%, #f1c40f 100%); 
                        border: none; color: #2c3e50; padding: 0.8rem 1.5rem; 
                        border-radius: 12px; font-weight: 600; cursor: pointer;
                        display: flex; align-items: center; gap: 8px;">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path>
                </svg>
                Connect to Telegram Bot
            </button>
        </a>
    </div>
</div>
""", unsafe_allow_html=True)

# =====================================
# FUNZIONALITÀ AVANZATE FINORA
# =====================================

# Sidebar - Configurazione trading
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; margin-bottom: 1.5rem;">
        <h3 style="color: #3498db; margin-bottom: 0.5rem;">⚙️ TRADING PARAMETERS</h3>
        <div style="background: linear-gradient(90deg, #2e86de, #3498db); height: 3px; width: 50%; margin: 0 auto;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Selezione asset
    asset_type = st.selectbox("ASSET TYPE", ["Crypto", "Forex", "Stocks"], index=0)
    
    # Per Crypto
    if asset_type == "Crypto":
        @st.cache_data(ttl=3600)
        def get_coinbase_products():
            url = "https://api.exchange.coinbase.com/products"
            resp = requests.get(url)
            data = resp.json()
            pairs = [p["id"] for p in data if p["quote_currency"] == "USD" and p["trading_disabled"] is False]
            return sorted(pairs)
        
        coin_pairs = get_coinbase_products()
        product_id = st.selectbox("SELECT CRYPTO PAIR", coin_pairs, index=coin_pairs.index('BTC-USD') if 'BTC-USD' in coin_pairs else 0)
    
    # Timeframe strategico
    st.markdown("**STRATEGIC TIMEFRAME CONFIGURATION**")
    col1, col2 = st.columns(2)
    with col1:
        primary_tf = st.selectbox("PRIMARY TF", ["15m", "1H", "4H", "1D"], index=2)
    with col2:
        secondary_tf = st.selectbox("SECONDARY TF", ["1H", "4H", "1D", "1W"], index=1)
    
    # Risk management
    st.markdown("**RISK MANAGEMENT**")
    account_size = st.number_input("ACCOUNT SIZE ($)", min_value=100, value=5000, step=500)
    risk_percent = st.slider("RISK PER TRADE (%)", 0.5, 10.0, 2.0, step=0.5)
    risk_reward = st.selectbox("RISK/REWARD RATIO", ["1:1", "1:2", "1:3", "1:4"], index=2)
    
    # Strategia
    st.markdown("**TRADING STRATEGY**")
    strategy = st.selectbox("SELECT STRATEGY", ["Trend Following", "Breakout Trading", "Mean Reversion", "Ichimoku Cloud", "Finora AI Strategy"], index=4)
    
    st.markdown("---")
    if st.button("🚀 RUN FINORA ANALYSIS", use_container_width=True, key="analyze"):
        st.session_state.run_analysis = True
    else:
        st.session_state.run_analysis = False
    
    st.markdown("""
    <div style="text-align: center; margin-top: 1.5rem; font-size: 0.8rem; opacity: 0.7;">
        <p>Finora Pro Terminal v2.0</p>
        <p>© 2023 Finora Trading Technologies</p>
    </div>
    """, unsafe_allow_html=True)

# =====================================
# DASHBOARD PRINCIPALE
# =====================================

# Sezione Market Overview
st.markdown("""
<div class="card">
    <h2 style="margin-top: 0; display: flex; align-items: center; gap: 10px;">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#3498db" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="12" y1="1" x2="12" y2="23"></line>
            <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
        </svg>
        MARKET OVERVIEW
    </h2>
    
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; margin-top: 1.5rem;">
        <div class="indicator-card">
            <div style="font-size: 0.9rem; opacity: 0.8;">BTC/USD</div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 1.5rem; font-weight: 700;">$34,218</span>
                <span class="positive">+2.3%</span>
            </div>
        </div>
        
        <div class="indicator-card">
            <div style="font-size: 0.9rem; opacity: 0.8;">ETH/USD</div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 1.5rem; font-weight: 700;">$1,802</span>
                <span class="positive">+1.7%</span>
            </div>
        </div>
        
        <div class="indicator-card">
            <div style="font-size: 0.9rem; opacity: 0.8;">MARKET SENTIMENT</div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 1.5rem; font-weight: 700;">Bullish</span>
                <span style="background: #27ae60; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8rem;">HIGH</span>
            </div>
        </div>
        
        <div class="indicator-card">
            <div style="font-size: 0.9rem; opacity: 0.8;">VOLATILITY INDEX</div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 1.5rem; font-weight: 700;">42.3</span>
                <span style="background: #f39c12; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8rem;">MEDIUM</span>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Sezione principale
col1, col2 = st.columns([3, 1])

with col1:
    # Grafico avanzato
    st.markdown("""
    <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <h2 style="margin: 0; display: flex; align-items: center; gap: 10px;">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#3498db" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M1 1v22h22"></path>
                    <polyline points="1 13 8 8 13 13 18 8 23 12 23 21"></polyline>
                </svg>
                PRICE ANALYSIS: {product_id}
            </h2>
            <div style="display: flex; gap: 10px;">
                <button style="background: rgba(255,255,255,0.1); border: none; border-radius: 8px; padding: 5px 10px; color: #3498db;">Ichimoku</button>
                <button style="background: rgba(255,255,255,0.1); border: none; border-radius: 8px; padding: 5px 10px; color: #3498db;">Volume</button>
                <button style="background: rgba(255,255,255,0.1); border: none; border-radius: 8px; padding: 5px 10px; color: #3498db;">Fibonacci</button>
            </div>
        </div>
        
        <div style="height: 500px; background: rgba(0,0,0,0.2); border-radius: 12px; display: flex; justify-content: center; align-items: center;">
            <div style="text-align: center; opacity: 0.5;">
                <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M1 1v22h22"></path>
                    <polyline points="1 13 8 8 13 13 18 8 23 12 23 21"></polyline>
                </svg>
                <p>Interactive Price Chart</p>
                <p style="font-size: 0.9rem;">Run analysis to display advanced chart</p>
            </div>
        </div>
    </div>
    """.format(product_id=product_id if asset_type == "Crypto" else "EUR/USD"), unsafe_allow_html=True)
    
    # Trading Signals
    st.markdown("""
    <div class="card">
        <h2 style="margin-top: 0; display: flex; align-items: center; gap: 10px;">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#3498db" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <polyline points="12 6 12 12 16 14"></polyline>
            </svg>
            REAL-TIME TRADING SIGNALS
        </h2>
        
        <div class="trading-signal-buy" style="padding: 1.2rem; border-radius: 12px; margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                        <span style="background: #27ae60; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8rem;">BUY SIGNAL</span>
                        <strong>BTC/USD</strong>
                        <span>4H Timeframe</span>
                    </div>
                    <div style="font-size: 1.2rem; font-weight: 700;">Strong Bullish Momentum Detected</div>
                </div>
                <span style="font-size: 2rem; font-weight: 700;" class="positive">$34,250</span>
            </div>
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-top: 1rem;">
                <div>
                    <div style="font-size: 0.8rem; opacity: 0.8;">Entry Point</div>
                    <div style="font-weight: 700;">$34,100</div>
                </div>
                <div>
                    <div style="font-size: 0.8rem; opacity: 0.8;">Take Profit</div>
                    <div style="font-weight: 700; color: #27ae60;">$35,200</div>
                </div>
                <div>
                    <div style="font-size: 0.8rem; opacity: 0.8;">Stop Loss</div>
                    <div style="font-weight: 700; color: #e74c3c;">$33,800</div>
                </div>
                <div>
                    <div style="font-size: 0.8rem; opacity: 0.8;">Confidence</div>
                    <div style="font-weight: 700; color: #27ae60;">92%</div>
                </div>
            </div>
        </div>
        
        <div class="trading-signal-wait" style="padding: 1.2rem; border-radius: 12px; margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                        <span style="background: #f39c12; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8rem;">HOLD SIGNAL</span>
                        <strong>ETH/USD</strong>
                        <span>1H Timeframe</span>
                    </div>
                    <div style="font-size: 1.2rem; font-weight: 700;">Consolidation Phase - Wait for Breakout</div>
                </div>
                <span style="font-size: 2rem; font-weight: 700;">$1,802</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    # Finora AI Strategy
    st.markdown("""
    <div class="card">
        <h2 style="margin-top: 0; display: flex; align-items: center; gap: 10px;">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#3498db" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
                <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
            </svg>
            FINORA AI STRATEGY
        </h2>
        
        <div style="background: rgba(46, 134, 222, 0.15); padding: 1rem; border-radius: 12px; margin-bottom: 1.5rem;">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                <div style="background: #2e86de; width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M12 5.69l5 4.5V18h-2v-6H9v6H7v-7.81l5-4.5M12 3L2 12h3v8h6v-6h2v6h6v-8h3L12 3z"></path>
                    </svg>
                </div>
                <strong>Current Market Phase</strong>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 1.2rem; font-weight: 700;">Bullish Acceleration</span>
                <span style="background: #27ae60; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8rem;">CONFIRMED</span>
            </div>
        </div>
        
        <div style="margin-bottom: 1.5rem;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                <span>Trend Strength</span>
                <span style="font-weight: 700;" class="positive">Strong</span>
            </div>
            <div style="height: 8px; background: rgba(255,255,255,0.1); border-radius: 4px; overflow: hidden;">
                <div style="height: 100%; width: 92%; background: #27ae60; border-radius: 4px;"></div>
            </div>
        </div>
        
        <div style="margin-bottom: 1.5rem;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                <span>Momentum</span>
                <span style="font-weight: 700;" class="positive">Increasing</span>
            </div>
            <div style="height: 8px; background: rgba(255,255,255,0.1); border-radius: 4px; overflow: hidden;">
                <div style="height: 100%; width: 87%; background: #27ae60; border-radius: 4px;"></div>
            </div>
        </div>
        
        <div style="margin-bottom: 1.5rem;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                <span>Risk Level</span>
                <span style="font-weight: 700;" class="positive">Low</span>
            </div>
            <div style="height: 8px; background: rgba(255,255,255,0.1); border-radius: 4px; overflow: hidden;">
                <div style="height: 100%; width: 35%; background: #f39c12; border-radius: 4px;"></div>
            </div>
        </div>
        
        <div style="margin-top: 2rem; background: rgba(243, 156, 18, 0.15); padding: 1rem; border-radius: 12px;">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#f39c12" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="12" y1="8" x2="12" y2="12"></line>
                    <line x1="12" y1="16" x2="12.01" y2="16"></line>
                </svg>
                <strong>AI Trading Tip</strong>
            </div>
            <p>Consider scaling in positions during pullbacks to the $33,800 support level. Monitor volume for confirmation of continued bullish momentum.</p>
        </div>
    </div>
    
    <div class="card">
        <h2 style="margin-top: 0; display: flex; align-items: center; gap: 10px;">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#3498db" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="12" y1="1" x2="12" y2="23"></line>
                <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
            </svg>
            RISK MANAGER
        </h2>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1.5rem;">
            <div style="background: rgba(231, 76, 60, 0.15); padding: 1rem; border-radius: 12px;">
                <div style="font-size: 0.9rem; margin-bottom: 5px;">Max Risk</div>
                <div style="font-size: 1.4rem; font-weight: 700; color: #e74c3c;">${account_size * risk_percent/100:.2f}</div>
            </div>
            
            <div style="background: rgba(46, 204, 113, 0.15); padding: 1rem; border-radius: 12px;">
                <div style="font-size: 0.9rem; margin-bottom: 5px;">Potential Reward</div>
                <div style="font-size: 1.4rem; font-weight: 700; color: #27ae60;">${account_size * risk_percent/100 * int(risk_reward.split(':')[1]):.2f}</div>
            </div>
        </div>
        
        <div style="margin-bottom: 1.5rem;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                <span>Position Size</span>
                <span style="font-weight: 700;">0.85 BTC</span>
            </div>
            <div style="height: 8px; background: rgba(255,255,255,0.1); border-radius: 4px; overflow: hidden;">
                <div style="height: 100%; width: 65%; background: #2e86de; border-radius: 4px;"></div>
            </div>
        </div>
        
        <div style="background: rgba(52, 152, 219, 0.15); padding: 1rem; border-radius: 12px; margin-top: 1.5rem;">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#3498db" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"></circle>
                    <polyline points="12 6 12 12 16 14"></polyline>
                </svg>
                <strong>Smart Protection</strong>
            </div>
            <p>Auto-adjusting stops enabled. Exit 50% at R1 ($34,500), trail stop on remainder.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Sezione inferiore
st.markdown("""
<div class="card">
    <h2 style="margin-top: 0; display: flex; align-items: center; gap: 10px;">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#3498db" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="16 18 22 12 16 6"></polyline>
            <polyline points="8 6 2 12 8 18"></polyline>
        </svg>
        MULTI-TIMEFRAME CONFIRMATION
    </h2>
    
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem;">
        <div>
            <h3 style="display: flex; align-items: center; gap: 8px; margin-bottom: 1rem;">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#3498db" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"></circle>
                    <polyline points="12 6 12 12 16 14"></polyline>
                </svg>
                4H TIMEFRAME
            </h3>
            <div style="background: rgba(39, 174, 96, 0.1); padding: 1rem; border-radius: 12px; border-left: 4px solid #27ae60;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span>Ichimoku Cloud</span>
                    <span class="positive">Bullish</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span>RSI (14)</span>
                    <span>62.3 <span class="positive">▲</span></span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span>Volume Trend</span>
                    <span class="positive">Increasing</span>
                </div>
                <div style="display: flex; justify-content: space-between;">
                    <span>Finora Score</span>
                    <span style="font-weight: 700;" class="positive">8.7/10</span>
                </div>
            </div>
        </div>
        
        <div>
            <h3 style="display: flex; align-items: center; gap: 8px; margin-bottom: 1rem;">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#3498db" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"></circle>
                    <polyline points="12 6 12 12 16 14"></polyline>
                </svg>
                1D TIMEFRAME
            </h3>
            <div style="background: rgba(39, 174, 96, 0.1); padding: 1rem; border-radius: 12px; border-left: 4px solid #27ae60;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span>Ichimoku Cloud</span>
                    <span class="positive">Bullish</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span>MACD</span>
                    <span class="positive">Positive Crossover</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span>Key Level</span>
                    <span>$33,800 Support</span>
                </div>
                <div style="display: flex; justify-content: space-between;">
                    <span>Finora Score</span>
                    <span style="font-weight: 700;" class="positive">8.2/10</span>
                </div>
            </div>
        </div>
        
        <div>
            <h3 style="display: flex; align-items: center; gap: 8px; margin-bottom: 1rem;">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#3498db" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"></circle>
                    <polyline points="12 6 12 12 16 14"></polyline>
                </svg>
                1W TIMEFRAME
            </h3>
            <div style="background: rgba(243, 156, 18, 0.1); padding: 1rem; border-radius: 12px; border-left: 4px solid #f39c12;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span>Trend</span>
                    <span>Neutral</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span>Volume</span>
                    <span>Below Average</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span>Key Level</span>
                    <span>$36,200 Resistance</span>
                </div>
                <div style="display: flex; justify-content: space-between;">
                    <span>Finora Score</span>
                    <span style="font-weight: 700;">6.5/10</span>
                </div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Disclaimer
st.markdown("""
<div class="card" style="background: rgba(231, 76, 60, 0.1); border-left: 4px solid #e74c3c;">
    <div style="display: flex; gap: 12px;">
        <div style="color: #e74c3c;">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="8" x2="12" y2="12"></line>
                <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
        </div>
        <div>
            <h3 style="margin-top: 0; color: #e74c3c;">RISK DISCLAIMER</h3>
            <p>Trading involves significant risk of loss. The analysis provided by Finora Pro Terminal is for informational purposes only and should not be considered financial advice. Past performance is not indicative of future results. Always conduct your own research and consider consulting with a qualified financial advisor before making any trading decisions.</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
