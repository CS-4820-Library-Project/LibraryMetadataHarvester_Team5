from LMH_database import Database  # Import your Database class
import subprocess
db_manager = Database("LMH_database.db")


def save_metadata_to_file(metadata, filename):         # Test function to save the output into a text file, could be removed later
    with open(filename, 'a', encoding='utf-8') as file:
        for isbn, entries in metadata.items():
            file.write(f"ISBN: {isbn}\n")
            for entry in entries:
                file.write(f"Library: {entry['Library']}\n")
                file.write(f"Field Value: {entry['Field Value']['value']}\n")
            file.write("\n")


def parse_text_marc(text_marc):
    # Split the text MARC records by lines
    lines = text_marc.strip().split('\n')

    # Dictionary to store MARC data
    marc_data = {}

    for line in lines:
        # Check if line starts with a MARC field such as "050  "
        if len(line) >= 4 and line[:3].isdigit():
            tag = line[:3]
            indicators = line[4:6]
            value = line[7:].strip()
            marc_data[tag] = {
                'indicators': indicators,
                'value': value
            }
            # if tag == '050':
            # print(f"{line}: tag:{tag};indicators:{indicators};value:{value}")

    return marc_data


def run_yaz_client(isbn, targetstring, returnfield):    # Requires the user to input the path to yaz-client.exe file
    commands = f"""
    open {targetstring}
    find @attr 1=7 {isbn}
    show 1
    quit
    """
    process = subprocess.run(['C:\\Program Files\\YAZ\\bin\\yaz-client'], input=commands, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')



    # Check for errors
    if process.stderr:
        print("Error:", process.stderr)
        return None  # Exit if there was an error

    # Process the MARC record text and extract the specified field
    if process.stdout:
        marc_data = parse_text_marc(process.stdout)

        # Return the specified field data if found
        if returnfield in marc_data:
            return marc_data[returnfield]
        else:
            return None
    return None


def insert_metadata_into_db(isbn, field_value, library_name):
    # Assuming you have an instance of your Database class called db_manager

    # Insert the metadata into the database
    db_manager.open_connection()
    db_manager.insert_isbn(isbn=isbn, ocns=[], lccn=field_value, doi="", source=library_name)
    db_manager.close_connection()


def process_isbns_from_file(filename, target_sources, record_field_to_return):
    metadata = {}
    with open(filename, 'r') as file:
        isbns = file.readlines()

    for isbn in isbns:
        isbn = isbn.strip()  # Remove leading/trailing whitespace, newline characters, etc.
        print(f"Processing ISBN: {isbn}")
        for library, target_string in target_sources.items():
            try:
                field_value = run_yaz_client(isbn, target_string, record_field_to_return)
                if field_value:
                    metadata_entry = {'Library': library, 'Field Value': field_value}
                    if isbn in metadata:
                        metadata[isbn].append(metadata_entry)
                    else:
                        metadata[isbn] = [metadata_entry]
                    insert_metadata_into_db(isbn, field_value['value'], library)
                    print(f"Metadata inserted into the database for ISBN {isbn} from {library}.")
                else:
                    print(f"Metadata for ISBN {isbn} not found in {library}.")
            except Exception as e:
                print(f"An error occurred while processing ISBN {isbn} from {library}: {str(e)}")
                continue  # Continue processing the remaining libraries
    save_metadata_to_file(metadata, output_filename)




# Define your target sources (libraries) and their corresponding target strings
target_sources = {
    "LOC": "lx2.loc.gov:210/LCDB",
    "Yale": "z3950.library.yale.edu:7090/voyager",
    "UVa": "virgo.lib.virginia.edu:2200/unicorn",
    "UAlberta": "ualapp.library.ualberta.ca:2200/unicorn",
    "Oxford": "library.ox.ac.uk:210/44OXF_INST",
    "Mich": "141.215.16.4:210/INNOPAC",
    "UCLA": "z3950.library.ucla.edu:1921/01UCS_LAL",
    "Cambridge": "newton.lib.cam.ac.uk:7790/voyager",
    "NLA": "catalogue.nla.gov.au:7090/voyager",
    "NCSU": "sirsi.lib.ncsu.edu:2200/UNICORN",
    "Toronto": "utoronto.alma.exlibrisgroup.com:1921/01UTORONTO_INST",
    "NLAus": "catalogue.nla.gov.au:7090/voyager",
    "UBC": "ils.library.ubc.ca:7090/Voyager",
    "DUKE": "catalog.library.duke.edu:9991/DUK01",
    "IUCAT": "libprd.uits.indiana.edu:2200/UNICORN",
    "QUEENS": "ocul-qu.alma.exlibrisgroup.com:210/01OCUL_QU",
    "UCB": "berkeley.alma.exlibrisgroup.com:1921/01UCS_BER/UCB",
    "NYU": "aleph.library.nyu.edu:9991/NYU01PUB",
    "UPenn": "na03.alma.exlibrisgroup.com:1921/01UPENN_INST",
    "NYPL": "nyst.sirsi.net:8419/unicorn"
    # Add more libraries as needed
}

# Define the filename containing the list of ISBNs
filename = "test_data/small_sample_isbns.txt"

output_filename = "metadata_output.txt"

# Define the MARC record field to return
record_field_to_return = "050"

# Process ISBNs from the file and search each library for metadata
process_isbns_from_file(filename, target_sources, record_field_to_return)
