# Required packages:
# pip install streamlit pandas psycopg2-binary plotly sqlalchemy streamlit-shadcn-ui

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import streamlit_shadcn_ui as ui
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from quant_engine import load_resolved_matches, compute_calibration_metrics, GLOBAL_CSS

st.set_page_config(layout="wide", page_title="Calibration")
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

@st.cache_data(ttl=600)
def fetch_and_compute():
    raw_df, db_connected = load_resolved_matches()
    df = compute_calibration_metrics(raw_df)
    return df, db_connected

df, db_connected = fetch_and_compute()

if not db_connected:
    ui.alert("Database connection failed. Operating in DEMO mode with fallback datasets.", key="calib_demo_alert")

resolved_matches_count = len(df)
favorite_win_rate = (df['favorite_won'].mean() * 100) if resolved_matches_count > 0 else 0
avg_implied_prob = df['favorite_implied_prob'].mean() if resolved_matches_count > 0 else 0
market_edge = favorite_win_rate - avg_implied_prob

edge_sign = "+" if market_edge >= 0 else "-"
edge_str = f"{edge_sign}{abs(market_edge):.1f}%"

st.markdown('<div class="section-label">MARKET CALIBRATION KPIs</div>', unsafe_allow_html=True)
cols = st.columns(4)
with cols[0]:
    ui.metric_card(title="Resolved Matches", content=str(resolved_matches_count), description="Total sample size", key="kpi_1")
with cols[1]:
    ui.metric_card(title="Favorite Win Rate", content=f"{favorite_win_rate:.1f}%", description="Actual performance", key="kpi_2")
with cols[2]:
    ui.metric_card(title="Avg Implied Prob", content=f"{avg_implied_prob:.1f}%", description="Bookmaker expectation", key="kpi_3")
with cols[3]:
    ui.metric_card(title="Market Edge", content=edge_str, description="Positive = bookmaker overvalues favorites", key="kpi_4")

st.markdown("<br>", unsafe_allow_html=True)

# Calibration Chart Prep
cal = df.groupby('prob_bucket', observed=False)['favorite_won'].agg(
    actual_win_rate=('mean'),
    matches=('count')
).reset_index()

cal['actual_win_rate'] = cal['actual_win_rate'] * 100
cal['midpoint'] = cal['prob_bucket'].apply(lambda b: (b.left + b.right) / 2)
cal['prob_bucket'] = cal['prob_bucket'].astype(str)
cal = cal[cal['matches'] >= 3].copy()

if cal.empty:
    ui.alert("Not enough resolved matches per probability bucket yet. Calibration requires at least 3 matches in a given probability range.", key="calib_empty_alert")
else:
    colors = []
    for _, row in cal.iterrows():
        if row['actual_win_rate'] > row['midpoint']:
            colors.append("#22c55e")
        else:
            colors.append("#ef4444")

    fig = go.Figure()
    
    # Bars
    fig.add_trace(go.Bar(
        x=cal['prob_bucket'],
        y=cal['actual_win_rate'],
        marker_color=colors,
        text=[f"n={n}" for n in cal['matches']],
        textposition='outside',
        name="Actual Win Rate"
    ))
    
    # Reference Line
    fig.add_trace(go.Scatter(
        x=cal['prob_bucket'],
        y=cal['midpoint'],
        mode='lines+markers',
        line=dict(color='#ef4444', dash='dash'),
        name="Perfect Calibration"
    ))

    fig.update_layout(
        title="Calibration Curve — Bookmaker Implied Probability vs Reality",
        xaxis_title="Implied Probability Bucket (%)",
        yaxis_title="Actual Win Rate (%)",
        paper_bgcolor="#0f1e30",
        plot_bgcolor="#0f1e30",
        font=dict(family="IBM Plex Mono", color="#94a3b8", size=11),
        xaxis=dict(gridcolor="#1e2d45", zeroline=False),
        yaxis=dict(gridcolor="#1e2d45", zeroline=False, range=[0, 105]),
        template="plotly_dark",
        hoverlabel=dict(bgcolor="#1e2d45", font_family="IBM Plex Mono"),
        margin=dict(t=30, b=50, l=40, r=20)
    )
    st.plotly_chart(fig, width="stretch")

st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-label">EXTRACTION LAYER AUDIT</div>', unsafe_allow_html=True)

layer_counts = df['extraction_layer'].value_counts().reset_index()
layer_counts.columns = ['extraction_layer', 'count']

fig_pie = go.Figure(data=[go.Pie(
    labels=layer_counts['extraction_layer'],
    values=layer_counts['count'],
    hole=0.4,
    marker=dict(colors=["#3b82f6", "#06b6d4"])
)])

fig_pie.update_layout(
    title="Extraction Layer Distribution",
    paper_bgcolor="#0f1e30",
    plot_bgcolor="#0f1e30",
    font=dict(family="IBM Plex Mono", color="#94a3b8", size=11),
    template="plotly_dark",
    hoverlabel=dict(bgcolor="#1e2d45", font_family="IBM Plex Mono"),
    margin=dict(l=40, r=40, t=60, b=40)
)
st.plotly_chart(fig_pie, width="stretch")
