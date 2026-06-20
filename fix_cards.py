import os

def fix_file(filepath, replacements):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    for old, new in replacements:
        content = content.replace(old, new)
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

# Home.py
fix_file(r"d:\projects\cs2-dashboard\Home.py", [
    ("from quant_engine import GLOBAL_CSS, load_live_odds, render_metric_card", "from quant_engine import GLOBAL_CSS, load_live_odds"),
    ('render_metric_card(title="Odds Scraper", content="ACTIVE", description="Every 2h via n8n")', 'ui.metric_card(title="Odds Scraper", content="ACTIVE", description="Every 2h via n8n", key="odds_status")'),
    ('render_metric_card(title="Results Logger", content="ACTIVE", description="Nightly at 23:00")', 'ui.metric_card(title="Results Logger", content="ACTIVE", description="Nightly at 23:00", key="res_status")'),
    ('render_metric_card(title="Database", content=db_status, description="192.168.100.59:5432")', 'ui.metric_card(title="Database", content=db_status, description="192.168.100.59:5432", key="db_status")'),
    ('render_metric_card(title="Last Sync", content=last_sync, description="Most recent scrape")', 'ui.metric_card(title="Last Sync", content=last_sync, description="Most recent scrape", key="sync_status")')
])

# 1_📊_Calibration.py
fix_file(r"d:\projects\cs2-dashboard\pages\1_📊_Calibration.py", [
    ("from quant_engine import load_resolved_matches, compute_calibration_metrics, GLOBAL_CSS, render_metric_card", "from quant_engine import load_resolved_matches, compute_calibration_metrics, GLOBAL_CSS"),
    ('render_metric_card(title="Resolved Matches", content=str(resolved_matches_count), description="Total sample size")', 'ui.metric_card(title="Resolved Matches", content=str(resolved_matches_count), description="Total sample size", key="kpi_1")'),
    ('render_metric_card(title="Favorite Win Rate", content=f"{favorite_win_rate:.1f}%", description="Actual performance")', 'ui.metric_card(title="Favorite Win Rate", content=f"{favorite_win_rate:.1f}%", description="Actual performance", key="kpi_2")'),
    ('render_metric_card(title="Avg Implied Prob", content=f"{avg_implied_prob:.1f}%", description="Bookmaker expectation")', 'ui.metric_card(title="Avg Implied Prob", content=f"{avg_implied_prob:.1f}%", description="Bookmaker expectation", key="kpi_3")'),
    ('render_metric_card(title="Market Edge", content=edge_str, description="Positive = bookmaker overvalues favorites")', 'ui.metric_card(title="Market Edge", content=edge_str, description="Positive = bookmaker overvalues favorites", key="kpi_4")')
])

# 2_🎯_Live_Radar.py
fix_file(r"d:\projects\cs2-dashboard\pages\2_🎯_Live_Radar.py", [
    ("from quant_engine import load_live_odds, GLOBAL_CSS, render_metric_card", "from quant_engine import load_live_odds, GLOBAL_CSS"),
    ('render_metric_card(title="Matches in Feed", content=matches_in_feed, description="Filtered / Total")', 'ui.metric_card(title="Matches in Feed", content=matches_in_feed, description="Filtered / Total", key="lr_metric_1")'),
    ('render_metric_card(title="Avg Vig", content=avg_vig_str, description="Mean margin")', 'ui.metric_card(title="Avg Vig", content=avg_vig_str, description="Mean margin", key="lr_metric_2")'),
    ('render_metric_card(title="Sharpest Line", content=sharpest_line, description="Lowest vig match")', 'ui.metric_card(title="Sharpest Line", content=sharpest_line, description="Lowest vig match", key="lr_metric_3")')
])

# 3_🗄️_Match_Ledger.py
fix_file(r"d:\projects\cs2-dashboard\pages\3_🗄️_Match_Ledger.py", [
    ("from quant_engine import load_resolved_matches, compute_calibration_metrics, GLOBAL_CSS, render_metric_card", "from quant_engine import load_resolved_matches, compute_calibration_metrics, GLOBAL_CSS")
])

# 4_🔧_Pipeline_Health.py
fix_file(r"d:\projects\cs2-dashboard\pages\4_🔧_Pipeline_Health.py", [
    ("from quant_engine import load_resolved_matches, load_health_data, load_extraction_audit, GLOBAL_CSS, render_metric_card", "from quant_engine import load_resolved_matches, load_health_data, load_extraction_audit, GLOBAL_CSS")
])

print("Fix applied successfully.")
