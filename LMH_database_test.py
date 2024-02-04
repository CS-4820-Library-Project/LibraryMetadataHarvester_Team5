import unittest
import sqlite3
from LMH_database import Database

class TestDatabase(unittest.TestCase):
    def setUp(self):
        # Set up a temporary database for testing
        self.test_db_name = 'test_database.db'
        self.db_manager = Database(self.test_db_name)
        self.db_manager.create_table()

        
        

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

    def test_insert_isbn(self):
        # Test case for inserting ISBN data into the database

        # Data for testing
        isbn = "1234567890"
        ocns = ["ocn1", "ocn2"]
        lccn = "lccn123"
        doi = "doi123"
        source = "test_source"

        # Insert ISBN data into the database
        self.db_manager.insert_isbn(isbn=isbn, ocns=ocns, lccn=lccn, doi=doi, source=source)

        # Retrieve the inserted data from the database
        self.db_manager.open_connection()
        cursor = self.db_manager.connection.cursor()
        result = cursor.execute("SELECT * FROM metadata WHERE isbn=? AND isbn_source=?", (isbn, "input")).fetchone()
        cursor.close()

        # Assertions to check if the data was inserted correctly
        self.assertIsNotNone(result)  # Check if the result is not None (i.e., data is found)
        self.assertEqual(result[0], isbn)  # ISBN should match
        self.assertEqual(result[1], "input")  # ISBN source should match
        self.assertEqual(result[2], ocns[0])  # First OCN should match
        self.assertEqual(result[3], source)  # OCN source should match
        self.assertEqual(result[4], lccn)  # LCCN should match
        self.assertEqual(result[5], source)  # LCCN source should match
        self.assertEqual(result[6], doi)  # DOI should match
        self.assertEqual(result[7], source)  # DOI source should match


    def test_insert_ocn(self):
        # Test case for inserting ISBN data into the database

        # Data for testing
        isbns = ["83425","1234567890"]
        ocn = "18395"
        lccn = "lccn123"
        doi = "doi123"
        source = "test_source"

        # Insert ISBN data into the database
        self.db_manager.insert_ocn(ocn=ocn, isbns=isbns, lccn=lccn, doi=doi, source=source)
        

        # Retrieve the inserted data from the database
        self.db_manager.open_connection()
        cursor = self.db_manager.connection.cursor()
        result = cursor.execute("SELECT * FROM metadata WHERE ocn=? AND ocn_source=?", (ocn, "input")).fetchone()
        cursor.close()

        # Assertions to check if the data was inserted correctly
        self.assertIsNotNone(result)  # Check if the result is not None (i.e., data is found)
        self.assertEqual(result[0], isbns[0])  # ISBN should match
        self.assertEqual(result[1], source)  # ISBN source should match
        self.assertEqual(result[2], ocn)  # First OCN should match
        self.assertEqual(result[3], "input")  # OCN source should match
        self.assertEqual(result[4], lccn)  # LCCN should match
        self.assertEqual(result[5], source)  # LCCN source should match
        self.assertEqual(result[6], doi)  # DOI should match
        self.assertEqual(result[7], source)  # DOI source should match



    def test_get_isbn_metadata(self):
       
        isbn = "1234567890"
        source = "test_source2"

        
        # Insert data into the database for the test
        self.db_manager.insert_isbn(isbn, ["3849", "3344"], "B18 23", "100.400", source)

        
        result = self.db_manager.get_isbn_metadata(isbn, source)

        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 5)  
        self.assertEqual(result, ["1234567890", ["3849","3344"], "B18 23","test_source2", "100.400"])
        

    def test_get_ocn_metadata(self):
        
        ocn = "432532"
        source = "test_source3"

        
        # Insert data into the database for the test
        self.db_manager.insert_ocn(ocn, ["21431", "53241"], "B18 23", "100.400", source)

        
        result = self.db_manager.get_ocn_metadata(ocn, source)

        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 5)  
        self.assertEqual(result, [ ["21431","53241"],"432532", "B18 23","test_source3", "100.400"])
        
        

    def test_clear_db(self):
        self.db_manager.open_connection()
        
        cursor = self.db_manager.connection.cursor()
        self.db_manager.clear_db()
        cursor.execute("SELECT * FROM metadata")
        result = cursor.fetchall()
        self.assertEqual(len(result), 0)

    
    
if __name__ == '__main__':
    unittest.main()