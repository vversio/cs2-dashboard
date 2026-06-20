# Required packages:
# pip install streamlit pandas psycopg2-binary plotly sqlalchemy streamlit-shadcn-ui

import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit_shadcn_ui as ui
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from quant_engine import load_resolved_matches, compute_calibration_metrics, GLOBAL_CSS

st.set_page_config(layout="wide", page_title="Match Ledger")
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

@st.cache_data(ttl=600)
def fetch_and_compute():
    raw_df, connected = load_resolved_matches()
    df = compute_calibration_metrics(raw_df)
    return df, connected

df, db_connected = fetch_and_compute()

if not db_connected:
    ui.alert("Database connection failed. Operating in DEMO mode with fallback datasets.", key="ledger_demo_alert")

st.markdown('<div class="section-label">RESOLVED MATCH HISTORY</div>', unsafe_allow_html=True)

display_df = df.copy()
if not display_df.empty:
    display_df['completed_at'] = pd.to_datetime(display_df['completed_at']).dt.strftime('%Y-%m-%d %H:%M')
    display_df['favorite_implied_prob'] = display_df['favorite_implied_prob'].apply(lambda x: f"{x:.1f}%")
    display_df['vig_percent'] = display_df['vig_percent'].apply(lambda x: f"{x:.1f}%")
    display_df['favorite_won'] = display_df['favorite_won'].map({1: "✓ Yes", 0: "✗ No"})
    display_df['result'] = display_df.apply(
        lambda r: f"{r['winner']} {r['team_a_score']}–{r['team_b_score']} {r['loser']}", axis=1
    )

    table_cols = ['completed_at', 'match_title', 'event_name', 'result', 'favorite', 'favorite_implied_prob', 'favorite_won', 'vig_percent']
    display_df_table = display_df[table_cols]
    
    # We must convert to dict format for ui.table
    ui.table(data=display_df_table, maxHeight=580, key="ledger_table")
else:
    st.markdown("<div style='color: var(--text-muted);'>No resolved matches available.</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

if not df.empty:
    # Scatter plot
    df['outcome'] = df['favorite_won'].map({1: "Favorite Won", 0: "Upset"})
    
    fig = px.scatter(
        df,
        x="odds_a",
        y="odds_b",
        color="outcome",
        color_discrete_map={"Favorite Won": "#3b82f6", "Upset": "#ef4444"},
        hover_name="match_title"
    )
    
    fig.update_layout(
        title="Odds Space — Where Upsets Cluster",
        xaxis_title="Team A Odds",
        yaxis_title="Team B Odds",
        paper_bgcolor="#0f1e30",
        plot_bgcolor="#0f1e30",
        font=dict(family="IBM Plex Mono", color="#94a3b8", size=11),
        xaxis=dict(gridcolor="#1e2d45", zeroline=False),
        yaxis=dict(gridcolor="#1e2d45", zeroline=False),
        template="plotly_dark",
        hoverlabel=dict(bgcolor="#1e2d45", font_family="IBM Plex Mono"),
        margin=dict(t=30, b=50, l=40, r=20)
    )
    
    fig.update_traces(marker=dict(size=8, line=dict(width=1, color="#0f1e30")))
    
    st.plotly_chart(fig, width="stretch")
