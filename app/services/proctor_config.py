"""
Proctoring configuration — persisted as a JSON file.
No DB migration needed; defaults are used if file doesn't exist.
"""
import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "../../proctor_config.json")

DEFAULTS = {
    "enabled": True,
    "check_interval_seconds": 30,
    "max_violations": 5,
    "allow_multiple_faces": False,
    "allow_no_face": False,
}


def load_config() -> dict:
    try:
        with open(CONFIG_PATH, "r") as f:
            data = json.load(f)
            # Fill missing keys with defaults
            return {**DEFAULTS, **data}
    except (FileNotFoundError, json.JSONDecodeError):
        return dict(DEFAULTS)


def save_config(config: dict) -> dict:
    merged = {**DEFAULTS, **config}
    with open(CONFIG_PATH, "w") as f:
        json.dump(merged, f, indent=2)
    return merged
