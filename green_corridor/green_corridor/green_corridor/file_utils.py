import json
import os
from datetime import datetime

LOG_FILE = "logs/corridor.log"


def load_json(path):
    with open(path, "r") as f:
        return json.load(f)


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=4)


def log_event(text):
    """Append one timestamped line to the log file and echo it."""
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {text}"
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")
    print(line)


def read_log(last_n=10):
    """Return the last n lines of the log as a list."""
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, "r") as f:
        return f.readlines()[-last_n:]
