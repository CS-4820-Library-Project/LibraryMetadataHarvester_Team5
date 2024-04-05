import json
import requests
from app import config, logs
from app import callNumberValidation
from datetime import timedelta
from ratelimit import limits, sleep_and_retry


def parse_loc_data(entry, number, retrieval_settings, is_oclc):
    loc_data = retrieve_data_from_loc(number, False)
    if loc_data:
        results = loc_data.get('results', {})

        lccn = ''
        oclc = ''
        for result in results:
            if not isinstance(result, dict):
                logs.log_warning("LOC Entry formatted incorrectly, skipping this one")
                continue
            if result.get('item').get('call_number'):
                call_number = (result.get('item').get('call_number'))
                lccn = call_number[0]
            if result.get('number_oclc') and not is_oclc:
                oclc_number = (result.get('number_oclc'))
                oclc = oclc_number[0]

            if is_oclc:
                if (entry.get('lccn') == '' or entry.get('lccn') is None and retrieval_settings['retrieve_lccn'] and
                        callNumberValidation.validate_lc_call_number(lccn)):
                    entry.update({
                        'lccn': lccn,
                        'source': 'LOC'
                    })
            else:
                if entry.get('oclc') == '' or entry.get('oclc') is None and retrieval_settings['retrieve_oclc']:
                    entry.update({
                        'oclc': oclc
                    })
                if (entry.get('lccn') == '' or entry.get('lccn') is None and retrieval_settings['retrieve_lccn'] and
                        callNumberValidation.validate_lc_call_number(lccn)):
                    entry.update({
                        'lccn': lccn,
                        'source': 'LOC'
                    })
    return entry


@sleep_and_retry
@limits(calls=10, period=timedelta(seconds=10).total_seconds())
def retrieve_data_from_loc(number, looking_for_status):
    config_file = config.load_config()

    base_url = "https://www.loc.gov/search/"
    jsonq = "?fo=json&q="
    full_url = f"{base_url}{jsonq}{number}"

    try:
        if looking_for_status:
            response = requests.get(full_url, timeout=config_file["search_timeout"])
            return response.status_code

        response = requests.get(full_url, timeout=config_file["search_timeout"])
        response.raise_for_status()  # Raise an HTTPError for bad responses
        data = response.content.decode('utf-8')  # Decode the byte string

        # Parse the extracted JSON data
        parsed_data = json.loads(data)

        return parsed_data
    except requests.exceptions.RequestException as e:
        logs.log_error(f"Error retrieving data from LOC: {e}")
        return None
