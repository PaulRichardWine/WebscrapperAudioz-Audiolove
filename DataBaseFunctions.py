import sqlite3
import datetime
import time
import shutil
import os

import alfalink
import audiolove_main
import audioz_main
import audioz_peeplink
import hosting
from hosting import check_hosting_availability

def timestamp():
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


def backup_database(db_filename):
    def safe_timestamp():
        now = datetime.datetime.now()
        return now.strftime("%Y-%m-%d_%H-%M-%S")
    backup_folder = 'backup'
    os.makedirs(backup_folder, exist_ok=True)
    date_stamp = safe_timestamp()
    backup_filename = f"{backup_folder}/{date_stamp} kopia zapasowa {db_filename}"
    shutil.copyfile(db_filename, backup_filename)
    return backup_filename


def create_empty_database(path):

    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    # Zdefiniuj zapytania SQL do utworzenia tabel

    create_kategoria_table = """
        CREATE TABLE IF NOT EXISTS kategoria (
            nazwa TEXT PRIMARY KEY
        )
       """

    create_main_table = """
        CREATE TABLE IF NOT EXISTS main (
            id INTEGER PRIMARY KEY,
            kategoria_nazwa TEXT,
            url TEXT NOT NULL UNIQUE,
            import_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'new',
            last_checked TIMESTAMP,
            FOREIGN KEY(kategoria_nazwa) REFERENCES kategoria(nazwa)
        )
    """

    create_middle_table = """
    CREATE TABLE IF NOT EXISTS middle (
        id INTEGER PRIMARY KEY,
        main_id INTEGER NOT NULL,
        url TEXT NOT NULL UNIQUE,
        password TEXT,
        import_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'new',
        last_checked TIMESTAMP,
        FOREIGN KEY(main_id) REFERENCES main(id)
    )
    """

    create_hosting_table = """
    CREATE TABLE IF NOT EXISTS hosting (
        id INTEGER PRIMARY KEY,
        middle_id INTEGER NOT NULL,
        url TEXT NOT NULL UNIQUE,
        import_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        active TEXT,
        last_checked TIMESTAMP,
        error_count INTEGER DEFAULT 0,
        FOREIGN KEY(middle_id) REFERENCES middle(id)
    )
    """

    # Wykonaj zapytania SQL
    cursor.execute(create_kategoria_table)
    cursor.execute(create_main_table)
    cursor.execute(create_middle_table)
    cursor.execute(create_hosting_table)

    # Zatwierdź zmiany i zamknij połączenie z bazą danych
    conn.commit()
    conn.close()

def insert_new_url(db_path, url):
    """
    Insert a new URL into the main table
    """
    # Open a connection to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # SQL query to insert a new row
    insert_query = """
    INSERT INTO main (url) VALUES (?)
    """

    # Attempt to insert the new URL
    try:
        cursor.execute(insert_query, (url,))  # You need to pass url as a tuple, i.e., (url,)
        conn.commit()
        print("URL successfully added.")
    except sqlite3.IntegrityError as e:
        print(f"Error: {e} - URL may already exist in the database.")
    finally:
        # Make sure the connection is closed even if an exception is raised
        conn.close()

def import_urls_from_csv (source_csv_path, target_sqlite_path):
    """
    zakładam, że struktura pliku csv jest taka jak w przesłanych plikach 'Automaty Paweł', czyli tylko jedna kolumna z urlami
    """

    import pandas as pd
    df = pd.read_csv(source_csv_path)
    for idx, row in df.iterrows():
        insert_new_url(target_sqlite_path,row[0])






def process_single_main_record(get_middle_url_function, db_path, main_id):
    """
    Process a single record from the main table using the main_id.
    Fetches the URL from the database and uses it to process the record.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Retrieve the URL from the main table using main_id
        select_url_query = "SELECT url FROM main WHERE id = ?"
        cursor.execute(select_url_query, (main_id,))
        url = cursor.fetchone()[0]
        print (url)

        result_dict = get_middle_url_function(url)
        print (result_dict)
        if result_dict:
            for key, val in result_dict.items():
                try:
                    insert_middle_query = """
                    INSERT INTO middle (main_id, url, password,  status, last_checked)
                    VALUES (?, ?, ?, 'new', NULL)
                    """
                    cursor.execute(insert_middle_query, (main_id, key, val))
                except sqlite3.IntegrityError:
                    print(f"Duplicate URL {dict['url']} not inserted.")

        # Update the main record to 'checked'
        update_main_query = """
        UPDATE main SET status = 'checked', last_checked = CURRENT_TIMESTAMP WHERE id = ?
        """
        cursor.execute(update_main_query, (main_id,))
        conn.commit()

    except Exception as e:
        print(f"Error processing ID {main_id}: {e}")

    finally:
        conn.close()

def iterate_through_main(get_middle_url_function, db_path, interval_in_seconds=3, checked_pass = True):
    """
    Iterate over the main table and process each record.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        if checked_pass:
            select_query = "SELECT id FROM main WHERE status != 'checked' ORDER BY id ASC"
        else:
            select_query = "SELECT id FROM main ORDER BY id ASC"
        cursor.execute(select_query)
        records = cursor.fetchall()

        for record in records:
            main_id = record[0]
            print ("id:", main_id)
            try:
                process_single_main_record (get_middle_url_function, db_path, main_id)
            except:
                print ("error zwrócony przez funkcję process_single_main_record")
            time.sleep(interval_in_seconds)

        print("Processed all records.")
    except Exception as e:
        print(f"Failed to process records: {e}")
    finally:
        conn.close()





def process_single_middle_record(get_hosting_url_function, db_path, middle_id):
    """
    Process a single record from the middle table using the middle_id.
    Fetches the URL from the database and uses it to process the record.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Retrieve the URL and password from the middle table using middle_id
        select_url_query = "SELECT url, password FROM middle WHERE id = ?"
        cursor.execute(select_url_query, (middle_id,))
        url, password = cursor.fetchone()
        print ("middle id:", middle_id)
        print ("url:", url)
        print("password", password)

        hosting_urls = get_hosting_url_function(url, password)
        if hosting_urls:
            for hosting_url in hosting_urls:
                try:
                    # Insert each new hosting URL into the hosting table with a new entry
                    insert_hosting_query = """
                    INSERT INTO hosting (middle_id, url)
                    VALUES (?, ?)
                    """
                    cursor.execute(insert_hosting_query, (middle_id, hosting_url))
                except sqlite3.IntegrityError:
                    print(f"Duplicate hosting URL {hosting_url} not inserted.")

        # Update the middle record to reflect that it has been checked
        update_middle_query = """
        UPDATE middle SET status = 'checked', last_checked = CURRENT_TIMESTAMP WHERE id = ?
        """
        cursor.execute(update_middle_query, (middle_id,))
        conn.commit()

    except Exception as e:
        print(f"Error processing middle ID {middle_id}: {e}")

    finally:
        conn.close()


def iterate_through_middle(get_url_function, db_path, interval_in_seconds=3, checked_pass=True):


    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        if checked_pass:
            select_query = f"SELECT id FROM middle WHERE status != 'checked' ORDER BY id ASC"
        else:
            select_query = f"SELECT id FROM middle ORDER BY id ASC"
        cursor.execute(select_query)
        records = cursor.fetchall()

        for record in records:
            record_id = record[0]
            print(f"id in middle:", record_id)
            try:
                process_single_middle_record(get_url_function, db_path, record_id)
            except Exception as e:
                print(f"Error returned by function: {e}")
            time.sleep(interval_in_seconds)

        print("Processed all records.")
    except Exception as e:
        print(f"Failed to process records for middle: {e}")
    finally:
        conn.close()



def process_single_hosting_record(db_path, hosting_id, check_hosting_availability = hosting.check_hosting_availability):
    """
    check_hosting_availability(url) - zwraca string "active", "deleted", albo podnosi error
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Retrieve the URL and password from the middle table using middle_id
        select_url_query = "SELECT url FROM hosting WHERE id = ?"
        cursor.execute(select_url_query, (hosting_id,))
        url_tuple = cursor.fetchone() #zwraca krotkę
        url = url_tuple[0]
        print ("hosting id:", hosting_id)
        print ("url:", url)

        try:
            active_or_deleted = check_hosting_availability(url)
            update_query = """
                        UPDATE hosting
                        SET active = ?,
                            last_checked = CURRENT_TIMESTAMP,
                            error_count = 0
                        WHERE id = ?
                    """

            # Update the 'active' and 'last_checked' fields in the database
            cursor.execute(update_query, (active_or_deleted, hosting_id))
            conn.commit()

        except Exception as e:
            print(f"Error podczas próby sprawdzenia linku:\n {e}")
            error_count_query = """
                UPDATE hosting 
                SET error_count = COALESCE(error_count, 0) + 1 
                WHERE id = ?
                """
            cursor.execute(error_count_query, (hosting_id,))
            conn.commit()

    except Exception as e:
        print(f"Error processing hosting ID {hosting_id}: {e}")

    finally:
        cursor.close()
        conn.close()


def iterate_through_hosting(db_path, interval_in_seconds):

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:

        select_query = f"SELECT id FROM hosting WHERE active != 'deleted' or active IS NULL ORDER BY last_checked IS NULL DESC, last_checked ASC, id ASC"

        cursor.execute(select_query)
        records = cursor.fetchall()

        for record in records:
            record_id = record[0]
            print(f"id in hosting:", record_id)
            try:
                process_single_hosting_record(db_path, record_id)
            except Exception as e:
                print(f"Error returned by function: {e}")
            time.sleep(interval_in_seconds)

        print("Processed all records.")
    except Exception as e:
        print(f"Failed to process records for hosting link: {e}")
    finally:
        conn.close()



class BaseClass:
    def __init__ (self, database_path):
        self.database_path = database_path

    def create_empty_database (self):
        create_empty_database(self.database_path)

    def import_urls_from_csv(self, source_csv_path):
        import_urls_from_csv(source_csv_path , self.database_path)

    def backup_database(self):
        backup_database (self.database_path)

    def process_single_hosting(self, hosting_id):
        process_single_hosting_record(self.database_path, hosting_id)

    def iterate_through_hosting(self, interval_in_seconds=3):
        iterate_through_hosting(self.database_path, interval_in_seconds=interval_in_seconds)


class Audioz (BaseClass):

    def process_single_main (self, main_id):
        process_single_main_record(audioz_main.main, self.database_path, main_id)

    def iterate_through_main(self, interval_in_seconds=3, checked_pass = True):
        iterate_through_main (audioz_main.main, self.database_path, interval_in_seconds=interval_in_seconds, checked_pass = checked_pass)

    def process_single_middle (self, middle_id):
        process_single_middle_record(audioz_peeplink.get_hosting_url, self.database_path, middle_id)

    def iterate_through_middle(self, interval_in_seconds=3, checked_pass = True):
        iterate_through_middle (audioz_peeplink.get_hosting_url, self.database_path, interval_in_seconds=interval_in_seconds, checked_pass = checked_pass)


class Audiolove(BaseClass):

    def process_single_main (self, main_id):
        process_single_main_record(audiolove_main.get_alfalink, self.database_path, main_id)

    def iterate_through_main(self, interval_in_seconds=3, checked_pass = True):
        iterate_through_main (audiolove_main.get_alfalink, self.database_path, interval_in_seconds=interval_in_seconds, checked_pass = checked_pass)

    def process_single_middle(self, middle_id):
        process_single_middle_record(alfalink.get_hosting_url, self.database_path, middle_id)

    def iterate_through_middle(self, interval_in_seconds=3, checked_pass=True):
        iterate_through_middle(alfalink.get_hosting_url, self.database_path,
                             interval_in_seconds=interval_in_seconds, checked_pass=checked_pass)


audioz = Audioz("audioz.sqlite")
audiolove = Audiolove("audiolove.sqlite")


# audioz.create_empty_database()
# audiolove.create_empty_database()

# audioz.import_urls_from_csv("Automaty Paweł - Audioz.csv")
# audiolove.import_urls_from_csv("Automaty Paweł - Audiolove.csv")
'''
poniższe funkcje są do używania przez użytkownika
kodu który jest wyżej nie trzeba zmieniać
aby uruchomić funkcję, zlikwiduj hashtag (#) i spację przed nią
'''

'''
pamiętaj o regularnych backupach
'''
# audioz.backup_database()
# audiolove.backup_database()


'''
Podstawowe sprawdzanie linkow z poszczególnych baz
(można odhaszować kilka opcji albo i wszystkie naraz, wtedy się wykona po kolei)
'''

# audioz.iterate_through_main()
# audiolove.iterate_through_main()

# audioz.iterate_through_middle()
# audiolove.iterate_through_middle()

# audioz.iterate_through_hosting()
# audiolove.iterate_through_hosting()



''' 
Ponowne sprawdanie linków już raz sprawdzonych 
"checked pass" oznacza że pomija te które już są checked czyli sprawdzone
przy parametrze checked_pass=False sprawdza je jeszcze raz, 
te linki które są już w bazie oczywiście nie sa wprowadzane ponownie
Nie dotyczy linków hostingowych, tam nie ma takiej opcji bo tam jest to inaczej zorganizowane: 
hostingowe domyślnie są sprawdzane wszystkie za każdym razem, zaczynając od nowych,
a później w kolejności od najdawniej sprawdzanego
'''

# audioz.iterate_through_main(checked_pass=False)
# audiolove.iterate_through_main(checked_pass=False)
# audioz.iterate_through_middle(checked_pass=False)
# audiolove.iterate_through_middle(checked_pass=False)
