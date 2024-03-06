import harvardAPI
import locAPI
import openLibraryAPI
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
                        help="Specify internet sources to search (comma-separated). Examples include: harvard, oclc, "
                             "loc, openlibrary")
    parser.add_argument("--source-priorities", help="Specify priority levels for internet sources (comma-separated).")
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

        # Check which type of input data we have
        if len(input_data[0]) >= 10:
            is_isbn = True
            print("List Contains ISBN Values")
        elif len(input_data[0]) <= 9:
            is_oclc = True
            print("List Contains OCLC Values")

        # Initialize metadata list
        metadata = []

        if args.source_priorities:
            # Define the search order based on source priorities
            source_order = args.search_sources.lower().split(',')
            priority_order = [int(priority) for priority in args.source_priorities.split(',')]
            ordered_sources = [source for _, source in sorted(zip(priority_order, source_order))]
            print(ordered_sources)

            for number in input_data:

                if is_isbn:
                    entry = {'isbn': number}
                if is_oclc:
                    entry = {'oclc': number}

                # Check sources in the specified priority order
                for source in ordered_sources:

                    # Check if Harvard is the next source
                    if source == 'harvard':
                        if not is_isbn:
                            print(
                                "Harvard API requires ISBN Values as Input. Please input a list of ISBN values to use "
                                "this API.")
                            break
                        entry = harvardAPI.parse_harvard_data(entry, number)

                    # Check if OCLC is the next source
                    elif source == 'oclc':
                        if not is_oclc:
                            print(
                                "OCLC API requires OCLC Values as Input. Please input a list of OCLC values to use "
                                "this API.")
                            break
                        # TODO: If OCLC isn't scrapped from the project, its stuff will go here

                    # Check if LOC is the next source
                    elif source == 'loc':
                        entry = locAPI.parse_loc_data(entry, number, is_oclc)

                    # Check if OpenLibrary is the next source
                    elif source == 'openlibrary':
                        entry = openLibraryAPI.parse_open_library_data(entry, number, is_oclc, is_isbn)

                    # Break out of the loop if data has been retrieved for the current source
                    if entry.get('oclc') and entry.get('oclc') != '' and entry.get('isbn') and entry.get('isbn') != '' and entry.get('lcc') and entry.get('lcc') != '':
                        break

                # Append the entry to metadata
                metadata.append(entry)

            if args.output:
                # Write metadata to output file
                write_to_output(metadata, args.output)
            else:
                print("No output file requested. If an output file is desired please use the -o or --output option.")
        else:
            print("Error: Please provide source priorities using the --source-priorities option")
    else:
        print("Error: Please provide an input file using the -i or --input option.")


if __name__ == "__main__":
    main()
