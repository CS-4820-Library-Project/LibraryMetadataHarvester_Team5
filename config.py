import json


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

    def set_sources(self, sources):
        self.config["sources"] = sources
        self.save_config(self.config)

    def set_priority_order(self, priority_order):
        self.config["priority_order"] = priority_order
        self.save_config(self.config)

    def set_include_LCCN(self, include_LCCN):
        self.config["include_LCCN"] = include_LCCN
        self.save_config(self.config)

    def set_include_DOI(self, include_DOI):
        self.config["include_DOI"] = include_DOI
        self.save_config(self.config)

    def set_OCLC_API_key(self, OCLC_API_key):
        self.config["OCLC_API_key"] = OCLC_API_key
        self.save_config(self.config)

    def set_search_timeout(self, search_timeout):
        self.config["search_timeout"] = search_timeout
        self.save_config(self.config)


# Example usage:
# Later down the line other branches can use this config to set up the settings
if __name__ == "__main__":
    config = Config()

    # Set new configuration options
    config.set_sources(["Library of Congress", "WorldCat", "British Library"])
    config.set_priority_order(["WorldCat", "Library of Congress"])
    config.set_include_LCCN(False)
    config.set_include_DOI(False)
    config.set_OCLC_API_key("NEW_OCLC_API_KEY")
    config.set_search_timeout(60)
