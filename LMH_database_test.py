import unittest
import sqlite3
from LMH_database import Database

class TestDatabase(unittest.TestCase):
    def setUp(self):
        # Set up a temporary database for testing
        self.test_db_name = 'test_database.db'
        self.db_manager = Database(self.test_db_name)
        self.db_manager.create_table()

        self.isbns = ["1111111111", "2222222222"]
        self.ocn = "987654"
        self.lccn = "LC987654"
        self.lccn_source = "Library of Congress (Updated)"
        self.doi = "doi:10.5678/updated"

        
        self.db_manager.db_insert(self.isbns, self.ocn, self.lccn, self.lccn_source, self.doi)

    def tearDown(self):
        # Remove the temporary database after testing
        try:
            self.db_manager.close_connection()
        except sqlite3.Error:
            pass  # Ignore errors during teardown, as the database might not exist
        finally:
            import os
            if os.path.exists(self.test_db_name):
                os.remove(self.test_db_name)

    def test_insert_single_isbn(self):
        # Test inserting a single ISBN
        self.db_manager.db_insert(["1234567890"], "123456", "LC123456", "Library of Congress", "doi:10.1234/example")
        self.db_manager.open_connection()
        cursor = self.db_manager.connection.cursor()
        cursor.execute("SELECT * FROM metadata WHERE isbn=?", ("1234567890",))
        result = cursor.fetchone()
        # Verify that the data is in the database
        
        self.assertEqual(result, ("1234567890", "123456", "LC123456", "Library of Congress", "doi:10.1234/example"))

    def test_insert_multiple_isbns(self):
        # Test inserting multiple ISBNs
        isbns = ["2234567890", "0987654321", "5555555555"]
        self.db_manager.db_insert(isbns, "123459", "LC12345", "Library of Congress", "doi:10.1234/example")

        # Verify that each ISBN is in the database
        for isbn in isbns:
            self.db_manager.open_connection()
            cursor = self.db_manager.connection.cursor()
            cursor.execute("SELECT * FROM metadata WHERE isbn=?", (isbn,))
            result = cursor.fetchone()
            
            
            self.assertEqual(result, (isbn, "123459", "LC12345", "Library of Congress", "doi:10.1234/example"))

    def test_insert_ocn(self):
        # Test inserting with OCN
        self.db_manager.db_insert([], "112233", "LC123456", "Library of Congress", "doi:10.1234/example")
        # Verify that the data is in the database
        self.db_manager.open_connection()
        cursor = self.db_manager.connection.cursor()
        cursor.execute("SELECT * FROM metadata WHERE ocn=?", ("112233",))
        result = cursor.fetchone()
        
        self.assertEqual(result, ("null", "112233", "LC123456", "Library of Congress", "doi:10.1234/example"))

        self.db_manager.db_insert(["1111122222","2222233333"],"4433234","LC123456", "Library of Congress", "null")
        self.db_manager.open_connection()
        cursor = self.db_manager.connection.cursor()
        cursor.execute("SELECT * FROM metadata WHERE ocn=?", ("4433234",))
        result = cursor.fetchall()
        
        self.assertEqual(result, [("1111122222","4433234","LC123456", "Library of Congress", "null"),("2222233333","4433234","LC123456", "Library of Congress", "null")])


    def test_get_metadata_with_isbn(self):
        # Test getting metadata with ISBN
        
        for isbn in self.isbns:
            metadata = self.db_manager.get_metadata(isbn, "ISBN")
            expected_metadata = [isbn, self.ocn, self.lccn, self.lccn_source, self.doi]
            self.assertEqual(metadata, expected_metadata)

    def test_get_metadata_with_ocn(self):
        # Test getting metadata with OCN
        metadata = self.db_manager.get_metadata(self.ocn, "OCN")
        expected_metadata = [self.isbns, self.ocn, self.lccn, self.lccn_source, self.doi]
        self.assertEqual(metadata, expected_metadata)

    def test_get_metadata_not_in_database(self):
        # Test getting metadata for a number not in the database
        not_in_database_number = "9999999999"
        metadata = self.db_manager.get_metadata(not_in_database_number, "ISBN")
        self.assertEqual(metadata, [])

    def test_update_db_ocn(self):
        # Test updating with OCN, updating ISBN, and creating new records for additional ISBNs
        self.db_manager.db_insert([],"12344","584A2", "OCLC", "null")
        self.db_manager.update_db("12344", "OCN", ["11111222", "333333222"], "584A2", "OCLC", "100.200/doi")

        # Check if the data was updated correctly
        result = self.get_metadata("12344", "OCN")
        expected_result = [["11111222", "333333222"],"12344", "584A2", "OCLC", "100.200/doi"]
        self.assertEqual(result, expected_result)

        # Check if new records were created for additional ISBNs
        result_isbn_1 = self.get_metadata("11111222", "ISBN")
        result_isbn_2 = self.get_metadata("333333222", "ISBN")
        expected_result_isbn_1 = ["11111222", "12344", "584A2", "OCLC", "100.200/doi"]
        expected_result_isbn_2 = ["333333222", "12344", "584A2", "OCLC", "100.200/doi"]
        self.assertEqual(result_isbn_1, expected_result_isbn_1)
        self.assertEqual(result_isbn_2, expected_result_isbn_2)

    def test_update_db_isbn(self):
        # Test updating with ISBN, updating other metadata values
        self.db_manager.db_insert(["44334422"],"null","584A2", "OCLC", "null")
        self.db_manager.update_db("44334422", "ISBN", "55544433", "584A2", "OCLC", "100.200")

        # Check if the data was updated correctly
        result = self.get_metadata("44334422", "ISBN")
        expected_result = ["44334422", "55544433", "584A2", "OCLC", "100.200"]
        self.assertEqual(result, expected_result)

    def test_is_in_database(self):
        self.db_manager.db_insert(["2234567890"],"234524", "null", "null", "null")
        self.assertEqual(self.db_manager.is_in_database("2234567890", "ISBN"), True)
        self.assertEqual(self.db_manager.is_in_database("234524", "OCN"), True)
        self.assertEqual(self.db_manager.is_in_database("7777777", "ISBN"), False)
        self.assertEqual(self.db_manager.is_in_database("0990909", "OCN"), False)
        

    def test_clear_db(self):
        self.db_manager.open_connection()
        
        cursor = self.db_manager.connection.cursor()
        self.db_manager.clear_db()
        cursor.execute("SELECT * FROM metadata")
        result = cursor.fetchall()
        self.assertEqual(len(result), 0)

    def get_metadata(self, number, isbn_or_ocn):
        # Helper function to retrieve metadata for testing
        return self.db_manager.get_metadata(number, isbn_or_ocn)
    
if __name__ == '__main__':
    unittest.main()