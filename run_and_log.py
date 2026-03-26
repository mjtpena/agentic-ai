"""Run a demo script and capture output to a UTF-8 log file."""
import subprocess
import sys
import os
from datetime import datetime, timezone

demo_dir = sys.argv[1]  # e.g. 01-basic-agent
script = sys.argv[2]    # e.g. src/main.py
base = r"C:\Users\mjtpena\dev\agentic-ai"

demo_path = os.path.join(base, demo_dir)
script_path = os.path.join(demo_path, script)
log_name = sys.argv[3] if len(sys.argv) > 3 else "execution.log"
log_path = os.path.join(demo_path, log_name)

timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

result = subprocess.run(
    [sys.executable, script_path],
    cwd=demo_path,
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace",
    timeout=300,
)

with open(log_path, "w", encoding="utf-8") as f:
    f.write(f"{'='*70}\n")
    f.write(f"EXECUTION LOG: {demo_dir}/{script}\n")
    f.write(f"Timestamp: {timestamp}\n")
    f.write(f"Exit Code: {result.returncode}\n")
    f.write(f"{'='*70}\n\n")
    f.write(result.stdout)
    if result.stderr:
        f.write(f"\n{'='*70}\n")
        f.write("STDERR:\n")
        f.write(result.stderr)

print(f"Log saved: {log_path} ({os.path.getsize(log_path)} bytes)")
print(f"Exit code: {result.returncode}")
if result.returncode != 0:
    print(f"STDERR: {result.stderr[:500]}")
