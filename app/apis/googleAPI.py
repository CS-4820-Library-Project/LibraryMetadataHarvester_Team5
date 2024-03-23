import json
import requests
from app import config
from datetime import timedelta
from ratelimit import limits, sleep_and_retry


def parse_google_data(entry, number, retrieval_settings, is_oclc, is_isbn):
    google_data = retrieve_data_from_google(number, False, is_oclc, is_isbn)
    if google_data:
        if 'items' in google_data:
            if is_isbn:
                book_data = google_data['items'][0].get('volumeInfo', {}).get('industryIdentifiers', [{}])
                for identifier in book_data:
                    if not isinstance(identifier, dict):
                        print("Error: Google entry formatted incorrectly, skipping this one")
                        continue
                    if identifier.get('type') == 'other' and identifier.get('identifier')[:4] == "OCLC":
                        oclc = identifier.get('identifier')[5:]
                        if entry.get('oclc') == '' or entry.get('oclc') is None and retrieval_settings['retrieve_oclc']:
                            entry.update({
                                'oclc': oclc,
                            })
            if is_oclc:
                book_data = google_data['items'][0].get('volumeInfo', {}).get('industryIdentifiers', [{}])
                for identifier in book_data:
                    if not isinstance(identifier, dict):
                        print("Error: Entry formatted incorrectly, skipping this one")
                        continue
                    if identifier.get('type') == 'ISBN_13':
                        isbn = identifier.get('identifier')
                        if entry.get('isbn') == '' or entry.get('isbn') is None and retrieval_settings['retrieve_isbn']:
                            entry.update({
                                'isbn': isbn,
                            })
                if entry.get('isbn') == '' or entry.get('isbn') is None:
                    for identifier in book_data:
                        if not isinstance(identifier, dict):
                            print("Error: Google entry formatted incorrectly, skipping this one")
                            continue
                        if identifier.get('type') == 'ISBN_10':
                            isbn = identifier.get('identifier')
                            if entry.get('isbn') == '' or entry.get('isbn') is None and retrieval_settings['retrieve_isbn']:
                                entry.update({
                                    'isbn': isbn,
                                })
    return entry


@sleep_and_retry
@limits(calls=10, period=timedelta(seconds=10).total_seconds())
def retrieve_data_from_google(number, looking_for_status, is_oclc, is_isbn):
    config_file = config.load_config()

    if is_isbn:
        base_url = "https://www.googleapis.com/books/v1/volumes?q=isbn:"
        key = "&key="
        api_key = config_file["google_api_key"]
        full_url = f"{base_url}{number}{key}{api_key}"
    if is_oclc:
        base_url = "https://www.googleapis.com/books/v1/volumes?q=oclc:"
        key = "&key="
        api_key = config_file["google_api_key"]
        full_url = f"{base_url}{number}{key}{api_key}"

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
        print(f"Error retrieving data from Google Books: {e}")
        return None
