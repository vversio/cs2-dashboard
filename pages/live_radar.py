# Required packages:
# pip install streamlit pandas psycopg2-binary plotly sqlalchemy streamlit-shadcn-ui

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import streamlit_shadcn_ui as ui
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from quant_engine import load_live_odds, GLOBAL_CSS

st.set_page_config(layout="wide", page_title="Live Radar")
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

@st.cache_data(ttl=600)
def fetch_live_odds():
    df, connected = load_live_odds()
    return df, connected

live_df, db_connected = fetch_live_odds()

if not db_connected:
    ui.alert("Database connection failed. Operating in DEMO mode with fallback datasets.", key="live_demo_alert")

with st.sidebar:
    st.markdown("<div style='font-family: IBM Plex Mono, monospace; font-weight: 600; color: var(--text-primary); margin-bottom: 8px;'>Max Bookmaker Vig (%)</div>", unsafe_allow_html=True)
    slider_res = ui.slider(default_value=[8.0], min_value=1.0, max_value=15.0, step=0.5, key="vig_slider")
    val = slider_res[0] if isinstance(slider_res, list) else slider_res

filtered = live_df[live_df['vig_percent'] <= val].copy()

matches_in_feed = f"{len(filtered)} / {len(live_df)}"
avg_vig = filtered['vig_percent'].mean() if not filtered.empty else 0
avg_vig_str = f"{avg_vig:.1f}%"

sharpest_line = "—"
if not filtered.empty:
    idx = filtered['vig_percent'].idxmin()
    sharpest_line = str(filtered.loc[idx, 'match_title'])[:24]

st.markdown('<div class="section-label">LIVE ODDS FEED</div>', unsafe_allow_html=True)
cols = st.columns(3)
with cols[0]:
    ui.metric_card(title="Matches in Feed", content=matches_in_feed, description="Filtered / Total", key="lr_metric_1")
with cols[1]:
    ui.metric_card(title="Avg Vig", content=avg_vig_str, description="Mean margin", key="lr_metric_2")
with cols[2]:
    ui.metric_card(title="Sharpest Line", content=sharpest_line, description="Lowest vig match", key="lr_metric_3")

st.markdown("<br>", unsafe_allow_html=True)

if not filtered.empty:
    chart_cols = st.columns([1])
    with chart_cols[0]:
        # Vig distribution chart
        colors = []
        for v in filtered['vig_percent']:
            if v <= 3.5:
                colors.append("#22c55e")
            elif v <= 6.5:
                colors.append("#f59e0b")
            else:
                colors.append("#ef4444")
                
        fig = go.Figure(data=[go.Bar(
            x=filtered['match_title'],
            y=filtered['vig_percent'],
            marker_color=colors,
        )])
        fig.update_layout(
            height=260,
            title="Vig Distribution",
            paper_bgcolor="#0f1e30",
            plot_bgcolor="#0f1e30",
            font=dict(family="IBM Plex Mono", color="#94a3b8", size=11),
            xaxis=dict(gridcolor="#1e2d45", zeroline=False),
            yaxis=dict(gridcolor="#1e2d45", zeroline=False),
            template="plotly_dark",
            hoverlabel=dict(bgcolor="#1e2d45", font_family="IBM Plex Mono"),
            margin=dict(t=30, b=50, l=40, r=20)
        )
        st.plotly_chart(fig, width="stretch")

st.markdown("<br>", unsafe_allow_html=True)

# Per-match probability cards
for _, row in filtered.iterrows():
    # Safe column extraction with fallbacks
    team_a  = row.get('team_a') if pd.notnull(row.get('team_a')) else row['match_title'].split(' vs ')[0].strip()
    team_b  = row.get('team_b') if pd.notnull(row.get('team_b')) else row['match_title'].split(' vs ')[1].strip()
    prob_a  = row.get('true_prob_a', 0.0) if pd.notnull(row.get('true_prob_a')) else 0.0
    prob_b  = row.get('true_prob_b', 0.0) if pd.notnull(row.get('true_prob_b')) else 0.0
    event   = row.get('event_name', '') if pd.notnull(row.get('event_name')) else ''
    vig     = row.get('vig_percent', 0.0) if pd.notnull(row.get('vig_percent')) else 0.0

    # Vig badge class
    if vig <= 3.5:
        vig_class, vig_label = "vig-low",    "LOW"
    elif vig <= 6.5:
        vig_class, vig_label = "vig-medium", "MED"
    else:
        vig_class, vig_label = "vig-high",   "HIGH"

    card_html = f"""
    <div class="match-card">
        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
            <div>
                <div class="match-teams">{team_a} <span style="color:#334155">vs</span> {team_b}</div>
                <div class="match-event">{event}</div>
            </div>
            <span class="vig-badge {vig_class}">VIG {vig:.1f}%</span>
        </div>
        <div class="prob-bar-container">
            <div style="height:100%; width:{prob_a:.1f}%; background-color:var(--accent-blue); float:left;"></div>
            <div style="height:100%; width:{prob_b:.1f}%; background-color:var(--accent-cyan); float:left;"></div>
        </div>
        <div style="display:flex; justify-content:space-between; font-family:'IBM Plex Mono',monospace; font-size:0.9rem; margin-top:4px;">
            <span style="color:var(--accent-blue);">{team_a} {prob_a:.1f}%</span>
            <span style="color:var(--accent-cyan);">{prob_b:.1f}% {team_b}</span>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
