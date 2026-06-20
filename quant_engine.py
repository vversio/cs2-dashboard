# Required packages:
# pip install streamlit pandas psycopg2-binary plotly sqlalchemy streamlit-shadcn-ui

from sqlalchemy import create_engine, text
import pandas as pd
import pandas as pd

DB_USER = "postgres"
DB_PASS = "12345678"
DB_HOST = "192.168.100.99"
DB_PORT = "5432"
DB_NAME = "postgres"

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

:root {
    --bg-primary:    #080e1a;
    --bg-secondary:  #0f1e30;
    --bg-card:       #0c1828;
    --border:        #1e2d45;
    --accent-blue:   #3b82f6;
    --accent-cyan:   #06b6d4;
    --accent-green:  #22c55e;
    --accent-red:    #ef4444;
    --accent-amber:  #f59e0b;
    --text-primary:  #f1f5f9;
    --text-secondary:#94a3b8;
    --text-muted:    #475569;
}

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif !important;
}

.stApp { background-color: var(--bg-primary); }

[data-testid="stSidebar"] {
    background-color: #0c1525 !important;
    border-right: 1px solid var(--border) !important;
}

[data-testid="stMetricValue"] {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 1.5rem !important;
    color: var(--text-primary) !important;
}

.section-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    font-weight: 600;
    color: var(--accent-blue);
    letter-spacing: 2px;
    text-transform: uppercase;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 16px;
}

.match-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 14px 18px;
    margin-bottom: 8px;
    transition: border-color 0.2s ease;
}

.match-card:hover { border-color: var(--accent-blue); }

.prob-bar-container {
    width: 100%; height: 5px;
    background: var(--border);
    border-radius: 3px; overflow: hidden;
    margin: 8px 0 4px 0;
}

.vig-badge {
    display: inline-block;
    padding: 2px 8px; border-radius: 4px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px; font-weight: 500;
}

.vig-low    { background:rgba(34,197,94,0.15);  color:#4ade80; border:1px solid rgba(34,197,94,0.3); }
.vig-medium { background:rgba(245,158,11,0.15); color:#fbbf24; border:1px solid rgba(245,158,11,0.3); }
.vig-high   { background:rgba(239,68,68,0.15);  color:#f87171; border:1px solid rgba(239,68,68,0.3); }

footer, #MainMenu { display: none !important; }
</style>
"""

DEMO_DF = pd.DataFrame({
    'match_title':     ['NAVI vs FaZe','HEROIC vs NiP','Liquid vs MIBR',
                        'Vitality vs G2','FaZe vs Vitality','Astralis vs Cloud9',
                        'NaVi vs Liquid','G2 vs HEROIC'],
    'event_name':      ['BLAST Premier','Stake Ranked','CCT Europe',
                        'IEM Cologne','BLAST Premier','ESL Pro League',
                        'BLAST Premier','IEM Cologne'],
    'team_a':          ['NAVI','HEROIC','Liquid','Vitality','FaZe',
                        'Astralis','NaVi','G2'],
    'team_b':          ['FaZe','NiP','MIBR','G2','Vitality',
                        'Cloud9','Liquid','HEROIC'],
    'odds_a':          [1.85,1.43,1.40,1.60,2.20,1.55,1.70,1.90],
    'odds_b':          [1.95,2.90,2.83,2.30,1.65,2.45,2.15,1.90],
    'true_prob_a':     [48.7,67.1,66.9,59.0,42.8,61.2,55.8,50.0],
    'true_prob_b':     [51.3,32.9,33.1,41.0,57.2,38.8,44.2,50.0],
    'vig_percent':     [3.2,4.1,5.0,3.8,4.4,5.1,3.6,4.2],
    'extraction_layer':['layer1_regex']*8,
    'winner':          ['FaZe','HEROIC','Liquid','G2','Vitality',
                        'Astralis','Liquid','G2'],
    'loser':           ['NAVI','NiP','MIBR','Vitality','FaZe',
                        'Cloud9','NaVi','HEROIC'],
    'team_a_score':    [14,16,16,12,13,16,11,14],
    'team_b_score':    [16,9,8,16,16,10,16,16],
    'status':          ['completed']*8,
    'completed_at':    pd.date_range('2026-05-01', periods=8, freq='2d')
})

LIVE_DEMO_DF = pd.DataFrame({
    'match_title':     ['MOUZ vs Spirit', 'NIP vs fnatic', 'ENCE vs G2'],
    'event_name':      ['BLAST Premier', 'CCT Europe', 'IEM Cologne'],
    'team_a':          ['MOUZ', 'NIP', 'ENCE'],
    'team_b':          ['Spirit', 'fnatic', 'G2'],
    'odds_a':          [1.85, 2.10, 3.50],
    'odds_b':          [1.95, 1.70, 1.30],
    'true_prob_a':     [48.7, 45.2, 27.5],
    'true_prob_b':     [51.3, 54.8, 72.5],
    'vig_percent':     [3.2, 4.0, 5.1],
    'bookmaker_name':  ['HLTV']*3,
    'extraction_layer':['layer1_regex', 'layer1_regex', 'layer2_ollama'],
    'scraped_at':      pd.date_range('2026-06-06', periods=3, freq='2h')
})

def get_engine():
    return create_engine(
        f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
        connect_args={"connect_timeout": 5}
    )

def load_resolved_matches():
    query = text('''
        SELECT
            o.match_title,
            o.event_name,
            o.team_a,
            o.team_b,
            o.odds_a,
            o.odds_b,
            o.true_prob_a,
            o.true_prob_b,
            o.vig_percent,
            o.extraction_layer,
            r.winner,
            r.loser,
            r.team_a_score,
            r.team_b_score,
            r.status,
            r.scraped_at AS completed_at
        FROM scraped_cs2_odds o
        JOIN match_results r
            ON (o.match_title = r.match_title OR o.match_title = r.match_title_b)
            AND o.event_name = r.event_name
        WHERE r.status = 'completed'
        ORDER BY r.scraped_at DESC;
    ''')
    try:
        engine = get_engine()
        df = pd.read_sql(query, engine)
        return df, True
    except Exception as e:
        print(f"Database offline. Loading static showcase data. Error: {e}")
        df = pd.read_csv("data/resolved_matches_fallback.csv")
        return df, False

def load_live_odds():
    query = text('''
        SELECT
            match_title, event_name, team_a, team_b,
            odds_a, odds_b, true_prob_a, true_prob_b,
            vig_percent, bookmaker_name, extraction_layer, scraped_at
        FROM scraped_cs2_odds
        WHERE is_valid = true
        ORDER BY scraped_at DESC;
    ''')
    try:
        engine = get_engine()
        df = pd.read_sql(query, engine)
        return df, True
    except Exception as e:
        print(f"Database offline. Loading static showcase data. Error: {e}")
        df = pd.read_csv("data/live_odds_fallback.csv")
        return df, False

def load_health_data():
    query1 = text('''
        SELECT o.match_title, o.event_name, o.scraped_at
        FROM scraped_cs2_odds o
        WHERE NOT EXISTS (
            SELECT 1 FROM match_results r
            WHERE o.match_title = r.match_title
               OR o.match_title = r.match_title_b
        )
        ORDER BY o.scraped_at DESC
        LIMIT 20;
    ''')
    query2 = text('''
        SELECT COUNT(*) as count FROM match_results r
        WHERE NOT EXISTS (
            SELECT 1 FROM scraped_cs2_odds o
            WHERE r.match_title = o.match_title
               OR r.match_title_b = o.match_title
        );
    ''')
    try:
        engine = get_engine()
        unmatched_odds_df = pd.read_sql(query1, engine)
        unmatched_results_count = pd.read_sql(query2, engine).iloc[0]['count']
        return unmatched_odds_df, int(unmatched_results_count), True
    except Exception as e:
        print(f"Database offline. Loading static showcase data. Error: {e}")
        unmatched_odds_df = pd.read_csv("data/health_data_fallback.csv")
        with open("data/health_count_fallback.txt", "r") as f:
            unmatched_results_count = int(f.read().strip())
        return unmatched_odds_df, unmatched_results_count, False

def load_extraction_audit():
    query = text('''
        SELECT extraction_layer, COUNT(*) as count,
               ROUND(AVG(vig_percent)::numeric, 2) as avg_vig
        FROM scraped_cs2_odds
        WHERE is_valid = true
        GROUP BY extraction_layer;
    ''')
    try:
        engine = get_engine()
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        print(f"Database offline. Loading static showcase data. Error: {e}")
        df = pd.read_csv("data/extraction_audit_fallback.csv")
        return df

def compute_calibration_metrics(df):
    df = df.copy()
    df['favorite'] = df.apply(
        lambda x: x['team_a'] if x['true_prob_a'] > x['true_prob_b'] else x['team_b'],
        axis=1
    )
    df['favorite_implied_prob'] = df[['true_prob_a', 'true_prob_b']].max(axis=1)
    df['favorite_won'] = (df['favorite'] == df['winner']).astype(int)
    df['prob_bucket'] = pd.cut(df['favorite_implied_prob'], bins=range(40, 105, 5))
    return df