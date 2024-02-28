import sqlite3
from sqlite3 import Error

class Database:
    def __init__(self, database_name='database.db'):
        """
        The initialization of a Database object. Creates the
        appropriate table inside the database

        Parameters:
        - database_name: Name of the database file to be used. String

        """
        self.database_name = database_name
        self.connection = None
        self.create_table()

    def open_connection(self):
        """
        Function that opens the connection to the database
        """
        self.connection = sqlite3.connect(self.database_name)

    def close_connection(self):
        """
        Function that closes the connection to the database
        """
        if self.connection:
            self.connection.close()

    def create_table(self):
        """
        Function that creates the appropriate table inside the
        database. Table is called 'metadata' and only contains
        text. 
        """
        try:
            self.open_connection()
            cursor = self.connection.cursor()

            # Create the 'metadata' table if it doesn't exist
            cursor.execute('''CREATE TABLE IF NOT EXISTS metadata (
                            isbn TEXT,
                            isbn_source TEXT,
                            ocn TEXT,
                            ocn_source TEXT,
                            lccn TEXT,
                            lccn_source TEXT,
                            doi TEXT)''')
            self.connection.commit()

        except sqlite3.Error as e:
            print(f"Error: {e}")

        finally:
            self.close_connection()

    def insert_isbn(self, isbn, ocns, lccn, doi, source):
        """
        Function that inserts an ISBN and metadata into the database.

        Parameters:
        - isbn: String that represents the ISBN that will be inserted.

        - ocns: List of strings that represent the OCN for an ISBN.

        -lccn: String that represents the LCCN for an ISBN.

        -doi: String that represents the doi for an ISBN.

        -source: String that represensts source used to get data.

        """
        try:
            self.open_connection()
            cursor= self.connection.cursor()
            # For each OCN provided, insert a new record in the database if it does not already exist.
            for item in ocns:
                x = cursor.execute('''SELECT * FROM metadata WHERE isbn=? 
                                   AND isbn_source=? AND ocn=? AND ocn_source=? AND lccn=? 
                                   AND lccn_source=? AND doi=?''', (isbn, "input", item, source, lccn, source, doi)).fetchall()
                
                if len(x) == 0:
                    cursor.execute("INSERT INTO metadata (isbn, isbn_source, ocn, ocn_source, lccn, lccn_source, doi) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                       (isbn, "input", item, source, lccn, source, doi))
                    
                self.connection.commit()

        except sqlite3.Error as e:
            print(f"Error: {e}")
            self.connection.rollback()

        finally:
            self.close_connection()


    def insert_ocn(self, ocn, isbns, lccn, doi, source):
        """
        Function that inserts an OCN and metadata into the database.

        Parameters:
        - ocn: String that represents the OCN that will be inserted.

        - isbns: List of strings that represent the ISBNs for an OCN.

        -lccn: String that represents the LCCN for an ISBN.

        -doi: String that represents the doi for an ISBN.

        -source: String that represensts source used to get data.

        """
        try:
            self.open_connection()
            cursor= self.connection.cursor()

            # For each ISBN provided, insert a new record in the database if it does not exits already.
            for item in isbns:
                x = cursor.execute('''SELECT * FROM metadata WHERE isbn=? 
                                   AND isbn_source=? AND ocn=? AND ocn_source=? AND lccn=? 
                                   AND lccn_source=? AND doi=?''', (item, source, ocn, "input", lccn, source, doi)).fetchall()
                
                if len(x) == 0:
                    cursor.execute("INSERT INTO metadata (isbn, isbn_source, ocn, ocn_source, lccn, lccn_source, doi) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                       (item, source, ocn, "input", lccn, source, doi))
                    
                self.connection.commit()

        except sqlite3.Error as e:
            print(f"Error: {e}")
            self.connection.rollback()

        finally:
            self.close_connection()





    def is_in_database(self, number, isbn_or_ocn):
        """
        Function that determines if an ISBN or OCN number is
        already in the database.

        Parameters:
        - number: String that represents the ISBN or OCN number
                  that will be looked up.

        - isbn_or_ocn: String. "OCN" if the number is an OCN
                       "ISBN" if the number is an ISBN.

        Returns:
        -True if the number is in the database.
        -False if the number is not in the database.
        """
        try:
            self.open_connection()
            cursor = self.connection.cursor()

            # If number is an ISBN, look for that ISBN in the database
            if isbn_or_ocn == 'ISBN':
                cursor.execute("SELECT isbn FROM metadata WHERE isbn=?", (number,))

                # If ISBN is in the database return True, else return False
                if len(cursor.fetchall()) > 0:
                    return True
                else:
                    return False

            # If number is an OCN, look for it in the database
            if isbn_or_ocn == 'OCN':
                cursor.execute("SELECT ocn FROM metadata WHERE ocn=?", (number,))

                # If OCN is in the database return True, else return False
                if len(cursor.fetchall()) > 0:
                    return True
                else:
                    return False

        except sqlite3.Error as e:
            print(f"Error: {e}")

        finally:
            self.close_connection()

    def get_isbn_metadata(self, isbn, source):
        """
        Function that returns metdata for a specific ISBN and source

        Parameters:
        -isbn: String of ISBN number you want to get metadata for.

        -source: String of the source used to obtain the metadata.

        Returns:
        A list of metadata will be returned in the following format:
        [isbn, ocns, lccn, lccn_source, doi]

        -isbn: String, same ISBN used in the parameters.

        -ocns: List of strings, any OCNs that match the ISBN and source provided.

        -lccn: String, lccn that matched the ISBN and source provided.

        -lccn_source: String, will be the same source provided in the parameter

        -doi: String, doi that matched the ISBN and source provided

        Note: If no values are found, "null" will be used.

        """
        try:
            self.open_connection()
            cursor = self.connection.cursor()

            ocn = cursor.execute("SELECT ocn FROM metadata WHERE isbn=? AND ocn_source=?", (isbn, source)).fetchall()
            ocn = [item[0] for item in ocn]
            if ocn is None:
                ocn = "null"

            lccn = cursor.execute("SELECT lccn FROM metadata WHERE isbn=? AND lccn_source=?", (isbn, source)).fetchone()
            lccn_source=source
            if lccn is None:
                lccn = "null"
                lccn_source = "null"

            doi = cursor.execute("SELECT doi FROM metadata WHERE isbn=?", (isbn,)).fetchone()
            if doi is None:
                doi = "null"

            return [isbn, ocn, lccn[0], lccn_source, doi[0]]
        
        except sqlite3.Error as e:
            print(f"Error: {e}")
            return []
        
        finally:
            self.close_connection()


    def get_ocn_metadata(self, ocn, source):
        """
        Function that returns metdata for a specific OCN and source

        Parameters:
        -ocn: String of OCn number you want to get metadata for.

        -source: String of the source used to obtain the metadata.

        Returns:
        A list of metadata will be returned in the following format:
        [isbn, ocn, lccn, lccn_source, doi]

        -isbns: List of strings, ISBNs that match the OCN and source.

        -ocn: String, OCN that was provided in the parameters.

        -lccn: String, lccn that matched the OCN and source provided.

        -lccn_source: String, will be the same source provided in the parameter

        -doi: String, doi that matched the OCN and source provided

        Note: If no values are found, "null" will be used.

        """
        try:
            self.open_connection()
            cursor = self.connection.cursor()

            isbns = cursor.execute("SELECT isbn FROM metadata WHERE ocn=? AND isbn_source=?", (ocn, source)).fetchall()
            isbns = [item[0] for item in isbns]
            if isbns is None:
                ocn = "null"

            lccn = cursor.execute("SELECT lccn FROM metadata WHERE ocn=? AND lccn_source=?", (ocn, source)).fetchone()
            lccn_source=source
            if lccn is None:
                lccn = "null"
                lccn_source = "null"

            doi = cursor.execute("SELECT doi FROM metadata WHERE ocn=?", (ocn,)).fetchone()
            if doi is None:
                doi = "null"

            return [isbns, ocn, lccn[0], lccn_source, doi[0]]
        
        except sqlite3.Error as e:
            print(f"Error: {e}")
            return []
        
        finally:
            self.close_connection()



    def clear_db(self):
        """
        Function that deletes all of the data inside the database.
        The table in the database will be left.

        """
        try:
            self.open_connection()
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM metadata")
            self.connection.commit()

        except sqlite3.Error as e:
            print(f"Error: {e}")

        finally:
            self.close_connection()

    def view_table_contents(self):
        """
        Function for viewing the contents of the database.
        Will print all of the data to the console.
        """
        try:
            self.open_connection()
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM metadata")
            rows = cursor.fetchall()

            for row in rows:
                print(row)

        except sqlite3.Error as e:
            print(f"Error viewing data: {e}")

        finally:
            self.close_connection()

    

