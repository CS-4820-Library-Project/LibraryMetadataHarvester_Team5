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
                            ocn TEXT,
                            lccn TEXT,
                            lccn_source TEXT)''')
            self.connection.commit()

        except sqlite3.Error as e:
            print(f"Error: {e}")

        finally:
            self.close_connection()

    def insert(self, isbn, ocn, lccn, lccn_source):
        """
        Function that inserts an ISBN OCN and LCCN into the database.

        Parameters:
        - isbn: String that represents the ISBN that will be inserted.

        - ocn: String that represents the OCN.

        -lccn: String that represents the LCCN.

        -lccn_source: String that represensts source used to get LCCN.

        """
        try:
            self.open_connection()
            cursor = self.connection.cursor()
            # For each OCN provided, insert a new record in the database if it does not already exist.

            x = cursor.execute('''SELECT * FROM metadata WHERE isbn=? AND ocn=? AND lccn=? AND lccn_source=?''',
                               (isbn, ocn, lccn, lccn_source)).fetchall()

            if len(x) == 0:
                cursor.execute(
                    "INSERT INTO metadata (isbn, ocn, lccn, lccn_source) VALUES (?, ?, ?, ?)",
                    (isbn, ocn, lccn, lccn_source))

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

    def get_metadata(self, number, type):
        """
        Function that returns metdata for a specific ISBN and source

        Parameters:
        -number: String of number(ISBN or OCN) you want to get metadata for.

        -type: Indicates what type number is. 0:ISBN, 1:OCN


        Returns:
        A list of metadata will be returned in the following format:
        [isbn, ocn, [lccns]]

        -isbn: String of ISBN.

        -ocns: String of OCN.

        -lccn_list: list of all lccn along with the source.

        Note: If no values are found for ISBN or OCN, "null" will be used.

        """
        try:
            self.open_connection()
            cursor = self.connection.cursor()

            # if number is an ISBN
            if type == 0:
                ocn = cursor.execute("SELECT ocn FROM metadata WHERE isbn=?", (number,)).fetchone()
                ocn = ocn[0] if ocn else "null"

                llist = cursor.execute("SELECT lccn, lccn_source FROM metadata WHERE isbn=?", (number,)).fetchall()
                lccn_list = [(row[0], row[1]) for row in llist]

                return [number, ocn, lccn_list]

            if type == 1:
                isbn = cursor.execute("SELECT isbn FROM metadata WHERE ocn=?", (number,)).fetchone()
                if isbn is None:
                    isbn = "null"

                llist = cursor.execute("SELECT lccn, lccn_source FROM metadata WHERE ocn=?", (number,)).fetchall()
                lccn_list = [(row[0], row[1]) for row in llist]
                return [isbn, number, lccn_list]

            else:
                return []

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
