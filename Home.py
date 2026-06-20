# Required packages:
# pip install streamlit pandas psycopg2-binary plotly sqlalchemy streamlit-shadcn-ui

# ═══════════════════════════════════════════════════════════
# CS2 QUANTITATIVE EDGE — LAUNCH INSTRUCTIONS
# ═══════════════════════════════════════════════════════════
# 1. Install dependencies:
#    pip install streamlit pandas psycopg2-binary plotly sqlalchemy streamlit-shadcn-ui
#
# 2. Ensure your Postgres LXC at 192.168.100.59:5432 is running
#    (dashboard degrades to demo data automatically if unreachable)
#
# 3. Launch from the project root directory:
#    streamlit run Home.py
#
# 4. Access at: http://localhost:8501
#    Or from another machine: http://<your-server-ip>:8501
#
# 5. To run in background on your i3 server:
#    nohup streamlit run Home.py --server.port 8501 &
#
# Page map:
#   Home           → Pipeline status and architecture overview
#   Calibration    → Is the bookmaker right? Charts and KPIs
#   Live Radar     → Current unresolved match odds feed
#   Match Ledger   → Full resolved match history
#   Pipeline Health → Entity resolution diagnostics
# ═══════════════════════════════════════════════════════════

import streamlit as st
import streamlit_shadcn_ui as ui
from quant_engine import GLOBAL_CSS, load_live_odds
import pandas as pd

st.set_page_config(layout="centered", page_title="CS2 Quant Edge", page_icon="🎯")
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

st.markdown("""
<div style="display: flex; align-items: baseline; gap: 12px; margin-bottom: -10px;">
    <h1 style="font-family: 'IBM Plex Mono', monospace; font-size: 2.5rem; margin: 0; color: var(--text-primary);">CS2 QUANTITATIVE EDGE</h1>
    <div style="display: flex; align-items: center; gap: 6px;">
        <div style="width: 10px; height: 10px; background-color: #22c55e; border-radius: 50%; animation: pulse 2s infinite;"></div>
        <span style="font-family: 'IBM Plex Mono', monospace; color: #22c55e; font-size: 0.9rem; font-weight: 600;">ACTIVE</span>
    </div>
</div>
<p style="color: var(--text-muted); font-size: 1.1rem; margin-bottom: 30px;">
    Autonomous odds intelligence · Implied probability engine · Market calibration
</p>

<style>
@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.4); }
    70% { box-shadow: 0 0 0 6px rgba(34, 197, 94, 0); }
    100% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
}
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=600)
def fetch_status():
    df, connected = load_live_odds()
    return df, connected

df, db_connected = fetch_status()

db_status = str(len(df)) if db_connected else "DEMO"
last_sync = "—"
if not df.empty:
    last_sync_val = df['scraped_at'].max()
    if pd.notnull(last_sync_val):
        last_sync = pd.to_datetime(last_sync_val).strftime('%Y-%m-%d %H:%M')

st.markdown('<div class="section-label">PIPELINE STATUS</div>', unsafe_allow_html=True)

cols = st.columns(4)
with cols[0]:
    ui.metric_card(title="Odds Scraper", content="ACTIVE", description="Every 2h via n8n", key="odds_status")
with cols[1]:
    ui.metric_card(title="Results Logger", content="ACTIVE", description="Nightly at 23:00", key="res_status")
with cols[2]:
    ui.metric_card(title="Database", content=db_status, description="192.168.100.59:5432", key="db_status")
with cols[3]:
    ui.metric_card(title="Last Sync", content=last_sync, description="Most recent scrape", key="sync_status")

st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-label">ARCHITECTURE SUMMARY</div>', unsafe_allow_html=True)

st.markdown("""
<div class="match-card" style="font-family: 'IBM Plex Mono', monospace; font-size: 0.9rem; color: var(--text-secondary); line-height: 1.6;">
    <div style="color: var(--accent-blue); margin-bottom: 8px;">[STAGE 1] SCRAPE</div>
    Two-layer extraction (Regex &rarr; Local LLM) pulls raw decimal odds from HLTV, bypassing anti-bot protection via FlareSolverr.
    <br><br>
    <div style="color: var(--accent-cyan); margin-bottom: 8px;">[STAGE 2] PROBABILITY MATH</div>
    Implied probabilities are calculated and the bookmaker vig (margin) is stripped to find the true normalized probability.
    <br><br>
    <div style="color: var(--accent-green); margin-bottom: 8px;">[STAGE 3] CALIBRATION</div>
    Nightly results are JOINed against historical odds to measure the real-world calibration of the market's implied probabilities.
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<div style='color: var(--text-muted); font-size: 0.9rem;'>Use the sidebar to navigate dashboard views.</div>", unsafe_allow_html=True)
