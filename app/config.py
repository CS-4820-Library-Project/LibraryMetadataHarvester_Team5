import json


def load_config():
    try:
        with open("config.json", 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # If config file doesn't exist, create a new one with default values
        default_config = {
            "google_api_key": "YOUR_GOOGLE_API_KEY",
            "search_timeout": 10  # Default search timeout in seconds
        }
        save_config(default_config)
        return default_config


def save_config(new_config):
    with open("config.json", 'w') as f:
        json.dump(new_config, f, indent=4)


def set_search_timeout(config, search_timeout):
    config["search_timeout"] = search_timeout
    save_config(config)


def set_google_key(config, google_key):
    config["google_api_key"] = google_key
    save_config(config)
