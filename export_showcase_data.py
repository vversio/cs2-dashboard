import os
import pandas as pd
from sqlalchemy import create_engine, text

# 1. Create a folder to hold the static data
os.makedirs('data', exist_ok=True)

print("Connecting to Proxmox database...")
# Using sqlalchemy as it's already used in the project
DB_USER = "postgres"
DB_PASS = "12345678"
DB_HOST = "192.168.100.59"
DB_PORT = "5432"
DB_NAME = "postgres"

engine = create_engine(
    f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
    connect_args={"connect_timeout": 5}
)

# 2. Export Live Odds
print("Exporting Live Odds...")
query_live_odds = text('''
    SELECT
        match_title, event_name, team_a, team_b,
        odds_a, odds_b, true_prob_a, true_prob_b,
        vig_percent, bookmaker_name, extraction_layer, scraped_at
    FROM scraped_cs2_odds
    WHERE is_valid = true
    ORDER BY scraped_at DESC;
''')
df_live = pd.read_sql_query(query_live_odds, engine)
df_live.to_csv('data/live_odds_fallback.csv', index=False)

# 3. Export Resolved Matches
print("Exporting Resolved Matches...")
query_resolved = text('''
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
df_resolved = pd.read_sql_query(query_resolved, engine)
df_resolved.to_csv('data/resolved_matches_fallback.csv', index=False)

# 4. Export Health Data
print("Exporting Health Data...")
query_health_data = text('''
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
df_health = pd.read_sql_query(query_health_data, engine)
df_health.to_csv('data/health_data_fallback.csv', index=False)

# Health Count
query_health_count = text('''
    SELECT COUNT(*) as count FROM match_results r
    WHERE NOT EXISTS (
        SELECT 1 FROM scraped_cs2_odds o
        WHERE r.match_title = o.match_title
           OR r.match_title_b = o.match_title
    );
''')
unmatched_results_count = pd.read_sql(query_health_count, engine).iloc[0]['count']
with open('data/health_count_fallback.txt', 'w') as f:
    f.write(str(int(unmatched_results_count)))

# 5. Export Extraction Audit
print("Exporting Extraction Audit...")
query_audit = text('''
    SELECT extraction_layer, COUNT(*) as count,
           ROUND(AVG(vig_percent)::numeric, 2) as avg_vig
    FROM scraped_cs2_odds
    WHERE is_valid = true
    GROUP BY extraction_layer;
''')
df_audit = pd.read_sql_query(query_audit, engine)
df_audit.to_csv('data/extraction_audit_fallback.csv', index=False)

engine.dispose()
print("Success! All static data exported to the data/ folder.")
