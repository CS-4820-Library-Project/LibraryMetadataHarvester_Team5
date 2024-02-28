import argparse
import csv
import json

import requests
from requests.auth import HTTPBasicAuth
from datetime import timedelta
from ratelimit import limits, sleep_and_retry

def read_input_file(file_path):
    with open(file_path, 'r') as file:
        reader = csv.reader(file, delimiter='\t')  # Adjust delimiter based on the actual file format
        input_data = [row[0] for row in reader]  # Assuming the data is in the first column of the file
    return input_data


def write_to_output(metadata, output_file):
    header = ['ISBN', 'OCLC', 'LCC', 'LCC-Source']

    with open(output_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter='\t')
        writer.writerow(header)

        for entry in metadata:
            row = [
                entry.get('isbn', ''),
                entry.get('oclc', ''),
                entry.get('lcc', ''),
                entry.get('source', '')
            ]
            writer.writerow(row)

    print("Output File Generated.")


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


def request_authentication_key_from_oclc():
    base_url = "https://oauth.oclc.org/token"
    client_id = "d2au8EHInSt5k21k3CJDlLe4Dn2FlXGEQ1LiNOWaWKIznGSAzEzwqMw9XsBSAbMsUImvplz98B5smA7J"
    secret = "Qjcq0YS93zZY52DK0Z6tDBluVZoUSXSR"

    headers = {'Accept': 'application/json'}
    params = {'grant_type': 'client_credentials', 'scope': 'WorldCatMetadataAPI'}

    try:
        response = requests.get(base_url, auth=HTTPBasicAuth(client_id, secret), params=params, headers=headers)
        response_data = response.json()
        print(response.text)

        if 'access_token' in response_data:
            access_token = response_data['access_token']
            print(f"Access Token: {access_token}")
        else:
            print("Error: Access token not found in response.")
    except Exception as e:
        print(f"Error retrieving access token from OCLC: {e}")
        return None


def retrieve_data_from_oclc(oclc):
    base_url = "https://americas.discovery.api.oclc.org/worldcat/search/v2/bibs/"
    full_url = f"{base_url}{oclc}"

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
        print(f"Error retrieving data from OCLC: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Library Metadata Harvester")

    # Define command-line arguments
    parser.add_argument("-i", "--input", help="Specify the input file containing ISBNs or OCNs.")
    parser.add_argument("-o", "--output", help="Specify the output file for tab-delimited results.")
    parser.add_argument("--retrieve-ocns", action="store_true", help="Retrieve associated OCNs (for ISBN input).")
    parser.add_argument("--retrieve-isbns", action="store_true", help="Retrieve associated ISBNs (for OCN input).")
    parser.add_argument("--retrieve-lccns", action="store_true", help="Retrieve Library of Congress Call Numbers.")
    parser.add_argument("--search-sources",
                        help="Specify internet sources to search (comma-separated). Examples include: harvard, oclc, loc")
    parser.add_argument("--source-priorities", help="Specify priority levels for internet sources (comma-separated).")
    parser.add_argument("--worldcat-key", help="Set the OCLC authentication key for WorldCat access.")
    parser.add_argument("--config", action="store_true",
                        help="Configure LMH settings (administrative permission required).")

    # Parse command-line arguments
    args = parser.parse_args()

    is_isbn = False
    is_oclc = False

    # Get the input data if the input argument was used
    if args.input:
        input_data = read_input_file(args.input)
        print(f"Input data: {input_data}")

        if len(input_data[0]) >= 10:
            is_isbn = True
            print("List Contains ISBN Values")
        elif len(input_data[0]) <= 9:
            is_oclc = True
            print("List Contains OCLC Values")

        # Initialize metadata list
        metadata = []

        for number in input_data:

            if is_isbn:
                entry = {'isbn': number}
            if is_oclc:
                entry = {'oclc': number}

            # Check if Harvard is selected as a source
            if args.search_sources and 'harvard' in args.search_sources.lower().split(','):
                if not is_isbn:
                    print(
                        "Harvard API requires ISBN Values as Input. Please input a list of ISBN values to use this API.")
                    break
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

            # Check if OCLC is selected as a source
            if args.search_sources and 'oclc' in args.search_sources.lower().split(','):
                if not is_oclc:
                    print("OCLC API requires OCLC Values as Input. Please input a list of OCLC values to use this API.")
                    break

                oclc_data = retrieve_data_from_oclc(number)

            # Check if LOC is selected as a source
            if args.search_sources and 'loc' in args.search_sources.lower().split(','):
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
                                'source': 'loc'
                            })
                        else:
                            entry.update({
                                'lcc': lcc,
                                'oclc': oclc,
                                'source': 'loc'
                            })

            # Append the entry to metadata
            metadata.append(entry)

        if args.output:
            # Write metadata to output file
            write_to_output(metadata, args.output)
        else:
            print("No output file requested. If an output file is desired please use the -o or --output option.")

    else:
        print("Error: Please provide an input file using the -i or --input option.")

    # TODO: Add logic to handle the rest of the command-line arguments and execute the LMH functionality


if __name__ == "__main__":
    main()
