import sqlite3

class MyDB:
    def __init__(self, db_name="printpro.db"):
        self.db_name = db_name

    def connect(self):
        self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        # Create User Table
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                mobile_number TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL
            )
        ''')

        # Create File Table
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS files (
                file_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                file_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                file_type TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')

        # Create Transaction Table
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                recharge_amount REAL NOT NULL,
                recharge_date TIMESTAMP NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')

        self.conn.commit()

    def close(self):
        self.conn.close()

    def execute_query(self, query, data=None):
        cursor = self.conn.cursor()
        if data:
            cursor.execute(query, data)
        else:
            cursor.execute(query)
        self.conn.commit()
        return cursor

    def fetch_one(self, query, data=None):
        cursor = self.execute_query(query, data)
        result = cursor.fetchone()
        cursor.close()
        return result

    def fetch_all(self, query, params=None):
        if not self.conn:
            raise Exception("Database connection not established. Call 'connect' method first.")
        cursor = self.conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.fetchall()

    def insert_user(self, username, mobile_number, password_hash, role):                                                                                  
        # Check if the mobile number is already registered
        if self.get_user_by_mobile_number(mobile_number):
            return False  # Return False if the mobile number is already registered

        query = '''
            INSERT INTO users (username, mobile_number, password_hash, role)
            VALUES (?, ?, ?, ?)
        '''
        data = (username, mobile_number, password_hash, role)
        self.execute_query(query, data)
        return True  # Return True after successful insertion

        data = (username, mobile_number, password_hash, role)
        self.execute_query(query, data)

    def get_user_by_mobile_number(self, mobile_number):
        query = 'SELECT * FROM users WHERE mobile_number = ?'
        user_row = self.fetch_one(query, (mobile_number,))

        if user_row:
            # Convert the row to a dictionary using column names as keys
            user_dict = {
                'user_id': user_row[0],
                'username': user_row[1],
                'mobile_number': user_row[2],
                'password_hash': user_row[3]
                # Add more keys as needed based on your table schema
            }
            return user_dict
        else:
            return None


    # Add other methods for file management and transactions as needed
    
    def get_file_names_by_mobile_number(self, mobile_number):
        query = '''
            SELECT file_name
            FROM files
            JOIN users ON users.user_id = files.user_id
            WHERE users.mobile_number = ?
        '''
        return [file_name[0] for file_name in self.fetch_all(query, (mobile_number,))]


    def get_password_by_user_id(self, user_id):
        self.connect()
        cursor = self.conn.cursor()

        # Execute a query to fetch the password for the given user_id
        cursor.execute("SELECT password_hash FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()

        self.close()

        if result:
            # Return the password_hash if the user_id exists in the database
            return result[0]
        else:
            # Return None if the user_id does not exist
            return None

    def create_qr_code_locations_table(self):
        self.connect()
        query = """
            CREATE TABLE IF NOT EXISTS qr_code_locations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT NOT NULL,
                qr_code_location TEXT NOT NULL
            )
        """
        self.conn.execute(query)
        self.close()

    def insert_qr_code_location(self, user_name, qr_code_location):
        query = "INSERT INTO qr_code_locations (user_name, qr_code_location) VALUES (?, ?)"
        data = (user_name, qr_code_location)
        self.execute_query(query, data)


    def get_qr_code_location_by_user_name(self, user_name):
        query = "SELECT qr_code_location FROM qr_code_locations WHERE user_name = ?"
        data = (user_name,)
        cursor = self.execute_query(query, data)
        return cursor.fetchone()[0] if cursor else None

    
    def get_shop_name_by_user_name(self, user_name):
        query = "SELECT username FROM users WHERE mobile_number = ?"
        data = (user_name,)
        cursor = self.execute_query(query, data)
        return cursor.fetchone()[0] if cursor else None


    
    def get_files_by_username(self, username):
        query = '''
            SELECT file_name, file_path, timestamp, file_type
            FROM files 
            JOIN users ON files.user_id = users.user_id 
            WHERE users.mobile_number = ?
        '''
        self.connect()
        result = self.fetch_all(query, (username,))
        # result will be a list of tuples, extract the elements of each tuple (file_name, file_path, timestamp, file_type)
        files = [{'file_name': file_tuple[0], 'file_path': file_tuple[1], 'timestamp': file_tuple[2], 'file_type': file_tuple[3]} for file_tuple in result]
        self.close()
        return files


    def insert_uploaded_file(self, username, file_name, file_path, timestamp, file_type):
        query = 'INSERT INTO files (user_id, file_name, file_path, timestamp, file_type) VALUES (?, ?, ?, ?, ?)'

        # Get the user_id associated with the given username
        user_id = self.get_user_id_by_username(username)
        print("----> ",username, user_id)
        if user_id is not None:
            try:
                self.execute_query(query, (user_id, file_name, file_path, timestamp, file_type))
                return True
            except Exception as e:
                print(f"Error inserting uploaded file: {e}")
        print("Returning False from The insert file upload")
        return False

    def get_user_id_by_username(self, username):
        query = 'SELECT user_id FROM users WHERE mobile_number = ?'
        result = self.fetch_one(query, (username,))
        if result:
            return result[0]  # Return the first element of the tuple (user_id)
        return None

    def get_timestamp_by_file_name(self, file_name):
        query = 'SELECT timestamp FROM files WHERE file_name = ?'
        result = self.fetch_one(query, (file_name,))

        if result:
            return result[0]  # Return the first element of the tuple (timestamp)
        return None
    
    def delete_file_entry(self, file_name):
        self.connect()
        if not self.conn:
            raise Exception("Database connection not established. Call 'connect' method first.")

        query = 'DELETE FROM files WHERE file_name = ?'
        cursor = self.conn.cursor()
        cursor.execute(query, (file_name,))
        self.conn.commit()
        self.close()

        return cursor.rowcount  # Return the number of rows deleted (0 or 1)


if __name__ == "__main__":
    db = MyDB("printpro.db")
    db.connect()
    db.close()
    db.create_qr_code_locations_table()
    # print(db.get_files_by_username('7631256855'))
    # db.close()