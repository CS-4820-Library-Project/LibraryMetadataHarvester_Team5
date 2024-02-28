import json

"""
This code will be updated at later point with any necessary new implementations
current features {
timeout time for a single ISBN search
} 
"""


class Config:
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # If config file doesn't exist, create a new one with default values
            default_config = {
                "sources": ["Library of Congress", "WorldCat"],
                "priority_order": ["Library of Congress", "WorldCat"],
                "include_LCCN": True,
                "include_DOI": True,
                "OCLC_API_key": "YOUR_OCLC_API_KEY",
                "search_timeout": 60  # Default search timeout in seconds
            }
            self.save_config(default_config)
            return default_config

    def save_config(self, new_config):
        with open(self.config_file, 'w') as f:
            json.dump(new_config, f, indent=4)

    def set_search_timeout(self, search_timeout):
        self.config["search_timeout"] = search_timeout
        self.save_config(self.config)


if __name__ == "__main__":
    config = Config()

    # Set new configuration options
    config.set_search_timeout(60)
