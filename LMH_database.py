import sqlite3

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
                            lccn_source TEXT,
                            doi TEXT)''')
            self.connection.commit()

        except sqlite3.Error as e:
            print(f"Error: {e}")

        finally:
            self.close_connection()

    def db_insert(self, isbn, ocn, lccn, lccn_source, doi):
        """
        Function that inserts metadata into the database.
        For every isbn given, a new record is inserted into
        the database with the parameters given.
        
        If no isbn is given, a record will be created with the 
        value "null" given to isbn.

        Parameters:
        - isbn: List of strings representing ISBNs. List is used
                even when one isbn is provided. Empty list is used
                when no ISBNs are provided.
        - ocn: String representing an OCN number. "null" if none
                is provided.

        - lccn: String representing the LCCN number. "null" if none
                is provided.

        - lccn_source: String representing the LCCN source. "null"
                if none is provided

        -doi: String representing the DOI number. "null" if none
                is provided.


        """
        try:
            self.open_connection()
            cursor = self.connection.cursor()

            # If al least 1 ISBN is provided, insert row into database for every ISBN if it is not in the database
            if len(isbn) > 0:
                for i in isbn:
                    x = cursor.execute("SELECT * FROM metadata WHERE isbn=? AND ocn=? AND lccn=? AND lccn_source=? AND doi=?",
                                   (i, ocn, lccn, lccn_source, doi)).fetchall()
                    if len(x) == 0:
                        cursor.execute("INSERT INTO metadata (isbn, ocn, lccn, lccn_source, doi) VALUES (?, ?, ?, ?, ?)",
                                       (i, ocn, lccn, lccn_source, doi))

            # If no ISBN is provided, insert row into database with null value for isbn
            if len(isbn) == 0:
                cursor.execute("INSERT INTO metadata (isbn, ocn, lccn, lccn_source, doi) VALUES (?,?,?,?,?)",
                               ("null", ocn, lccn, lccn_source, doi))

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

    def get_metadata(self, number, isbn_or_ocn):
        """
        Function that returns the associated metadata for a given
        ISBN or OCN.

        Parameters:
        - number: String representing the ISBN or OCN number.
        - isbn_or_ocn: String "OCN" if the number is an OCN
                       or "ISBN" if the number is an ISBN.

        Returns:
        - A list of data will be returned in the format:
            [[isbns], ocn, lccn, lccn_source, doi]

            The value "null" will be used if there are no
            associated values for any of the metadata
            
        """

        # Check if the number provided is in the database:
        if self.is_in_database(number, isbn_or_ocn):
            try:
                self.open_connection()
                cursor = self.connection.cursor()

                # If the number is an ISBN search the database for it and return metadata in a list
                if isbn_or_ocn == 'ISBN':
                    cursor.execute("SELECT * FROM metadata WHERE isbn=(?);", (number,))
                    data = cursor.fetchone()
                    return [data[0], data[1], data[2], data[3], data[4]]

                # If the number is an OCN, search for metadata
                if isbn_or_ocn == 'OCN':
                    cursor.execute("SELECT isbn FROM metadata WHERE ocn=(?);", (number,))
                    data = cursor.fetchall()
                    # Put all ISBNs associated with the OCN inside a list
                    isbn_list = [i[0] for i in data]
                    cursor.execute("SELECT * FROM metadata WHERE ocn=(?);", (number,))
                    data2 = cursor.fetchone()
                    # Return a list of metadata
                    return [isbn_list, data2[1], data2[2], data2[3], data2[4]]

            except sqlite3.Error as e:
                print("Error", e)

            finally:
                self.close_connection()

        # If the number provided is not in the database, return an empty list
        else:
            return []

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

    def update_db(self, number, isbn_or_ocn, other_numbers, lccn, lccn_source, doi):
        """
        Function for updating data in the database.
        User may not always want all metadata so some will be left as "null"
        These "null" values will be updated if values are given in the parameters.

        Parameters:
        - number: String representing an ISBN or OCN.

        - isbn_or_ocn: String "OCN" if number is an OCN, "ISBN" if number is an ISBN.

        - other_numbers: Either an ISBN or OCN. The one that is not given in the parameter
                         number. If number is an OCN other_numbers will be a list of ISBN strings.
                         If number is an ISBN, then other_numbers will be a OCN string.

        - lccn: String representing LCCN. "null" if no value is to be updated.

        - lccn_source: String representing LCCN source. "null" if no value is to be updated.

        - doi: String representing DOI. "null" if no value is to be updated.


        """
        try:
            self.open_connection()
            cursor = self.connection.cursor()

            # Look up the number (ISBN or OCN) in the database
            if isbn_or_ocn == "ISBN":
                cursor.execute("SELECT * FROM metadata WHERE isbn=?", (number,))
            elif isbn_or_ocn == "OCN":
                cursor.execute("SELECT * FROM metadata WHERE ocn=?", (number,))
            else:
                raise ValueError("Invalid value for isbn_or_ocn. Use 'ISBN' or 'OCN'.")

            existing_data = cursor.fetchone()

            # If the number is not found, handle the creation of new rows
            if not existing_data:
                raise ValueError(f"No data found for {isbn_or_ocn} {number}.")

            # Update other number (OCN) if provided
            if isbn_or_ocn == "OCN" and number != "null":
                # Update ISBN if it's "null"
                if existing_data[0] == "null" and other_numbers:
                    cursor.execute("UPDATE metadata SET isbn=? WHERE ocn=?", (other_numbers[0], number))

                    # Create new records for additional ISBNs
                    for new_isbn in other_numbers[1:]:
                        cursor.execute("INSERT INTO metadata (isbn, ocn, lccn, lccn_source, doi) VALUES (?, ?, ?, ?, ?)",
                                    (new_isbn, number, existing_data[2], existing_data[3], existing_data[4]))

                # Update metadata values if they are "null"
                if existing_data[2] == "null" and lccn != "null":
                    cursor.execute("UPDATE metadata SET lccn=? WHERE ocn=?", (lccn, number))

                if existing_data[3] == "null" and lccn_source != "null":
                    cursor.execute("UPDATE metadata SET lccn_source=? WHERE ocn=?", (lccn_source, number))

                if existing_data[4] == "null" and doi != "null":
                    cursor.execute("UPDATE metadata SET doi=? WHERE ocn=?", (doi, number))

            # Update ISBN if provided
            if isbn_or_ocn == "ISBN" and number != "null":
                # Update other metadata values if they are "null"
                if existing_data[1] == "null" and other_numbers != "null":
                    cursor.execute("UPDATE metadata SET ocn=? WHERE isbn=?", (other_numbers, number))

                if existing_data[2] == "null" and lccn != "null":
                    cursor.execute("UPDATE metadata SET lccn=? WHERE isbn=?", (lccn, number))

                if existing_data[3] == "null" and lccn_source != "null":
                    cursor.execute("UPDATE metadata SET lccn_source=? WHERE isbn=?", (lccn_source, number))

                if existing_data[4] == "null" and doi != "null":
                    cursor.execute("UPDATE metadata SET doi=? WHERE isbn=?", (doi, number))

            self.connection.commit()

        except sqlite3.Error as e:
            print(f"Error: {e}")
            self.connection.rollback()

        finally:
            self.close_connection()


