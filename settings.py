import json
import os
import logging

SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")

DEFAULTS = {
    "last_scan_path": os.path.expanduser("~"),
    "size_filter": "All",
    "max_depth": 3,
    "exclusions": "",
    "dark_mode": "auto",
    "sort_column": "size",
    "sort_descending": True,
    "plugins": {
        "python": True,
        "nodejs": True
    }
}

def load_settings():
    logger = logging.getLogger(__name__)
    if not os.path.exists(SETTINGS_FILE):
        logger.info("Settings file not found, using defaults")
        return DEFAULTS.copy()
    try:
        with open(SETTINGS_FILE, "r") as f:
            data = json.load(f)
        for k, v in DEFAULTS.items():
            if k not in data:
                data[k] = v
        logger.info("Settings loaded")
        return data
    except Exception as e:
        logger.error(f"Error loading settings: {e}")
        return DEFAULTS.copy()

def save_settings(settings):
    logger = logging.getLogger(__name__)
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=2)
        logger.info("Settings saved to file")
    except Exception as e:
        logger.error(f"Error saving settings: {e}")