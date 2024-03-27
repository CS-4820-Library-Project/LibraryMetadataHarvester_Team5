import json


def load_config():
    try:
        with open("config.json", 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # If config file doesn't exist, create a new one with default values
        default_config = {
            "google_api_key": "YOUR_GOOGLE_API_KEY",
            "search_timeout": 10,  # Default search timeout in seconds
            "retrieve_isbn": True,
            "retrieve_oclc": True,
            "retrieve_lccn": True,
            "appearance_mode": "Dark",
            "z3950_sources": {
                "Yale": "z3950.library.yale.edu:7090/voyager",
                "UVa": "virgo.lib.virginia.edu:2200/unicorn",
                "UAlberta": "ualapp.library.ualberta.ca:2200/unicorn",
                "Oxford": "library.ox.ac.uk:210/44OXF_INST",
                "Mich": "141.215.16.4:210/INNOPAC",
                "UCLA": "z3950.library.ucla.edu:1921/01UCS_LAL",
                "Cambridge": "newton.lib.cam.ac.uk:7790/voyager",
                "NLA": "catalogue.nla.gov.au:7090/voyager",
                "NCSU": "sirsi.lib.ncsu.edu:2200/UNICORN",
                "Toronto": "utoronto.alma.exlibrisgroup.com:1921/01UTORONTO_INST",
                "NLAus": "catalogue.nla.gov.au:7090/voyager",
                "UBC": "ils.library.ubc.ca:7090/Voyager",
                "DUKE": "catalog.library.duke.edu:9991/DUK01",
                "IUCAT": "libprd.uits.indiana.edu:2200/UNICORN",
                "QUEENS": "ocul-qu.alma.exlibrisgroup.com:210/01OCUL_QU",
                "UCB": "berkeley.alma.exlibrisgroup.com:1921/01UCS_BER/UCB",
                "NYU": "aleph.library.nyu.edu:9991/NYU01PUB",
                "UPenn": "na03.alma.exlibrisgroup.com:1921/01UPENN_INST",
                "NYPL": "nyst.sirsi.net:8419/unicorn"
            },
            "ordered_sources": []
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


def set_isbn_retrieval(config, isbn_retrieval):
    config["retrieve_isbn"] = isbn_retrieval
    save_config(config)


def set_oclc_retrieval(config, oclc_retrieval):
    config["retrieve_oclc"] = oclc_retrieval
    save_config(config)


def set_lccn_retrieval(config, lccn_retrieval):
    config["retrieve_lccn"] = lccn_retrieval
    save_config(config)


def set_appearance_mode(config, appearance_mode):
    config["appearance_mode"] = appearance_mode
    save_config(config)


def add_z3950_source(config, source_name, source_link):
    config["z3950_sources"][source_name] = source_link
    save_config(config)


def remove_z3950_source(config, source):
    del config["z3950_sources"][source]
    save_config(config)


def save_source_configuration(config, sources):
    config["ordered_sources"] = sources
    save_config(config)


def append_source(config, source):
    config["ordered_sources"].append(source)
    save_config(config)


def remove_source(config, source):
    config["ordered_sources"].remove(source)
    save_config(config)
