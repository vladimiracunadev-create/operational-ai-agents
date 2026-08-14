import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from operational_agents.validator import validate

issues = validate(ROOT)
for item in issues:
    print(f"{item['level'].upper()} {item['agent_id']}: {item['message']}")
raise SystemExit(1 if any(item['level'] == 'error' for item in issues) else 0)
