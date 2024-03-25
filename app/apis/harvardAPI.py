import json
import requests
from app import config
from app import callNumberValidation


def parse_harvard_data(entry, number, retrieval_settings):
    harvard_data = retrieve_data_from_harvard(number, False)
    if harvard_data:
        classifications = harvard_data.get('mods', {}).get('classification', [])
        identifiers = harvard_data.get('mods', {}).get('identifier', [])

        if isinstance(identifiers, dict):
            if identifiers.get('type') == 'oclc':
                oclc = identifiers.get('content', '')

                if entry.get('oclc') == '' or entry.get('oclc') is None and retrieval_settings['retrieve_oclc']:
                    entry.update({
                        'oclc': oclc,
                    })
        else:
            oclc = ''
            for identifier in identifiers:
                if not isinstance(identifier, dict):
                    print("Error: Harvard entry formatted incorrectly, skipping this one")
                    continue
                if identifier.get('type') == 'oclc':
                    oclc = identifier.get('content', '')

                if entry.get('oclc') == '' or entry.get('oclc') is None and retrieval_settings['retrieve_oclc']:
                    entry.update({
                        'oclc': oclc,
                    })

        if isinstance(classifications, dict):
            if classifications.get('authority') == 'lcc':
                lccn = classifications.get('content', '')

                if (entry.get('lccn') == '' or entry.get('lccn') is None and retrieval_settings['retrieve_lccn'] and
                        callNumberValidation.validate_lc_call_number(lccn)):
                    entry.update({
                        'lccn': lccn,
                        'source': 'Harvard'
                    })
        else:
            lccn = ''
            for classification in classifications:
                if not isinstance(classification, dict):
                    print("Error: Harvard entry formatted incorrectly, skipping this one")
                    continue
                if classification.get('authority') == 'lcc':
                    lccn = classification.get('content', '')

                if (entry.get('lccn') == '' or entry.get('lccn') is None and retrieval_settings['retrieve_lccn'] and
                        callNumberValidation.validate_lc_call_number(lccn)):
                    entry.update({
                        'lccn': lccn,
                        'source': 'Harvard'
                    })
    return entry


def retrieve_data_from_harvard(isbn, looking_for_status):
    config_file = config.load_config()

    base_url = "http://webservices.lib.harvard.edu/rest/v3/hollis/mods/isbn/"
    jsonp = "?jsonp=record"
    full_url = f"{base_url}{isbn}{jsonp}"

    try:
        if looking_for_status:
            response = requests.get(full_url, timeout=config_file["search_timeout"])
            return response.status_code

        response = requests.get(full_url, timeout=config_file["search_timeout"])
        response.raise_for_status()  # Raise an HTTPError for bad responses
        data = response.content.decode('utf-8')  # Decode the byte string

        # Extract JSON data from the response (assuming the JSON is inside parentheses)
        json_start = data.find('(') + 1
        json_end = data.rfind(')')
        json_data = data[json_start:json_end]

        # Parse the extracted JSON data
        parsed_data = json.loads(json_data)

        return parsed_data
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving data from Harvard: {e}")
        return None
