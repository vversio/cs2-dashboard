import os
import re

directories = [r"d:\projects\cs2-dashboard", r"d:\projects\cs2-dashboard\pages"]

for d in directories:
    for filename in os.listdir(d):
        if filename.endswith(".py") and filename != "quant_engine.py":
            filepath = os.path.join(d, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace import to include render_metric_card if not present
            if "from quant_engine import" in content and "render_metric_card" not in content:
                content = re.sub(r'(from quant_engine import .*)', r'\1, render_metric_card', content)
            
            # Replace ui.metric_card with render_metric_card, ignoring the key argument
            # Format is typically: render_metric_card(title="...", content=..., description="...")
            content = re.sub(r'ui\.metric_card\(\s*title=(.*?),\s*content=(.*?),\s*description=(.*?),\s*key=.*?\)', 
                             r'render_metric_card(title=\1, content=\2, description=\3)', content)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
print("Cards patched successfully.")
