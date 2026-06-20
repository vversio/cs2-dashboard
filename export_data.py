import pandas as pd
from sqlalchemy import create_engine, text
import os

DB_USER = "postgres"
DB_PASS = "12345678"
DB_HOST = "192.168.100.59"
DB_PORT = "5432"
DB_NAME = "postgres"

def get_engine():
    return create_engine(
        f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
        connect_args={"connect_timeout": 5}
    )

os.makedirs('data', exist_ok=True)
engine = get_engine()

# 1. resolved_matches
query1 = text('''
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
df1 = pd.read_sql(query1, engine)
df1.to_csv('data/resolved_matches_fallback.csv', index=False)
print("Exported resolved_matches_fallback.csv")

# 2. live_odds
query2 = text('''
    SELECT
        match_title, event_name, team_a, team_b,
        odds_a, odds_b, true_prob_a, true_prob_b,
        vig_percent, bookmaker_name, extraction_layer, scraped_at
    FROM scraped_cs2_odds
    WHERE is_valid = true
    ORDER BY scraped_at DESC;
''')
df2 = pd.read_sql(query2, engine)
df2.to_csv('data/live_odds_fallback.csv', index=False)
print("Exported live_odds_fallback.csv")

# 3. health_data (unmatched odds) and unmatched results count
query3 = text('''
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
query4 = text('''
    SELECT COUNT(*) as count FROM match_results r
    WHERE NOT EXISTS (
        SELECT 1 FROM scraped_cs2_odds o
        WHERE r.match_title = o.match_title
           OR r.match_title_b = o.match_title
    );
''')
df3 = pd.read_sql(query3, engine)
df3.to_csv('data/health_data_fallback.csv', index=False)
unmatched_results_count = pd.read_sql(query4, engine).iloc[0]['count']
with open('data/health_count_fallback.txt', 'w') as f:
    f.write(str(int(unmatched_results_count)))
print("Exported health_data_fallback.csv and health_count_fallback.txt")

# 4. extraction_audit
query5 = text('''
    SELECT extraction_layer, COUNT(*) as count,
           ROUND(AVG(vig_percent)::numeric, 2) as avg_vig
    FROM scraped_cs2_odds
    WHERE is_valid = true
    GROUP BY extraction_layer;
''')
df5 = pd.read_sql(query5, engine)
df5.to_csv('data/extraction_audit_fallback.csv', index=False)
print("Exported extraction_audit_fallback.csv")

print("All exports completed successfully.")
