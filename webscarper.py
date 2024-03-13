import requests
from lxml import html
from app.database.LMH_database import Database
from lmh_logging import log_error, log_info


class MetadataScraper:
    def __init__(self, isbn_list):
        self.database = Database()
        self.isbn_list = isbn_list
        self.setup_database()
        self.urls = {
            'blacklight': [
                "https://search.lib.virginia.edu/",
                "https://searchworks.stanford.edu/",
                "https://catalyst.library.jhu.edu/",
                "https://newcatalog.library.cornell.edu",
                "https://catalog.lib.ncsu.edu",
                "https://find.library.duke.edu",
                "https://catalog.libraries.psu.edu/",
                "https://iucat.iu.edu/"
                # ... more URLs can be added here
            ],
            'worldcat': [
                "https://mcgill.on.worldcat.org/discovery",
                "https://canada.on.worldcat.org/discovery"
                # ... more URLs can be added here
            ]
        }

    def setup_database(self):
        # Utilize the Database class for database setup
        self.database.open_connection()

    def scrape_metadata(self, isbn, source):
        search_url = f"{self.urls[source][0]}search?isbn={isbn}"
        try:
            response = requests.get(search_url)
            response.raise_for_status()
            tree = html.fromstring(response.content)
            title = tree.xpath('//div[contains(@class, "title")]/text()')[0].strip()
            author = tree.xpath('//div[contains(@class, "author")]/text()')[0].strip()
            return {"isbn": isbn, "title": title or "Unknown", "author": author or "Unknown", "source": source}
        except requests.RequestException as e:
            log_error(f"Error scraping {source}: {e}")
            return None

    def run_scraper(self):
        for isbn in self.isbn_list:
            for source in self.urls:
                metadata = self.scrape_metadata(isbn, source)
                if metadata:
                    self.save_metadata(isbn, metadata)
                    break  # Exit loop once metadata is found

    def save_metadata(self, isbn, metadata):
        try:
            # Using Database class methods for data insertion
            self.database.insert_isbn(isbn, metadata)
            log_info(f"Metadata saved for ISBN: {isbn}")
        except Exception as e:
            log_error(f"Error saving metadata for ISBN {isbn}: {e}")

    def close(self):
        self.database.close_connection()


# Main execution logic
if __name__ == "__main__":
    # Example usage
    scraper = MetadataScraper(['9780131103627', '9780131103628'])  # Sample ISBN list
    scraper.run_scraper()
    scraper.close()
