import streamlit as st
import yfinance as yf
import pandas as pd
import ta

# --- SYSTEM PAGE LAYOUT ---
st.set_page_config(page_title="SURGICAL // THEFXEMPIRE", layout="centered")

# --- CSS MASTER INJECTION WITH PREMIUM SVG WALLPAPER ---
st.markdown("""
    <style>
    .stApp { 
        background-color: #020617;
        background-image: 
            radial-gradient(circle at top, rgba(15, 23, 42, 0.94) 0%, #020617 100%),
            url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='60' height='60' viewBox='0 0 60 60'%3E%3Cpath d='M27 13h6v4h-6zm0 10h6v4h-6zm0 10h6v4h-6zM13 27h4v6h-4zm10 0h4v6h-4zm10 0h4v6h-4z' fill='%2300f0ff' fill-opacity='0.025' fill-rule='evenodd'/%3E%3C/svg%3E");
        background-repeat: repeat;
        color: #ffffff; 
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, sans-serif;
    }
    
    .profile-container { display: flex; justify-content: space-between; align-items: center; padding: 10px 0 25px 0; }
    .profile-meta h2 { font-size: 18px; margin: 0; color: #ffffff; font-weight: 600; }
    .profile-meta p { font-size: 12px; margin: 0; color: #64748b; }
    .status-ping { width: 10px; height: 10px; background-color: #00f0ff; border-radius: 50%; box-shadow: 0 0 10px #00f0ff; }

    .vitals-row { display: flex; justify-content: space-between; gap: 12px; margin-bottom: 25px; }
    .vital-card { flex: 1; background: rgba(15, 23, 42, 0.75); border: 1px solid rgba(0, 240, 255, 0.12); border-radius: 14px; padding: 15px; backdrop-filter: blur(10px); }
    .vital-card p { margin: 0; font-size: 11px; color: #94a3b8; letter-spacing: 0.5px; }
    .vital-card h3 { margin: 5px 0 0 0; font-size: 18px; color: #ffffff; font-weight: 700; }
    .neon-text-blue { color: #00f0ff !important; font-weight: bold; }
    
    .theater-container { background: rgba(15, 23, 42, 0.5); border: 1px solid rgba(255, 255, 255, 0.04); border-radius: 24px; padding: 30px 20px; text-align: center; margin-bottom: 25px; backdrop-filter: blur(10px); }
    .theater-title { font-size: 13px; color: #94a3b8; letter-spacing: 2px; font-weight: 600; margin-bottom: 25px; }
    .spotlight-wrapper { display: flex; justify-content: center; margin: 10px 0 25px 0; }
    
    .surgical-circle-active {
        width: 280px; height: 280px; border-radius: 50%;
        background: radial-gradient(circle, #0f172a 40%, #020617 100%);
        border: 3px solid #00f0ff; box-shadow: 0 0 40px rgba(0, 240, 255, 0.25);
        display: flex; flex-direction: column; justify-content: center; align-items: center;
    }
    .vitals-halo { font-size: 11px; color: #94a3b8; letter-spacing: 2px; font-weight: 700; margin-bottom: 8px; }
    .target-ticker { font-size: 34px; font-weight: 800; color: #ffffff; margin: 0; }
    .target-action { font-size: 13px; font-weight: 700; color: #00f0ff; letter-spacing: 1.5px; margin-top: 5px; }
    .target-activity { font-size: 11px; color: #64748b; margin-top: 10px; }

    .calc-box { background: rgba(15, 23, 42, 0.75); border: 1px solid rgba(255, 255, 255, 0.04); border-radius: 16px; padding: 20px; margin-top: 20px; backdrop-filter: blur(10px); }
    .prescription-box { background: rgba(0, 240, 255, 0.03); border-radius: 12px; border-left: 3px solid #00f0ff; padding: 12px 15px; text-align: left; margin-top: 15px; }
    
    .stButton>button { background: rgba(15, 23, 42, 0.8) !important; border: 1px solid rgba(255, 255, 255, 0.04) !important; color: #94a3b8 !important; border-radius: 10px !important; padding: 10px 0 !important; }
    .stButton>button:hover { border-color: #00f0ff !important; color: #00f0ff !important; }
    .active-btn>button { border-color: #00f0ff !important; color: #00f0ff !important; background: rgba(0, 240, 255, 0.05) !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# --- MAP ALL 24 LIQUID INSTRUMENTS & CONTRACT METRICS ---

# --- MAP ALL 24 LIQUID INSTRUMENTS & CONTRACT METRICS (MAJORS, MINORS & MACRO SECTORS) ---
ASSET_METRICS = {
    # --- GLOBAL MACRO COMMODITIES & INDICES ---
    "GOLD": {"ticker": "GC=F", "pip_val": 10.0, "label": "Per 0.1 Point ($10)"},
    "SILVER": {"ticker": "SI=F", "pip_val": 50.0, "label": "Per 0.01 Point ($50)"},
    "CRUDE OIL": {"ticker": "CL=F", "pip_val": 10.0, "label": "Per 0.01 Point ($10)"},
    "NASDAQ 100": {"ticker": "NQ=F", "pip_val": 20.0, "label": "Per Full Point ($20)"},
    "S&P 500": {"ticker": "ES=F", "pip_val": 50.0, "label": "Per Full Point ($50)"},
    "DOW JONES 30": {"ticker": "YM=F", "pip_val": 5.0, "label": "Per Full Point ($5)"},
    "BITCOIN": {"ticker": "BTC-USD", "pip_val": 1.0, "label": "Per Full Dollar ($1)"},
    "ETHEREUM": {"ticker": "ETH-USD", "pip_val": 1.0, "label": "Per Full Dollar ($1)"},
    
    # --- FOREX MAJORS ---
    "EUR/USD": {"ticker": "EURUSD=X", "pip_val": 10.0, "label": "Standard Lot Pip ($10)"},
    "GBP/USD": {"ticker": "GBPUSD=X", "pip_val": 10.0, "label": "Standard Lot Pip ($10)"},
    "USD/JPY": {"ticker": "JPY=X", "pip_val": 6.50, "label": "Standard Lot Pip (~$6.5)"},
    "AUD/USD": {"ticker": "AUDUSD=X", "pip_val": 10.0, "label": "Standard Lot Pip ($10)"},
    "USD/CHF": {"ticker": "CHF=X", "pip_val": 11.20, "label": "Standard Lot Pip (~$11.2)"},
    "USD/CAD": {"ticker": "CAD=X", "pip_val": 7.30, "label": "Standard Lot Pip (~$7.3)"},
    "NZD/USD": {"ticker": "NZDUSD=X", "pip_val": 10.0, "label": "Standard Lot Pip ($10)"},
    
    # --- FOREX MINORS & CROSSES ---
    "GBP/JPY": {"ticker": "GBPJPY=X", "pip_val": 6.50, "label": "Standard Lot Pip (~$6.5)"},
    "EUR/JPY": {"ticker": "EURJPY=X", "pip_val": 6.50, "label": "Standard Lot Pip (~$6.5)"},
    "EUR/GBP": {"ticker": "EURGBP=X", "pip_val": 12.80, "label": "Standard Lot Pip (~$12.8)"},
    "EUR/AUD": {"ticker": "EURAUD=X", "pip_val": 6.60, "label": "Standard Lot Pip (~$6.6)"},
    "GBP/AUD": {"ticker": "GBPAUD=X", "pip_val": 6.60, "label": "Standard Lot Pip (~$6.6)"},
    "AUD/JPY": {"ticker": "AUDJPY=X", "pip_val": 6.50, "label": "Standard Lot Pip (~$6.5)"},
    "EUR/CAD": {"ticker": "EURCAD=X", "pip_val": 7.30, "label": "Standard Lot Pip (~$7.3)"},
    "GBP/CAD": {"ticker": "GBPCAD=X", "pip_val": 7.30, "label": "Standard Lot Pip (~$7.3)"},
    "DAX 40": {"ticker": "GDAXI", "pip_val": 25.0, "label": "Per Full Point (€25)"}
}


# --- APPARATUS DATA ENGINE ---
@st.cache_data(ttl=30)
def scan_all_assets():
    active_surgeries = []
    all_patients = []
    historical_feeds = {}
    
    for name, config in ASSET_METRICS.items():
        try:
            data = yf.download(config["ticker"], period="5d", interval="15m", progress=False)
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
            
            close = data['Close'].squeeze()
            high = data['High'].squeeze()
            low = data['Low'].squeeze()
            
            atr = ta.volatility.average_true_range(high, low, close, window=14).iloc[-1]
            base = ta.volatility.average_true_range(high, low, close, window=150).iloc[-1]
            activity = (atr / base) * 100 if base > 0 else 100
            
            m15_ema = ta.trend.ema_indicator(close, window=20).iloc[-1]
            current_price = close.iloc[-1]
            bias = "⚡ BUY" if current_price > m15_ema else "⚡ SHORT"
            
            patient_info = {"Name": name, "Activity": activity, "Bias": bias, "Price": current_price}
            all_patients.append(patient_info)
            historical_feeds[name] = close.tail(30) # Capture last 30 data points for trend charting
            
            if activity > 115:
                active_surgeries.append(patient_info)
        except:
            continue
            
    return sorted(active_surgeries, key=lambda x: x['Activity'], reverse=True), sorted(all_patients, key=lambda x: x['Activity'], reverse=True), historical_feeds

active_ops, matrix_deck, chart_feeds = scan_all_assets()

# --- INITIALIZE SESSSION PERSISTENCE ---
if "active_tab" not in st.session_state: st.session_state.active_tab = "🩺 Ward"
if "surgery_log" not in st.session_state: st.session_state.surgery_log = []
if "last_alert_asset" not in st.session_state: st.session_state.last_alert_asset = None

# Automatically log active breakouts into history log
for op in active_ops:
    if op['Name'] not in [log['Name'] for log in st.session_state.surgery_log]:
        st.session_state.surgery_log.insert(0, {"Name": op['Name'], "Bias": op['Bias'], "Activity": op['Activity']})

# --- AUDIO ALERT MECHANICS ---
AUDIO_URL = "https://actions.google.com/sounds/v1/science_fiction/glitchy_digital_opening.ogg"
def trigger_surgical_alarm(asset_name):
    if st.session_state.last_alert_asset != asset_name:
        st.session_state.last_alert_asset = asset_name
        st.markdown(f'<iframe src="{AUDIO_URL}" allow="autoplay" style="display:none;"></iframe>', unsafe_allow_html=True)

# --- PROFILE CANVAS HEADER ---
st.markdown("""
    <div class="profile-container">
        <div class="profile-meta">
            <h2>Gozan Bless</h2>
            <p>Primary Strategist // THEFXEMPIRE</p>
        </div>
        <div class="status-ping"></div>
    </div>
""", unsafe_allow_html=True)

# --- TOP STAT BAR ---
st.markdown(f"""
    <div class="vitals-row">
        <div class="vital-card">
            <p>TOTAL MONITORED</p>
            <h3>24 Assets</h3>
        </div>
        <div class="vital-card">
            <p>ACTIVE SURGERIES</p>
            <h3 class="neon-text-blue">{len(active_ops)} Live</h3>
        </div>
        <div class="vital-card">
            <p>RISK PROTOCOL</p>
            <h3>0.3% - 0.6%</h3>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- TAB VIEW ROUTING ---
if st.session_state.active_tab == "🩺 Ward":
    st.markdown('<div class="theater-title" style="text-align:center;">THE OPERATING THEATER</div>', unsafe_allow_html=True)
    
    if active_ops:
        primary = active_ops[0]
        trigger_surgical_alarm(primary['Name'])
        is_bullish = "BUY" in primary['Bias']
        v_color = "#00f0ff" if is_bullish else "#ff3b3b"
        trend_tag = "🟢" if is_bullish else "🔴"
        
        st.markdown(f"""
            <div class="theater-container">
                <div class="spotlight-wrapper">
                    <div class="surgical-circle-active" style="border-color: {v_color}; box-shadow: 0 0 40px {v_color}40;">
                        <div class="vitals-halo">12M{trend_tag} 1M{trend_tag} 1D{trend_tag} M15{trend_tag}</div>
                        <div class="target-ticker">{primary['Name']}</div>
                        <div class="target-action" style="color: {v_color};">{primary['Bias']} LIQUIDITY REQUIRED</div>
                        <div class="target-activity">ACTIVITY INDEX: {primary['Activity']:.1f}% 🔥</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.info("All assets are stable. Select target manually below to run risk calculations.")
        primary = {"Name": matrix_deck[0]['Name'] if matrix_deck else "EUR/USD"}

    # --- AUTO-CONFIGURED CALCULATOR INTERFACE ---
    st.markdown('<div class="calc-box">', unsafe_allow_html=True)
    st.subheader("📐 Precision Surgical Calculator")
    
    # Let user change target on the fly
    calc_target = st.selectbox("Target Patient Under Operation", list(ASSET_METRICS.keys()), index=list(ASSET_METRICS.keys()).index(primary['Name']))
    selected_unit = ASSET_METRICS[calc_target]
    
    c1, c2 = st.columns(2)
    with c1:
        equity = st.number_input("Account Balance ($)", min_value=100.0, value=100000.0, step=1000.0)
        risk_pct = st.slider("Surgical Risk Threshold (%)", 0.3, 0.6, 0.5, step=0.05)
    with c2:
        stop_loss_pips = st.number_input("Stop Loss Distance (Pips/Points)", min_value=0.1, value=15.0, step=1.0)
        # Automatic contract sizing hook
        pip_value = st.number_input(f"Pip Value ({selected_unit['label']})", value=selected_unit['pip_val'], disabled=True)
        
    risk_cash = equity * (risk_pct / 100.0)
    calculated_lots = risk_cash / (stop_loss_pips * pip_value) if stop_loss_pips > 0 else 0.0
    
    st.markdown(f"""
        <div class="prescription-box">
            <strong>🏥 PATIENT PRESCRIPTION SIZE ({calc_target}):</strong>
            <p>• Max Risk Allocation: <b>${risk_cash:,.2f} USD</b><br/>
            • Precise Volume Execution: <span style="color:#00f0ff; font-weight:bold; font-size:16px;">{calculated_lots:.2f} Standard Lots</span></p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.active_tab == "📋 Charts":
    st.subheader("📈 Operating Analytics & Volatility Charts")
    
    # Pick asset trend to visualize
    select_chart = st.selectbox("Select Patient Trend Stream", list(ASSET_METRICS.keys()))
    if select_chart in chart_feeds:
        # Generate a premium dark neon-themed line chart
        chart_data = pd.DataFrame(chart_feeds[select_chart])
        chart_data.columns = ["Price Level"]
        st.line_chart(chart_data, color="#00f0ff")
        
    st.write("---")
    st.subheader("📋 Complete Matrix Registry Ward")
    df_matrix = pd.DataFrame(matrix_deck)
    df_matrix.columns = ["Patient Asset", "Volatility Index", "Suggested Vector Bias", "Last Feed Price"]
    st.dataframe(df_matrix.style.format({"Volatility Index": "{:.1f}%", "Last Feed Price": "{:,.4f}"}), use_container_width=True)

elif st.session_state.active_tab == "⚙️ Options":
    st.subheader("⚙️ System Configuration Logs")
    
    # Clear logs trigger
    if st.button("Clear Emergency Alert Logs"):
        st.session_state.surgery_log = []
        st.rerun()
        
    st.write("### 🚨 Logged Incidents Matrix")
    if st.session_state.surgery_log:
        st.table(pd.DataFrame(st.session_state.surgery_log))
    else:
        st.write("No critical surgeries logged during this session.")

# --- NAVIGATION FOOTER DOCK NAVIGATION ---
st.write("<br/>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('<div class="active-btn">' if st.session_state.active_tab == "🩺 Ward" else '<div>', unsafe_allow_html=True)
    if st.button("🩺 Ward", use_container_width=True): st.session_state.active_tab = "🩺 Ward"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="active-btn">' if st.session_state.active_tab == "📋 Charts" else '<div>', unsafe_allow_html=True)
    if st.button("📋 Charts", use_container_width=True): st.session_state.active_tab = "📋 Charts"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="active-btn">' if st.session_state.active_tab == "⚙️ Options" else '<div>', unsafe_allow_html=True)
    if st.button("⚙️ Options", use_container_width=True): st.session_state.active_tab = "⚙️ Options"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)