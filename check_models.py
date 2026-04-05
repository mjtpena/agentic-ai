"""Query available Azure OpenAI models from models.json snapshot."""

import json
import os

models_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models.json")
data = json.load(open(models_path))

for m in data:
    if m['name'].startswith('gpt-5'):
        skus = [s['name'] for s in m['skus']]
        caps = list(m.get('capabilities', {}).keys())
        print(f"{m['name']} v{m['version']}: skus={skus}, caps={caps}")
