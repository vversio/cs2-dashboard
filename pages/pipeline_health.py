# Required packages:
# pip install streamlit pandas psycopg2-binary plotly sqlalchemy streamlit-shadcn-ui

import streamlit as st
import pandas as pd
import streamlit_shadcn_ui as ui
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from quant_engine import load_resolved_matches, load_health_data, load_extraction_audit, GLOBAL_CSS

st.set_page_config(layout="wide", page_title="Pipeline Health")
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

def render_page():
    # DB connectivity check
    _, db_connected = load_resolved_matches()

    if not db_connected:
        ui.alert(
            "Health diagnostics require a live database connection. The dashboard is currently running on demo data. Verify that the Postgres LXC container at 192.168.100.59:5432 is reachable.",
            key="health_demo_alert"
        )
        return

    unmatched_df, unmatched_results_count, _ = load_health_data()

    cols = st.columns(2)
    with cols[0]:
        ui.metric_card(
            title="Unmatched Odds Records", 
            content=str(len(unmatched_df)), 
            description="Odds with no result match", 
            key="health_kpi_1"
        )
    with cols[1]:
        ui.metric_card(
            title="Unmatched Results", 
            content=str(unmatched_results_count), 
            description="Results with no odds match", 
            key="health_kpi_2"
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">UNMATCHED ODDS RECORDS — ENTITY RESOLUTION FAILURES</div>', unsafe_allow_html=True)

    if not unmatched_df.empty:
        display_df = unmatched_df[['match_title', 'event_name', 'scraped_at']].copy()
        display_df['scraped_at'] = display_df['scraped_at'].astype(str)
        ui.table(data=display_df, maxHeight=400, key="unmatched_table")
    else:
        st.markdown("<div style='color: var(--text-muted);'>No unmatched odds records found.</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="match-card" style="font-family: 'IBM Plex Mono', monospace; font-size: 0.9rem; color: var(--text-secondary); line-height: 1.6; margin-top: 16px;">
        <div style="color: var(--accent-red); margin-bottom: 8px;">[ISSUE] ENTITY RESOLUTION MISMATCH</div>
        Team names differ between the odds scraper and results scraper because HLTV uses different name formats on different pages (e.g. "Natus Vincere" vs "NAVI").
        <br><br>
        <div style="color: var(--accent-blue); margin-bottom: 8px;">[FIX] ADD ALIAS MAPPINGS IN N8N</div>
        To fix this, add alias mappings in the n8n Code node to normalize the team names so they match during the JOIN.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">EXTRACTION LAYER AUDIT</div>', unsafe_allow_html=True)

    audit_df = load_extraction_audit()
    if not audit_df.empty:
        ui.table(data=audit_df, maxHeight=300, key="audit_table")
    else:
        st.markdown("<div style='color: var(--text-muted);'>No audit data available.</div>", unsafe_allow_html=True)

render_page()
