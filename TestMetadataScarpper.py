import unittest
import webscarper  # Replace 'your_module' with the actual module name


class TestMetadataScraper(unittest.TestCase):
    def setUp(self):
        # Example ISBN list for testing
        self.test_isbn_list = ['9781234567897', '9781234567898']
        # Initialize the MetadataScraper object
        self.scraper = webscarper.MetadataScraper(self.test_isbn_list)

    def test_insert_isbn(self):
        # Test the insert_isbn method
        test_data = {
            "isbn": "9781234567897",
            "ocns": ["ocn1", "ocn2"],
            "lccn": "lccn123",
            "doi": "doi123",
            "source": "Harvard"
        }
        self.scraper.insert_isbn(test_data["isbn"], test_data["ocns"], test_data["lccn"], test_data["doi"],
                                 test_data["source"])

        # Query the database to verify the insertion
        self.scraper.db_cursor.execute("SELECT * FROM metadata WHERE isbn = ?", (test_data["isbn"],))
        result = self.scraper.db_cursor.fetchone()

        # Assert that the data matches
        self.assertIsNotNone(result)
        self.assertEqual(result[0], test_data["isbn"])
        self.assertEqual(result[1], ', '.join(test_data["ocns"]))
        self.assertEqual(result[2], test_data["lccn"])
        self.assertEqual(result[3], test_data["doi"])
        self.assertEqual(result[4], test_data["source"])

    def tearDown(self):
        # Clean up and close the database connection
        self.scraper.db_cursor.execute("DELETE FROM metadata")
        self.scraper.db_connection.commit()
        self.scraper.close()


if __name__ == '__main__':
    unittest.main()
