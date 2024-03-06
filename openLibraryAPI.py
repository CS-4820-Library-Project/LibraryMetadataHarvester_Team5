import json
import requests


def parse_open_library_data(entry, number, is_oclc, is_isbn):
    open_library_data = retrieve_data_from_open_library(number, is_oclc, is_isbn)
    if open_library_data:
        if is_isbn:
            book_data = open_library_data.get(f"ISBN:{number}", {})
            oclc_number = book_data.get("identifiers", {}).get("oclc", '')
            call_number = book_data.get("classifications", {}).get("lc_classifications", '')
            if oclc_number:
                oclc = oclc_number[0]
                if entry.get('oclc') == '' or entry.get('oclc') is None:
                    entry.update({
                        'oclc': oclc,
                    })
            if call_number:
                lcc = call_number[0]
                if entry.get('lcc' == '') or entry.get('lcc') is None:
                    entry.update({
                        'lcc': lcc,
                        'source': 'OpenLibrary'
                    })
        if is_oclc:
            book_data = open_library_data.get(f"OCLC{number}", {})
            isbn_number = book_data.get("identifiers", {}).get("isbn_13", '')
            if isbn_number == '':
                isbn_number = book_data.get("identifiers", {}).get("isbn_10", '')
            call_number = book_data.get("classifications", {}).get("lc_classifications", '')
            if isbn_number:
                isbn = isbn_number[0]

                if entry.get('isbn') == '' or entry.get('isbn') is None:
                    entry.update({
                        'isbn': isbn,
                    })
            if call_number:
                lcc = call_number[0]

                if entry.get('lcc' == '') or entry.get('lcc') is None:
                    entry.update({
                        'lcc': lcc,
                        'source': 'OpenLibrary'
                    })
    return entry


def retrieve_data_from_open_library(number, is_oclc, is_isbn):
    if is_isbn:
        base_url = "https://openlibrary.org/api/books?bibkeys=ISBN:"
        json_data = "&format=json&jscmd=data"
        full_url = f"{base_url}{number}{json_data}"
    if is_oclc:
        base_url = "http://openlibrary.org/api/books?bibkeys=OCLC"
        json_data = "&format=json&jscmd=data"
        full_url = f"{base_url}{number}{json_data}"

    try:
        response = requests.get(full_url)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        data = response.content.decode('utf-8')  # Decode the byte string

        # Parse the extracted JSON data
        parsed_data = json.loads(data)

        return parsed_data
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving data from Open Library: {e}")
        return None
