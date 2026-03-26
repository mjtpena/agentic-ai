import json

data = json.load(open(r'C:\Users\mjtpena\dev\agentic-ai\models.json'))

for m in data:
    if m['name'].startswith('gpt-5'):
        skus = [s['name'] for s in m['skus']]
        caps = list(m.get('capabilities', {}).keys())
        print(f"{m['name']} v{m['version']}: skus={skus}, caps={caps}")
