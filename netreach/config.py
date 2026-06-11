import os
import yaml

CONFIG_DIR = os.path.expanduser("~/.netreach")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.yaml")

DEFAULT_CONFIG = {
    "github_token": "",
    "twitter_cookies": "",
    "reddit_user_agent": "netreach/1.0",
    "bilibili_sessdata": "",
}

def load_config():
    """Loads configuration, merging missing keys with default values."""
    if not os.path.exists(CONFIG_FILE):
        return DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if not isinstance(data, dict):
                return DEFAULT_CONFIG.copy()
            # Merge with defaults
            config = DEFAULT_CONFIG.copy()
            config.update(data)
            return config
    except Exception:
        return DEFAULT_CONFIG.copy()

def save_config(config):
    """Saves configuration directory and writes YAML file."""
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            yaml.safe_dump(config, f, default_flow_style=False)
        return True
    except Exception:
        return False

def set_config_value(key, value):
    """Updates a configuration key and persists it to config.yaml."""
    config = load_config()
    if key not in DEFAULT_CONFIG:
        raise KeyError(f"Invalid configuration key: {key}")
    config[key] = value
    save_config(config)
