from app.apis import harvardAPI
from app.apis import locAPI
from app.apis import openLibraryAPI
from app.apis import googleAPI
from app import config
import argparse
import csv


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


def main():
    parser = argparse.ArgumentParser(description="Library Metadata Harvester")

    # Define command-line arguments
    parser.add_argument("-i", "--input", help="Specify the input file containing ISBNs or OCNs.")
    parser.add_argument("-o", "--output", help="Specify the output file for tab-delimited results.")
    parser.add_argument("--retrieve-ocns", action="store_true", help="Retrieve associated OCNs (for ISBN input).")
    parser.add_argument("--retrieve-isbns", action="store_true", help="Retrieve associated ISBNs (for OCN input).")
    parser.add_argument("--retrieve-lccs", action="store_true", help="Retrieve Library of Congress Call Numbers.")
    parser.add_argument("--search-sources",
                        help="Specify internet sources to search (comma-separated). Examples include: harvard,oclc,"
                             "loc,openlibrary,google")
    parser.add_argument("--source-priorities", help="Specify priority levels for internet sources (comma-separated).")
    parser.add_argument("--set-timeout", help="Configure LMH timeout for requesting data from APIs. Default is 10 "
                                              "seconds.")
    parser.add_argument("--set-google-key", help="Configure which key the LMH should use for Google Books API, "
                                                 "without one, searching via google books will be disallowed.")

    # Parse command-line arguments
    args = parser.parse_args()

    is_isbn = False
    is_oclc = False
    dont_use_google = False
    dont_use_oclc = False
    dont_use_harvard = False

    if args.set_google_key:

        config_file = config.load_config()
        config.set_google_key(config_file, args.set_google_key)
        print(f"Google Books API key is now set to {args.set_google_key}")
    elif args.set_timeout:
        try:
            if int(args.set_timeout) < 0:
                print("Error: Timeout value cannot be a negative number. Please provide a valid positive integer when "
                      "trying to change timeout value.")
                return

            config_file = config.load_config()
            config.set_search_timeout(config_file, int(args.set_timeout))
            print(f"API timeout is now set to {args.set_timeout}")
        except ValueError:
            print("Error: Timeout value must be an integer. Please provide a valid positive integer when trying to "
                  "change timeout value.")
            return
    else:
        # Get the input data if the input argument was used
        if args.input:
            input_data = read_input_file(args.input)
            print(f"Input data: {input_data}")

            # Check which type of input data we have
            if len(input_data[0]) >= 10:
                is_isbn = True
                print("List Contains ISBN Values")
            elif len(input_data[0]) <= 9:
                is_oclc = True
                print("List Contains OCLC Values")

            # Initialize metadata list
            metadata = []

            if args.source_priorities and args.search_sources:

                # Define the search order based on source priorities
                source_order = args.search_sources.lower().split(',')

                try:
                    # Attempt to convert each priority to an integer
                    priority_order = [int(priority) for priority in args.source_priorities.split(',')]

                    # Check if all priorities are valid integers
                    if not all(isinstance(priority, int) for priority in priority_order):
                        raise ValueError

                    ordered_sources = [source for _, source in sorted(zip(priority_order, source_order))]

                except ValueError:
                    print("Error: Each source priority must be an integer. Please provide valid integers for source "
                          "priorities.")
                    return

                for number in input_data:

                    if is_isbn:
                        entry = {'isbn': number}
                    if is_oclc:
                        entry = {'oclc': number}

                    # Check sources in the specified priority order
                    for source in ordered_sources:

                        # Check if Harvard is the next source
                        if source == 'harvard' and not dont_use_harvard:
                            if not is_isbn:
                                print(
                                    "Error: Harvard API requires ISBN Values as Input. Please input a list of ISBN "
                                    "values to use this API.")
                                dont_use_harvard = True
                                break
                            entry = harvardAPI.parse_harvard_data(entry, number)

                        # Check if OCLC is the next source
                        elif source == 'oclc' and not dont_use_oclc:
                            if not is_oclc:
                                print(
                                    "Error: OCLC API requires OCLC Values as Input. Please input a list of OCLC "
                                    "values to use this API.")
                                dont_use_oclc = True
                                break
                            # TODO: If OCLC isn't scrapped from the project, its stuff will go here

                        # Check if LOC is the next source
                        elif source == 'loc':
                            entry = locAPI.parse_loc_data(entry, number, is_oclc)

                        # Check if OpenLibrary is the next source
                        elif source == 'openlibrary':
                            entry = openLibraryAPI.parse_open_library_data(entry, number, is_oclc, is_isbn)

                        elif source == 'google' and not dont_use_google:
                            config_file = config.load_config()
                            if config_file["google_api_key"] == "YOUR_GOOGLE_API_KEY":
                                print(
                                    "Error: Google Books API requires the user to have a Google API key saved using "
                                    "the --set-google-key option. Please input a key to use this API.")
                                dont_use_google = True
                                break
                            entry = googleAPI.parse_google_data(entry, number, is_oclc, is_isbn)

                        # Break out of the loop if data has been retrieved for the current source
                        if entry.get('oclc') and entry.get('oclc') != '' and entry.get('isbn') and entry.get(
                                'isbn') != '' and entry.get('lcc') and entry.get('lcc') != '':
                            break

                    # Append the entry to metadata
                    metadata.append(entry)

                if args.output:
                    # Write metadata to output file
                    write_to_output(metadata, args.output)
                else:
                    print("No output file requested. If an output file is desired please use the -o or --output option.")
            else:
                print("Error: Please provide source priorities using the --source-priorities option as well as "
                      "searchable sources using the --search-sources option")
        else:
            print("Error: Please provide an input file using the -i or --input option.")


if __name__ == "__main__":
    main()
