import json
import requests


def parse_harvard_data(entry, number):
    harvard_data = retrieve_data_from_harvard(number)
    if harvard_data:
        classifications = harvard_data.get('mods', {}).get('classification', [])
        identifiers = harvard_data.get('mods', {}).get('identifier', [])

        if isinstance(identifiers, dict):
            if identifiers.get('type') == 'oclc':
                oclc = identifiers.get('content', '')

                entry.update({
                    'oclc': oclc,
                })
        else:
            oclc = ''
            for identifier in identifiers:
                if not isinstance(identifier, dict):
                    print("Error: Entry formatted incorrectly, skipping this one")
                    continue
                if identifier.get('type') == 'oclc':
                    oclc = identifier.get('content', '')

                entry.update({
                    'oclc': oclc,
                })

        if isinstance(classifications, dict):
            if classifications.get('authority') == 'lcc':
                lcc = classifications.get('content', '')

                entry.update({
                    'lcc': lcc,
                    'source': 'Harvard'
                })
        else:
            lcc = ''
            for classification in classifications:
                if not isinstance(classification, dict):
                    print("Error: Entry formatted incorrectly, skipping this one")
                    continue
                if classification.get('authority') == 'lcc':
                    lcc = classification.get('content', '')

                entry.update({
                    'lcc': lcc,
                    'source': 'Harvard'
                })

    return entry

def retrieve_data_from_harvard(isbn):
    base_url = "http://webservices.lib.harvard.edu/rest/v3/hollis/mods/isbn/"
    jsonp = "?jsonp=record"
    full_url = f"{base_url}{isbn}{jsonp}"

    try:
        response = requests.get(full_url)
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
