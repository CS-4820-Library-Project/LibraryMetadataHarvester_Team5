import subprocess
from app import config
from app import callNumberValidation


def parse_text_marc(text_marc):
    # Split the text MARC records by lines
    lines = text_marc.strip().split('\n')

    # Dictionary to store MARC data
    marc_data = {'lccn': '', 'oclc': ''}

    for line in lines:
        tag = line[:3]
        if tag == "050":
            marc_data['lccn'] = line.split('$a')[1].strip().replace("$b ", "")
        if tag == "079":
            marc_data['oclc'] = line.split('$z')[0].split('$a')[1].lower().replace("(ocolc)", "").strip()

    return marc_data


def run_yaz_client(isbn, target_string):
    config_file = config.load_config()

    commands = f"""
    open {target_string}
    find @attr 1=7 {isbn}
    show 1
    quit
    """
    process = subprocess.run(['C:\\Program Files\\YAZ\\bin\\yaz-client'], input=commands, text=True, encoding='utf-8',
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=config_file["search_timeout"])

    # # Exit if there was an error
    if process.stderr and "Innovative Interfaces Inc. Z39.50 SERVER version 1.1" not in process.stderr:
        print("Error: ", process.stderr)
        return None

    # Process the MARC record text
    if process.stdout:
        marc_data = parse_text_marc(process.stdout)
        return marc_data

    return None


def parse_data(entry, number, retrieval_settings):
    for library, target_string in target_sources.items():
        library_data = run_yaz_client(number, target_string)
        if (entry.get('lccn') == '' or entry.get('lccn') is None and retrieval_settings['retrieve_lccn'] and
                callNumberValidation.validate_lc_call_number(library_data['lccn'])):
            entry.update({
                'lccn': library_data['lccn'],
                'source': library
            })
        if entry.get('oclc') == '' or entry.get('oclc') is None and retrieval_settings['retrieve_oclc']:
            entry.update({
                'oclc': library_data['oclc'],
            })
    return entry


# Define your target sources (libraries) and their corresponding target strings
target_sources = {
    "LOC": "lx2.loc.gov:210/LCDB",
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
    # Add more libraries as needed
}
