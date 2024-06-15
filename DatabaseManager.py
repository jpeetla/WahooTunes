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
                
    def clear_venue_table(self):
        self.check_connection()

        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM Venue;")
            self.connection.commit()
            print("Venue table cleared successfully.")
        except sqlite3.Error as e:
            print("Failed to clear Venue table:", e)
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
                
    def insert_venue_data(self):
        self.check_connection()

        insert_venues_sql = """
        INSERT INTO Venue (VenueName, VenueStreet, VenueCity, VenueState, VenueZipCode, VenueWebsite, ContactFirstName, ContactLastName, PhoneNumber) VALUES 
        ('JPJ', '295 Massie Rd', 'Charlottesville', 'VA', '22903', 'jpj.com', 'Johnny', 'Doe', '1234560000'),
        ('UVA Amp', '151 Amphitheater Way', 'Charlottesville', 'VA', '22903', 'jpj.com', 'Johnny', 'Doe', '1234560000'),
        ('The Lawn', '400 Emmet St S', 'Charlottesville', 'VA', '22903', 'jpj.com', 'Johnny', 'Doe', '1234560000'),
        ('The Corner', '1501 University Ave', 'Charlottesville', 'VA', '22903', 'jpj.com', 'Johnny', 'Doe', '1234560000');
        
        """

        venue_ids = []

        try:
            cursor = self.connection.cursor()
            cursor.executescript(insert_venues_sql)
            self.connection.commit()
            
            # Retrieve the inserted venue IDs
            cursor.execute("SELECT VenueID FROM Venue;")
            venue_ids = [row[0] for row in cursor.fetchall()]

            print("Venue data inserted successfully.")
        except sqlite3.Error as e:
            print("Failed to insert Venue data:", e)
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()

        return venue_ids

    def clear_event_venue_data(self):
        self.check_connection()

        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM EventVenue;")
            self.connection.commit()
            print("EventVenue table cleared successfully.")
        except sqlite3.Error as e:
            print("Failed to clear EventVenue table:", e)
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()

    def clear_event_data(self):
        self.check_connection()

        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM Event;")
            self.connection.commit()
            print("Event table cleared successfully.")
        except sqlite3.Error as e:
            print("Failed to clear Event table:", e)
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()

    def insert_event_data(self, venue_ids):
        self.check_connection()

        insert_events_sql = """
        INSERT INTO Event (Name, Date, ContactFirstName, ContactLastName, CPPhoneNumber) VALUES 
        ('Rap Concert featuring Drake', '2025-02-01', 'John', 'Doe', '1234567890'),
        ('Pop Concert featuring Beyonce', '2025-02-02', 'Jane', 'Doe', '0987654321'),
        ('Jazz Concert featuring Louis Armstrong', '2025-02-03', 'John', 'Doe', '1234567890'),
        ('Classical Concert featuring Mozart', '2025-02-04', 'Jane', 'Doe', '0987654321');
        """

        try:
            cursor = self.connection.cursor()
            cursor.executescript(insert_events_sql)
            self.connection.commit()
            print("Event data inserted successfully.")
            
            # Retrieve the inserted event IDs
            cursor.execute("SELECT EventID FROM Event;")
            event_ids = [row[0] for row in cursor.fetchall()]

            # Insert into EventVenue table
            if len(venue_ids) == len(event_ids):
                for i in range(len(venue_ids)):
                    cursor.execute("INSERT INTO EventVenue (VenueID, EventID) VALUES (?, ?);", (venue_ids[i], event_ids[i]))
                self.connection.commit()
                print("EventVenue data inserted successfully.")
            else:
                print("Mismatch between venue and event counts. Data not inserted into EventVenue.")
            
        except sqlite3.Error as e:
            print("Failed to insert Event data:", e)
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
                

    def clear_event_attendees(self):
            self.check_connection()

            try:
                cursor = self.connection.cursor()
                cursor.execute("DELETE FROM EventAttendee;")
                self.connection.commit()
                print("EventAttendee table cleared successfully.")
                return True

            except sqlite3.Error as e:
                print("Failed to clear EventAttendee table:", e)
                self.connection.rollback()
                return False

            finally:
                if 'cursor' in locals() and cursor:
                    cursor.close()
                    

    def insert_event_attendees(self):
        self.check_connection()

        event_attendees = [
    ('2025-02-01', 'VIP', 1, 1),    # EventID 1, User ID 1 
    ('2025-02-01', 'General', 1, 2),# EventID 1, User ID 2 
    ('2025-02-01', 'General', 1, 3),# EventID 1, User ID 3 
    ('2025-02-01', 'General', 1, 4),# EventID 1, User ID 4 
    ('2025-02-01', 'General', 1, 5),# EventID 1, User ID 5 
    
    ('2025-02-02', 'VIP', 2, 1),    # EventID 2, User ID 1 
    ('2025-02-02', 'General', 2, 2),# EventID 2, User ID 2 
    ('2025-02-02', 'General', 2, 3),# EventID 2, User ID 3 
    ('2025-02-02', 'General', 2, 4),# EventID 2, User ID 4 
    ('2025-02-02', 'General', 2, 5),# EventID 2, User ID 5 
    
    ('2025-02-03', 'VIP', 3, 1),    # EventID 3, User ID 1 
    ('2025-02-03', 'General', 3, 2),# EventID 3, User ID 2 
    ('2025-02-03', 'General', 3, 3),# EventID 3, User ID 3 
    ('2025-02-03', 'General', 3, 4),# EventID 3, User ID 4 
    ('2025-02-03', 'General', 3, 5),# EventID 3, User ID 5 
    
    ('2025-02-04', 'VIP', 4, 1),    # EventID 4, User ID 1 
    ('2025-02-04', 'General', 4, 2),# EventID 4, User ID 2 
    ('2025-02-04', 'General', 4, 3),# EventID 4, User ID 3 
    ('2025-02-04', 'General', 4, 4),# EventID 4, User ID 4 
    ('2025-02-04', 'General', 4, 5),# EventID 4, User ID 5 
]

        try:
            cursor = self.connection.cursor()
            cursor.executemany('''
                INSERT INTO EventAttendee (RegistrationDate, TicketType, EventID, UserID)
                VALUES (?, ?, ?, ?)
            ''', event_attendees)

            self.connection.commit()
            print("EventAttendees inserted successfully.")
            return True

        except sqlite3.Error as e:
            print("Failed to insert EventAttendees:", e)
            self.connection.rollback()
            return False

        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()

                
if __name__ == "__main__":
    db_manager = DatabaseManager("music.sqlite3")
    db_manager.connect()
    db_manager.clear_event_attendees()
    db_manager.insert_event_attendees()

    db_manager.connection.close()