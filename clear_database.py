import sqlite3
import qrcode


def clear_all_tables(database_file):
    try:
        conn = sqlite3.connect(database_file)
        cursor = conn.cursor()

        # List all table names in the database
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        # Truncate or delete all rows from each table
        for table in tables:
            table_name = table[0]
            if table_name != 'sqlite_sequence':  # Skip the sqlite_sequence table
                # You can choose to truncate or delete rows based on your requirements
                # Use TRUNCATE if you want to keep the table structure, or DELETE if you want to remove all rows
                # Replace TABLE_NAME with the actual table name in the SQL statement
                cursor.execute(f"DELETE FROM {table_name};")

        # Commit the changes and close the connection
        conn.commit()
        conn.close()
        return True

    except Exception as e:
        print(f"Error: {e}")
        return False


def generate_qr_code(user_name, unique_url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    print("++", unique_url)
    qr.add_data(unique_url)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_path = f"static/qrcodes/{user_name}_qr.png"
    qr_img.save(qr_path)
    return qr_path

# generate_qr_code("7631256855", "http://192.168.1.5:5000/upload/7631256855")
clear_all_tables("printpro.db")