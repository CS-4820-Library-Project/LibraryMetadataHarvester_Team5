import requests
from lxml import html
import sqlite3


def scrape_worldcat(isbn, url):
    # Construct the search URL with the ISBN
    search_url = f"{url}search?isbn={isbn}"
    response = requests.get(search_url)
    if response.status_code != 200:
        return None  # Handle HTTP errors

    tree = html.fromstring(response.content)

    # Extract metadata using XPath or CSS Selectors based on the page structure
    title = tree.xpath('//div[contains(@class, "title")]/text()')[0]
    author = tree.xpath('//div[contains(@class, "author")]/text()')[0]

    return {
        "isbn": isbn,
        "title": title.strip() if title else "Unknown",
        "author": author.strip() if author else "Unknown",
        "source": "WorldCat"
    }


def scrape_blacklight(isbn, url):
    # Construct the search URL with the ISBN
    search_url = f"{url}search?isbn={isbn}"
    response = requests.get(search_url)
    if response.status_code != 200:
        return None  # Handle HTTP errors

    tree = html.fromstring(response.content)

    # Extract metadata using XPath or CSS Selectors based on the page structure
    # Example (this will vary depending on the actual page structure):
    title = tree.xpath('//div[contains(@class, "title")]/text()')[0]
    author = tree.xpath('//div[contains(@class, "author")]/text()')[0]

    return {
        "isbn": isbn,
        "title": title.strip() if title else "Unknown",
        "author": author.strip() if author else "Unknown",
        "source": "Blacklight"
    }


class MetadataScraper:
    def __init__(self, isbn_list):
        self.isbn_list = isbn_list
        self.db_connection = sqlite3.connect('metadata.db')
        self.db_cursor = self.db_connection.cursor()
        self.setup_database()
        # URLs for Blacklight and WorldCat catalogs
        self.blacklight_urls = [
            "https://search.lib.virginia.edu/",
            "https://searchworks.stanford.edu/",
            "https://catalyst.library.jhu.edu/",
            "https://newcatalog.library.cornell.edu",
            "https://catalog.lib.ncsu.edu",
            "https://find.library.duke.edu",
            "https://catalog.libraries.psu.edu/",
            "https://iucat.iu.edu/"
            # ... more URLs can be added here
        ]
        self.worldcat_urls = [
            "https://mcgill.on.worldcat.org/discovery",
            "https://canada.on.worldcat.org/discovery"
            # ... more URLs can be added here
        ]

    def setup_database(self):
        self.db_cursor.execute('''CREATE TABLE IF NOT EXISTS metadata 
                                  (isbn TEXT, ocns TEXT, iccn TEXT, source TEXT)''')
        self.db_connection.commit()

    def scrape_metadata(self):
        for isbn in self.isbn_list:
            metadata_found = False

            # First try to scrape from Blacklight URLs
            for url in self.blacklight_urls:
                metadata = scrape_blacklight(isbn, url)
                if metadata:
                    self.save_metadata(isbn, metadata)
                    metadata_found = True
                    break  # Exit Blacklight loop once metadata is found

            # If metadata not found in Blacklight, try WorldCat URLs
            if not metadata_found:
                for url in self.worldcat_urls:
                    metadata = scrape_worldcat(isbn, url)
                    if metadata:
                        self.save_metadata(isbn, metadata)
                        break  # Exit WorldCat loop once metadata is found

    def save_metadata(self, isbn, metadata):
        # Save the scraped metadata to the SQLite database
        self.db_cursor.execute('''INSERT INTO metadata (isbn, ocns, iccn, source)
                                  VALUES (?, ?, ?, ?)''',
                               (isbn, metadata['title'], metadata['author'], metadata['source']))
        self.db_connection.commit()

    def close(self):
        self.db_connection.close()
