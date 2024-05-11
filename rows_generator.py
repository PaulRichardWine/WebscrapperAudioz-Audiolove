import sqlite3

def rows_generator(db_path , table_name):
    # Connect to the SQLite database at the provided path
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Set the row factory to sqlite3.Row
    cursor = conn.cursor()

    # Query to select all rows from the 'middle' table
    select_url_query = f"SELECT * FROM {table_name}"
    cursor.execute(select_url_query)

    rows = cursor.fetchall()

    for row in rows:
        yield row  # Access by column names

    # Close the cursor and connection to clean up resources
    cursor.close()
    conn.close()