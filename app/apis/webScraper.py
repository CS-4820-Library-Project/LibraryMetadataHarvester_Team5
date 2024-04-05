import os
import requests
import re
from app import config, logs
from app import callNumberValidation
from datetime import timedelta
from ratelimit import limits, sleep_and_retry

download_directory = r'web_pages'


def extract_highlighted_items(html_content):
    document_id_pattern = r'&amp;document_id=(\d+)&amp;|href="/catalog/([A-Z0-9]+)"'
    matches = re.findall(document_id_pattern, html_content)

    document_ids = set()
    for match in matches:
        # Only add the non-empty part of the tuple
        document_id = next(item for item in match if item)
        document_ids.add(document_id)

    return document_ids


def read_html_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    return html_content


@sleep_and_retry
@limits(calls=10, period=timedelta(seconds=10).total_seconds())
def download_webpage(url, file_path):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(response.text)
            return True
        else:
            logs.log_error(f"Failed to download {url}. Status code: {response.status_code}")
            return False
    except Exception as e:
        logs.log_error(f"Exception occurred during website download: {e}")
        return False


def extract_lccn_numbers(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Patterns for the first and second parts of LCCN numbers
    id_no_1_patterns = [
        r'<span class="sub_code">a\|</span>\s*([A-Z0-9]+\.[A-Z0-9]+)\s*<',
        r'<span class=\'sub_code\'>\|a</span>\s*([A-Z0-9]+\.[A-Z0-9]+)\s*',
        r'LCCN:\s*(\d+)'  # New pattern to match the third HTML structure
    ]
    id_no_2_patterns = [
        r'<span class="sub_code">b\|</span>\s*([A-Z0-9]+\s+[0-9]+[a-z]*)\s*<',
        r'<span class=\'sub_code\'>\|b</span>\s*([A-Z0-9]+\s+[0-9]+)\s*'
    ]

    lccn_numbers = set()
    for pattern_1, pattern_2 in zip(id_no_1_patterns, id_no_2_patterns):
        id_no_1_matches = re.findall(pattern_1, html_content)
        id_no_2_matches = re.findall(pattern_2, html_content)

        for id_no_1, id_no_2 in zip(id_no_1_matches, id_no_2_matches):
            lccn_numbers.add(f"{id_no_1} {id_no_2}")

    # New addition to handle the third pattern
    id_no_3_matches = re.findall(id_no_1_patterns[2], html_content)
    lccn_numbers.update(id_no_3_matches)

    return list(lccn_numbers)


def extract_oclc_numbers(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Patterns to match different OCoLC number formats
    oclc_patterns = [
        r'\(OCoLC\)(?:ocn|ocm)?(\d+)',
        r'<dt class="blacklight-oclc_number">\s*OCLC Number:\s*</dt>\s*(\d+)'  # New pattern for the additional format
    ]

    oclc_numbers = set()
    for pattern in oclc_patterns:
        oclc_matches = re.findall(pattern, html_content)
        # Normalize numbers by removing leading zeros
        normalized_matches = {match.lstrip('0') for match in oclc_matches}
        oclc_numbers.update(normalized_matches)

    return list(oclc_numbers)


def parse_data(entry, number, retrieval_settings, library):
    config_file = config.load_config()

    if not os.path.exists(download_directory):
        os.makedirs(download_directory)

    for key, urls in config_file["web_scraping_sources"].items():
        if library == key:
            # Construct and download the main URL
            main_url = urls[0].format(number=number)
            main_file_path = os.path.join(download_directory, f'{number}.html')
            if download_webpage(main_url, main_file_path):
                # Extract document IDs from the main page
                main_html_content = read_html_file(main_file_path)
                extracted_ids = extract_highlighted_items(main_html_content)

                # Delete the main webpage file after extraction
                os.remove(main_file_path)

                # Process each document ID
                for doc_id in extracted_ids:
                    # Adjust the URL based on the format of the document ID
                    if re.match(r'^[A-Z]+\d+$', doc_id):
                        doc_url = f"{urls[1]}/{doc_id}"
                    else:
                        doc_url = f"{urls[1]}/{doc_id}/librarian_view"

                    doc_file_path = os.path.join(download_directory, f'{doc_id}.html')
                    if download_webpage(doc_url, doc_file_path):
                        lccn_values = extract_lccn_numbers(doc_file_path)
                        oclc_values = extract_oclc_numbers(doc_file_path)

                        if lccn_values:
                            if (entry.get('lccn') == '' or entry.get('lccn') is None and
                                    retrieval_settings['retrieve_lccn'] and
                                    callNumberValidation.validate_lc_call_number(lccn_values[0])):
                                entry.update({
                                    'lccn': lccn_values[0],
                                    'source': library
                                })
                        if oclc_values:
                            if entry.get('oclc') == '' or entry.get('oclc') is None and retrieval_settings['retrieve_oclc']:
                                entry.update({
                                    'oclc': oclc_values[0],
                                })

                        # Delete the document webpage file after extraction
                        os.remove(doc_file_path)
                    else:
                        logs.log_error(f"Failed to download page for document ID: {doc_id}")
            else:
                logs.log_error(f"Failed to download main page for value: {number}")
    return entry
