
import os
import json
from typing import List

LOG_DIR = "session_logs"

# Ensure the log directory exists and is a proper directory
if not os.path.exists(LOG_DIR) or not os.path.isdir(LOG_DIR):
    os.makedirs(LOG_DIR, exist_ok=True)

def get_log_path(session_id: str) -> str:
    return os.path.join(LOG_DIR, f"{session_id}.json")

def save_log(session_id: str, entry: dict):
    path = get_log_path(session_id)
    logs = []
    if os.path.exists(path):
        with open(path, "r") as f:
            logs = json.load(f)
    logs.append(entry)
    with open(path, "w") as f:
        json.dump(logs, f, indent=2)

def get_logs(session_id: str) -> List[dict]:
    path = get_log_path(session_id)
    if not os.path.exists(path):
        raise FileNotFoundError("Session does not exist")
    with open(path, "r") as f:
        return json.load(f)

def list_sessions() -> List[str]:
    return [f.replace(".json", "") for f in os.listdir(LOG_DIR) if f.endswith(".json")]
