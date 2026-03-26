"""Reformat execution logs into clean Markdown with proper headers."""
import re
import os

BASE = r"C:\Users\mjtpena\dev\agentic-ai"

files = [
    os.path.join(BASE, "01-basic-agent", "execution.md"),
    os.path.join(BASE, "02-openapi-agent", "execution.md"),
    os.path.join(BASE, "04-agent-framework", "execution.md"),
    os.path.join(BASE, "04-agent-framework", "execution_streaming.md"),
    os.path.join(BASE, "04-agent-framework", "execution_debate.md"),
]

for fpath in files:
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    # Remove double --- lines (consecutive horizontal rules)
    content = re.sub(r'(---\n)+---', '---', content)

    # Remove --- that sit alone between blank lines redundantly  
    content = re.sub(r'\n---\n---\n', '\n---\n', content)

    # Fix task headers that became --- by looking for emoji + title pattern
    # Pattern: ---\n📊 Title\n--- => ## 📊 Title  
    content = re.sub(r'---\n(📊[^\n]+)\n---', r'## \1', content)
    content = re.sub(r'---\n(🗺️[^\n]+)\n---', r'## \1', content)
    content = re.sub(r'---\n(⚖️[^\n]+)\n---', r'## \1', content)
    content = re.sub(r'---\n(📢[^\n]+)\n---', r'## \1', content)

    # Fix the agent info block  
    content = re.sub(
        r'(🔬[^\n]+\n\s+Model:[^\n]+)\n---',
        r'\1\n',
        content
    )
    content = re.sub(
        r'(🌍[^\n]+\n\s+Model:[^\n]+)\n---',
        r'\1\n',
        content
    )
    content = re.sub(
        r'(💰[^\n]+)\n---',
        r'\1\n',
        content
    )
    content = re.sub(
        r'(⚖️  Multi-Agent Debate[^\n]+)\n---',
        r'\1\n',
        content
    )

    # Clean up any remaining triple+ newlines
    content = re.sub(r'\n{4,}', '\n\n\n', content)

    with open(fpath, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Fixed: {fpath}")
