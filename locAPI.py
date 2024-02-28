import json
import requests
from datetime import timedelta
from ratelimit import limits, sleep_and_retry


def parse_loc_data(entry, number, is_oclc):
    loc_data = retrieve_data_from_loc(number)
    if loc_data:
        results = loc_data.get('results', {})

        lcc = ''
        oclc = ''
        for result in results:
            if not isinstance(result, dict):
                print("Error: Entry formatted incorrectly, skipping this one")
                continue
            if result.get('item').get('call_number'):
                call_number = (result.get('item').get('call_number'))
                lcc = call_number[0]
            if result.get('number_oclc') and not is_oclc:
                oclc_number = (result.get('number_oclc'))
                oclc = oclc_number[0]

            if is_oclc:
                entry.update({
                    'lcc': lcc,
                    'source': 'LOC'
                })
            else:
                entry.update({
                    'lcc': lcc,
                    'oclc': oclc,
                    'source': 'LOC'
                })
    return entry


@sleep_and_retry
@limits(calls=10, period=timedelta(seconds=10).total_seconds())
def retrieve_data_from_loc(number):
    base_url = "https://www.loc.gov/search/"
    jsonq = "?fo=json&q="
    full_url = f"{base_url}{jsonq}{number}"

    try:
        response = requests.get(full_url)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        data = response.content.decode('utf-8')  # Decode the byte string

        # Parse the extracted JSON data
        parsed_data = json.loads(data)

        return parsed_data
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving data from LOC: {e}")
        return None
