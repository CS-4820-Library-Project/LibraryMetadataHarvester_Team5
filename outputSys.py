import sqlite3

class LMHDataOutputSystem:
    def __init__(self, database_name='LMH_database.db'):
        # Initialize the LMHDataOutputSystem
        self.database_name = database_name
        self.conn = sqlite3.connect(database_name)
        self.cursor = self.conn.cursor()

    def retrieve_metadata(self, number, number_type):
        # Check if the given ISBN or OCN is in the database
        if self.is_in_database(number, number_type):
            # Query to retrieve metadata from the database
            query = f"SELECT ISBN, OCN, LCCN, LCCN_SOURCE, DOI FROM lmh_data WHERE {number_type} = ?"
            self.cursor.execute(query, (number,))
            result = self.cursor.fetchone()

            if result:
                # Extract metadata from the result
                isbn_list, ocn, lccn, lccn_source, doi = result
                return [isbn_list.split(','), ocn, lccn, lccn_source, doi]
        return []

    def is_in_database(self, number, number_type):
        # Check if the given ISBN or OCN is present in the database
        query = f"SELECT COUNT(*) FROM lmh_data WHERE {number_type} = ?"
        self.cursor.execute(query, (number,))
        count = self.cursor.fetchone()[0]
        return count > 0

    def reset_database(self):
        # Reset the entire database
        query = "DELETE FROM lmh_data"
        self.cursor.execute(query)
        self.conn.commit()

    def display_database(self):
        # Display the contents of the database (for testing)
        query = "SELECT * FROM lmh_data"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()

        for row in rows:
            print(row)

    def close_connection(self):
        # Close the database connection
        self.conn.close()


# Example usage
lmh_output_system = LMHDataOutputSystem()

# Retrieve metadata example
metadata = lmh_output_system.retrieve_metadata("1234", 0)
print("Retrieve Metadata:", metadata)

# Display the database (for testing)
print("\nDatabase Contents:")
lmh_output_system.display_database()

# Reset the database (for testing)
lmh_output_system.reset_database()
print("\nAfter Reset:")
lmh_output_system.display_database()

# Close the database connection
lmh_output_system.close_connection()
