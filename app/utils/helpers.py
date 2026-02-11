import json
from pathlib import Path

def load_json(path: str):
    p = Path(path)
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))
