#config_manager.py
import json
import os
from PyQt5.QtCore import QSettings

SETTINGS_FILE = "stress_tester_config.json"

DEFAULT_CONFIG = {
    "solution": "",
    "brute": "",
    "generator": "",
    "mode": "Brute Force",
    "num_tests": 100,
    "stop_on_fail": True,
    "timeout": 2.0,
    "theme": "light"
}

def load_config():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    return DEFAULT_CONFIG.copy()

def save_config(config):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(config, f, indent=4)