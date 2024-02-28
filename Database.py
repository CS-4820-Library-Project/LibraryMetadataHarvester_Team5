import sqlite3


def create_database(name):
    # Connect to the database (it will be created if it doesn't exist)
    conn = sqlite3.connect(name)

    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()

    # Create the table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lmh_data (
            OCN TEXT PRIMARY KEY,
            ISBN TEXT,
            LCCN TEXT,
            LCCN_SOURCE TEXT,
            DOI TEXT
        )
    ''')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()


# Example usage
create_database('LMH_database.db')
