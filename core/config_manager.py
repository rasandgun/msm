import json
import os

SETTINGS_FILE = "stress_tester_config.json"

DEFAULT_CONFIG = {
    "solution": "",
    "brute": "",
    "generator": "",
    "mode": "Brute Force",
    "num_tests": 100,
    "stop_on_fail": True,
    "timeout": 2,
    "theme": "light"
}

def load_config() -> dict:
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return DEFAULT_CONFIG.copy()

def save_config(config: dict) -> None:
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)