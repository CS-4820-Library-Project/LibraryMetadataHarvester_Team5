import argparse
import csv
import json

import requests


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
    
def open_library_isbn(isbn):
    try:
        # Construct the URL for the Open Library API
        url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"

        # Send a GET request to the Open Library API
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Convert the response to JSON format
            data = response.json()
            

            # Extract OCLC number and LC call number if available
            if f"ISBN:{isbn}" in data:
                book_info = data[f"ISBN:{isbn}"]
                oclc_number = book_info.get("identifiers", {}).get("oclc")
                lc_call_number = book_info.get("classifications", {}).get("lc_classifications")
                return [oclc_number, lc_call_number]
            else:
                return [None, None]
        else:
            # If the request was not successful, print the error message
            print(f"Error in Open Library API: {response.status_code}")
            return [None, None]

    except Exception as e:
        print(f"An error occurred in OpenLibrary API: {e}")
        return [None, None]



    

def open_library_oclc(oclc_number):
    try:
        url = f"http://openlibrary.org/api/books?bibkeys=OCLC:{oclc_number}&format=json&jscmd=data"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            print(data)
            book_info = data.get(f"OCLC:{oclc_number}", {})
            
        
            isbn_number = book_info.get("identifiers", {}).get("isbn_13")
            lc_call_number = book_info.get("classifications", {}).get("lc_classifications")
            return [isbn_number, lc_call_number]
            
        else:
            print("Error for OpenLibrary API:", response.status_code)
            return [None, None]
        
    except Exception as e:
        print(f"An error occurred in OpenLibrary API: {e}")
        return [None, None]
    



def main():
    parser = argparse.ArgumentParser(description="Library Metadata Harvester")

    # Define command-line arguments
    parser.add_argument("-i", "--input", help="Specify the input file containing ISBNs or OCNs.")
    parser.add_argument("-o", "--output", help="Specify the output file for tab-delimited results.")
    parser.add_argument("--retrieve-ocns", action="store_true", help="Retrieve associated OCNs (for ISBN input).")
    parser.add_argument("--retrieve-isbns", action="store_true", help="Retrieve associated ISBNs (for OCN input).")
    parser.add_argument("--retrieve-lccns", action="store_true", help="Retrieve Library of Congress Call Numbers.")
    parser.add_argument("--search-sources", help="Specify internet sources to search (comma-separated).")
    parser.add_argument("--source-priorities", help="Specify priority levels for internet sources (comma-separated).")
    parser.add_argument("--worldcat-key", help="Set the OCLC authentication key for WorldCat access.")
    parser.add_argument("--config", action="store_true",
                        help="Configure LMH settings (administrative permission required).")

    # Parse command-line arguments
    args = parser.parse_args()

    # Get the input data if the input argument was used
    if args.input:
        input_data = read_input_file(args.input)
        print(f"Input data: {input_data}")

        # Initialize metadata list
        metadata = []

        for isbn in input_data:
            entry = {'isbn': isbn}

            # Check if Harvard is selected as a source
            if args.search_sources and 'harvard' in args.search_sources.lower().split(','):
                harvard_data = retrieve_data_from_harvard(isbn)
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
                            if classification.get('authority') == 'lcc':
                                lcc = classification.get('content', '')

                            entry.update({
                                'lcc': lcc,
                                'source': 'Harvard'
                            })

            # Append the entry to metadata
            metadata.append(entry)

        # Write metadata to output file
        write_to_output(metadata, args.output)

    else:
        print("Error: Please provide an input file using the -i or --input option.")

    # TODO: Add logic to handle the rest of the command-line arguments and execute the LMH functionality


if __name__ == "__main__":
    main()
