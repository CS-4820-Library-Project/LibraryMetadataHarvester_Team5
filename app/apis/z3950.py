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
        try:
            if tag == "050":
                marc_data['lccn'] = line.split('$a')[1].strip().replace("$b ", "")
            if tag == "079":
                marc_data['oclc'] = line.split('$z')[0].split('$a')[1].lower().replace("(ocolc)", "").strip()
        except IndexError as e:
            print("Error: Z39.50 entry was formatted incorrectly, skipping this one")

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


def parse_data(entry, number, retrieval_settings, library):
    config_file = config.load_config()

    for key, target_string in config_file["z3950_sources"].items():
        if library == key:
            library_data = run_yaz_client(number, target_string)
            if library_data['lccn']:
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
