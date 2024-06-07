import sqlite3
import os

class DatabaseManager:
    def __init__(self, db_file):
        self.connection = None
        self.db_file = db_file

    def connect(self):
        if self.connection is not None:
            raise RuntimeError("Already connected to the database.")
        
        try:
            self.connection = sqlite3.connect(self.db_file)
            print("Connected to the database successfully.")
        except sqlite3.Error as e:
            print("Failed to connect to the database:", e)

    def check_connection(self):
        if self.connection is None:
            raise RuntimeError("Manager not connected")
        
    def create_tables(self):
        self.check_connection()
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        sql_file_path = os.path.join(script_dir, "sql/create_tables.txt")
        
        try:
            with open(sql_file_path, 'r') as file:
                sql_script = file.read()

            cursor = self.connection.cursor()
            cursor.executescript(sql_script)
            self.connection.commit()
            print("Tables created successfully.")
        except FileNotFoundError as e:
            print("Failed to find the SQL script file:", e)
        except sqlite3.Error as e:
            print("Failed to execute SQL script:", e)
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
        
    def delete_tables(self):
        self.check_connection()

        # List of tables to delete
        tables = ['Genre', 'Artist', 'Song', 'SongArtist', 'Rating', 'User', 'Venue',
                  'EventVenue', 'Event', 'EventAttendee']

        try:
            cursor = self.connection.cursor()
            for table in tables:
                cursor.execute(f"DROP TABLE IF EXISTS {table};")
            self.connection.commit()
            print("All tables deleted successfully.")
        except sqlite3.Error as e:
            print("Failed to delete tables:", e)
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
                
    def clear_tables(self):
        self.check_connection()

        # List of tables to clear
        tables = ['Genre', 'Artist', 'Song', 'SongArtist', 'Rating', 'User', 'Venue',
                  'EventVenue', 'Event', 'EventAttendee']

        try:
            cursor = self.connection.cursor()
            for table in tables:
                cursor.execute(f"DELETE FROM {table};")
            self.connection.commit()
            print("All tables cleared successfully.")
        except sqlite3.Error as e:
            print("Failed to clear tables:", e)
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()

    def insert_initial_data(self):
        self.check_connection()

        script_dir = os.path.dirname(os.path.abspath(__file__))
        sql_file_path = os.path.join(script_dir, "sql/initial_data.txt")

        try:
            with open(sql_file_path, 'r') as file:
                sql_script = file.read()

            cursor = self.connection.cursor()
            cursor.executescript(sql_script)
            self.connection.commit()
            print("Initial data inserted successfully.")
        except FileNotFoundError as e:
            print("Failed to find the SQL script file:", e)
        except sqlite3.Error as e:
            print("Failed to execute SQL script:", e)
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()

if __name__ == "__main__":
    db_manager = DatabaseManager("music.sqlite3")
    db_manager.connect()
    db_manager.delete_tables()
    db_manager.create_tables()
    db_manager.insert_initial_data()