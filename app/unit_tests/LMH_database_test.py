import unittest
import sqlite3
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "database")))
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
        ocn = "1684013"
        lccn = "lccn123"
        source = "test_source"

        # Insert ISBN data into the database
        self.db_manager.insert(isbn=isbn, ocn=ocn, lccn=lccn, lccn_source=source)

        # Retrieve the inserted data from the database
        self.db_manager.open_connection()
        cursor = self.db_manager.connection.cursor()
        result = cursor.execute("SELECT * FROM metadata WHERE isbn=?", (isbn,)).fetchone()
        cursor.close()

        # Assertions to check if the data was inserted correctly
        self.assertIsNotNone(result)  # Check if the result is not None (i.e., data is found)
        self.assertEqual(result[0], isbn)  # ISBN should match
        self.assertEqual(result[1], ocn)  # OCN  should match
        self.assertEqual(result[2], lccn)  # LCCN  should match
        self.assertEqual(result[3], source)  # LCCN source should match
        


    def test_insert_ocn(self):
        # Test case for inserting ISBN data into the database

        # Data for testing
        isbn = "1234567890"
        ocn = "18395"
        lccn = "lccn123"
        source = "test_source"

        # Insert ISBN data into the database
        self.db_manager.insert(isbn, ocn, lccn, source)
        

        # Retrieve the inserted data from the database
        self.db_manager.open_connection()
        cursor = self.db_manager.connection.cursor()
        result = cursor.execute("SELECT * FROM metadata WHERE ocn=?", (ocn,)).fetchone()
        cursor.close()

        # Assertions to check if the data was inserted correctly
        self.assertIsNotNone(result)  # Check if the result is not None (i.e., data is found)
        self.assertEqual(result[0], isbn)  # ISBN should match
        self.assertEqual(result[1], ocn)  # OCN  should match
        self.assertEqual(result[2], lccn)  # LCCN  should match
        self.assertEqual(result[3], source)  # source should match
        



    def test_get_isbn_metadata(self):
        # make sure insert function is working first
        isbn = "1234522890"
        ocn = "82940283"
        source = "test_source4"
        lccn = "lccn-831"
        source2 = "test-source5"
        lccn2 = "lccn-184"
        ocn2 = "14715783"

        
        
        self.db_manager.open_connection()
        cursor = self.db_manager.connection.cursor()
        cursor.execute("INSERT INTO metadata (isbn, ocn, lccn, lccn_source) VALUES (?, ?, ?, ?)", (isbn, ocn, lccn, source))
        cursor.execute("INSERT INTO metadata (isbn, ocn, lccn, lccn_source) VALUES (?, ?, ?, ?)", (isbn, ocn2, lccn2, source2))
        self.db_manager.connection.commit()
        self.db_manager.close_connection()
        

        
        result = self.db_manager.get_metadata(isbn, 0)
        
        

        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)  
        self.assertEqual(result, [isbn, ocn, [(lccn,source), (lccn2, source2)]])
        

    
    def test_get_ocn_metadata(self):
        # make sure insert function is working first
        isbn = "1234522890"
        ocn = "82940283"
        source = "test_source4"
        lccn = "lccn-831"
        source2 = "test-source5"
        lccn2 = "lccn-184"
        ocn2 = "14715783"

        
        
        self.db_manager.open_connection()
        cursor = self.db_manager.connection.cursor()
        cursor.execute("INSERT INTO metadata (isbn, ocn, lccn, lccn_source) VALUES (?, ?, ?, ?)", (isbn, ocn, lccn, source))
        cursor.execute("INSERT INTO metadata (isbn, ocn, lccn, lccn_source) VALUES (?, ?, ?, ?)", (isbn, ocn, lccn2, source2))
        self.db_manager.connection.commit()
        self.db_manager.close_connection()
        

        
        result = self.db_manager.get_metadata(ocn, 1)
        
        

        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)  
        self.assertEqual(result, [isbn, ocn, [(lccn,source), (lccn2,source2)]])



    def test_clear_db(self):
        self.db_manager.open_connection()
        
        cursor = self.db_manager.connection.cursor()
        cursor.execute("INSERT INTO metadata (isbn, ocn, lccn, lccn_source) VALUES (?, ?, ?, ?)", ("14214215", "812941", "ABC 2002", "OL"))
        self.db_manager.connection.commit()
        self.db_manager.clear_db()
        cursor.execute("SELECT * FROM metadata")
        result = cursor.fetchall()
        self.assertEqual(len(result), 0)


    def test_isbn_not_in_db(self):
        result = self.db_manager.get_metadata("1748129424", 0)
        self.assertIsInstance(result, list)
        self.assertEqual(result, ["1748129424", '', []])

    
    
if __name__ == '__main__':
    unittest.main()