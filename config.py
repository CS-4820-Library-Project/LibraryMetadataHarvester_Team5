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
                "input_type": "ISBN",
                "sources": [],
                "priority_order": [],
                "include_other": True,
                "include_LCCN": True,
                "include_DOI": True,
                "OCLC_API_key": "YOUR_OCLC_API_KEY",
                "google_API_key": "",
                "search_timeout": 60  # Default search timeout in seconds
            }
            self.save_config(default_config)
            return default_config

    def save_config(self, new_config):
        with open(self.config_file, 'w') as f:
            json.dump(new_config, f, indent=4)

    # Setters for the configuration
            
    # Setter for input type, input_type: "ISBN" or "OCN"
    def set_input_type(self, input_type):
        if (input_type=="ISBN" or input_type=="OCN"):
            self.config["input_type"] = input_type
            self.save_config(self.config)

    # Setter for what sources are to be used, source_list: list indicating sources
    def set_sources(self, source_list):
        self.config["sources"] = source_list
        self.save_config(self.config)

    # Setter for priority order of sources, priority_list: list indicating priority
    def set_priority_order(self, priority_list):
        self.config["priority_order"] = priority_list
        self.save_config(self.config)

    # Setter for including other number(ISBN or OCN), t_or_f: True or False
    def set_include_other(self, t_or_f):
        self.config["include_other"] = t_or_f
        self.save_config(self.config)

    # Setter for including LCCN, t_or_f: True or False
    def set_include_lccn(self, t_or_f):
        self.config["include_LCCN"] = t_or_f
        self.save_config(self.config)

    # Setter for including DOI, t_or_f: True or False
    def set_include_doi(self, t_or_f):
        self.config["include_DOI"] = t_or_f
        self.save_config(self.config)

    # Setter for OCLC API key
    def set_oclc_key(self, key):
        self.config["OCLC_API_key"] = key
        self.save_config(self.config)

    # Setter for Google Books API key
    def set_google_key(self, key):
        self.config["google_API_key"] = key
        self.save_config(self.config)

    # Setter for search timeout per item
    def set_search_timeout(self, search_timeout):
        self.config["search_timeout"] = search_timeout
        self.save_config(self.config)

    # Getter for input type
    def get_input_type(self):
        return self.config["input_type"]
    

    # Getter for source list
    def get_sources(self):
        return self.config["sources"]
        

    # Getter for priority order of sources
    def get_priority_order(self):
        return self.config["priority_order"]
        

    # Getter for including other number(ISBN or OCN)
    def get_include_other(self):
        return self.config["include_other"]
        

    # Getter for including LCCN
    def get_include_lccn(self):
        return self.config["include_LCCN"]
        

    # Getter for including DOI
    def get_include_doi(self):
        return self.config["include_DOI"]
    

    # Getter for OCLC API key
    def get_oclc_key(self):
        return self.config["OCLC_API_key"]
        

    # Getter for Google Books API key
    def get_google_key(self):
        return self.config["google_API_key"]
        

    # Getter for search timeout per item
    def get_search_timeout(self):
        return self.config["search_timeout"]
        


if __name__ == "__main__":
    config = Config()

