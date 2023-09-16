from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, flash
import os
from datetime import datetime
import mimetypes
from mydatabase import MyDB
import bcrypt
import qrcode
from time import time


app = Flask(__name__)
app.secret_key = 'nitish_sumita'  # Set your own secret key

db = MyDB()

# Database connection details (you can modify as needed)
DB_NAME = "printpro.db"

def get_base_url():
    return request.url_root

def get_timestamp(filename):
    # Extract the timestamp from the filename
    timestamp = filename.split('__')[-1].split('.')[0]
    # print(f"Time Stamp: {timestamp}")
    # return datetime.strptime(timestamp, r'%Y%m%d%H%M%S')
    db.connect()
    time_stamp = db.get_timestamp_by_file_name(filename)
    db.close()
    return time_stamp


def hash_password(password):
    # Generate a salt and hash the password using bcrypt
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')
 

def verify_password(password, hashed_password, salt):
    # Check if the given password matches the hashed password
    return bcrypt.checkpw(password.encode('utf-8'), (salt + hashed_password).encode('utf-8'))

# TODO: Modify this function to verify user
# def verify_user_password(user_info, password):
#     print(f"In the Function check the output of the user: {user_info}, Password: {password}")
#     if user_info:
#         # Fetch the hashed password and salt from the database
#         hashed_password = user_info['password_hash']
#         salt = hashed_password[:29]  # Extract the first 29 characters as the salt

#         # Verify the entered password against the stored hashed password
#         if verify_password(password, hashed_password, salt):
#             print("Passwords match, user is authenticated")
#             return True

#     # Passwords don't match, user is not authenticated
#     return False

def verify_user_password(user_info, password):
    # print(f"=====Debug-1======  {user_info['password_hash']}, {password}")
    if user_info["password_hash"] == password:
        # Authenticate the User
        return True
    
    # Deauthenticate the user
    return False


def generate_qr_code(user_name, unique_url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    # print("++", unique_url)
    qr.add_data(unique_url)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_path = f"static/qrcodes/{user_name}_qr.png"
    qr_img.save(qr_path)
    return qr_path


@app.route('/register', methods=['GET', 'POST'])
def register_user():
    error_message = None

    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        mobile_number = request.form['mobile_number']
        password = request.form['password']
        role = request.form['role']
        # hashed_password = hash_password(password)
        hashed_password = password

        # Insert the user into the database
        db = MyDB(DB_NAME)
        db.connect()
        if db.insert_user(username, mobile_number, hashed_password, role):
            qr_path = generate_qr_code(mobile_number, f"{get_base_url()}upload/{mobile_number}")
            db.insert_qr_code_location(mobile_number, qr_path)
            return redirect(url_for('login'))  # Redirect to the login page after successful registration
        else:
            error_message = 'Mobile number is already registered.'
        db.close()

    return render_template('register.html', error_message=error_message)


@app.route("/home", methods=['POST', 'GET'])
def index():
    return render_template("index.html")


@app.route('/', methods=['GET', 'POST'])
def home_index():
    print(get_base_url())
    if request.method == 'POST':
        # check if the post request has the file part
        if 'files' not in request.files:
            return render_template('upload.html', message='No file part')

        files = request.files.getlist('files')

        # process and save the files (e.g., store them on the server)
        for file in files:
            if file.filename == '':
                continue  # skip empty file inputs

            # generate a timestamp string
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

            # extract the file extension
            file_extension = os.path.splitext(file.filename)[1]

            # generate the new file name with timestamp
            new_filename = f"{file.filename.split('.')[0]}__{timestamp}{file_extension}"

            # save the file to the server with the new filename
            file.save(os.path.join('uploads', new_filename))

            # store the file information or perform any additional processing
            # ...

        return render_template('upload.html', message='Files uploaded successfully')

    return render_template('index.html')
    # return redirect(url_for("login"))


# username == mobile_number
@app.route('/upload/<username>', methods=['GET', 'POST'])
def upload_file(username):
    error_message = None

    if request.method == 'POST':
        files = request.files.getlist('files')
        if not files:
            return redirect(request.url)

        for file in files:
            if file.filename == '':
                return redirect(request.url)

            if file:
                # Save the uploaded file in the 'uploads' folder
                # Get the current timestamp
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                file.filename = f"{str(time()).replace('.', '_')}__{file.filename}"

                file_path = os.path.join("uploads", file.filename)
                file.save(file_path)

                file_type, _ = mimetypes.guess_type(file.filename)

                if file_type is None:
                    file_type = "Unrecognized"

                # Insert the record into the database table
                db.connect()
                if not db.insert_uploaded_file(username, file.filename, file_path, timestamp, file_type):
                    error_message = 'An unknown error occurred while uploading the file.'
                db.close()

        session["current_user"] = username
        if error_message is not None:
            return render_template('upload.html', username=username, error_message=error_message)
        else:
            # return redirect(url_for('admin'))  # Redirect to the admin page after successful upload
            error_message = "successful uploaded"
            return render_template('upload.html', username=username, error_message=error_message)

    return render_template('upload.html', username=username, error_message=error_message)


@app.route('/admin_upload/<username>', methods=['GET', 'POST'])
def admin_upload_file(username):
    error_message = None

    if request.method == 'POST':
        files = request.files.getlist('files')
        if not files:
            return redirect(request.url)

        for file in files:
            if file.filename == '':
                return redirect(request.url)

            if file:
                # Save the uploaded file in the 'uploads' folder
                # Get the current timestamp
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                file.filename = f"{str(time()).replace('.', '_')}__{file.filename}"

                file_path = os.path.join("uploads", file.filename)
                file.save(file_path)

                file_type, _ = mimetypes.guess_type(file.filename)

                if file_type is None:
                    file_type = "Unrecognized"

                # Insert the record into the database table
                db.connect()
                if not db.insert_uploaded_file(username, file.filename, file_path, timestamp, file_type):
                    error_message = 'An unknown error occurred while uploading the file.'
                db.close()

        session["current_user"] = username
        if error_message is not None:
            return render_template('admin_upload.html', username=username, error_message=error_message)
        else:
            # return redirect(url_for('admin'))  # Redirect to the admin page after successful upload
            error_message = "successful uploaded"
            return redirect(url_for('admin'))
            # return render_template('upload.html', username=username, error_message=error_message)

    return render_template('admin_upload.html', username=username, error_message=error_message)


# username == mobile_number
@app.route('/upload_by_id', methods=['GET', 'POST'])
def upload_file_by_id():
    error_message = None
    username = ""
    if request.method == 'POST':
        files = request.files.getlist('files')
        username = request.form["mobile"]
        if not files:
            return redirect(request.url)

        for file in files:
            if file.filename == '':
                return redirect(request.url)

            if file:
                # Save the uploaded file in the 'uploads' folder
                # Get the current timestamp
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                file.filename = f"{str(time()).replace('.', '_')}__{file.filename}"

                file_path = os.path.join("uploads", file.filename)
                file.save(file_path)

                file_type, _ = mimetypes.guess_type(file.filename)

                if file_type is None:
                    file_type = "Unrecognized"

                # Insert the record into the database table
                db.connect()
                if not db.insert_uploaded_file(username, file.filename, file_path, timestamp, file_type):
                    error_message = 'An unknown error occurred while uploading the file.'
                db.close()

        session["current_user"] = username
        if error_message is not None:
            return render_template('upload_by_id.html', username=username, error_message=error_message)
        else:
            # return redirect(url_for('admin'))  # Redirect to the admin page after successful upload
            error_message = "successful uploaded"
            # return render_template('upload.html', username=username, error_message=error_message)
            return redirect(url_for('home_index'))

    return render_template('upload_by_id.html', username=username, error_message=error_message)


@app.route('/unauthorized', methods=['GET'])
def unauthorized():
    return render_template('unauthorized.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        mobile_number = request.form.get('mobile_number')
        password = request.form.get('password')

        # Get user information from the database based on the mobile number
        db.connect()
        # print(f"Got mobile Numebr: {mobile_number}")
        user_info = db.get_user_by_mobile_number(mobile_number)
        db.close()
        if user_info and verify_user_password(user_info, password):
            # Set a session variable to indicate that the user is logged in
            session['logged_in'] = True
            session['user_id'] = user_info['user_id']
            session['username'] = user_info['mobile_number']
            session["current_user"] = mobile_number

            # Redirect to the dashboard or profile page after successful login
            return redirect(url_for('admin'))  # Change 'dashboard' to your desired endpoint

        # Redirect back to the login page with an error message
        # return redirect(url_for('login', error_message='Invalid credentials'))
        # return redirect(url_for('login'))
        return render_template('login.html', error_message="Invalid credentials")

    return render_template('login.html', error_message="")
    

@app.route('/admin', methods=['GET'])
def admin():
    # Check if the current user is authenticated as an admin
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    # Get the list of uploaded files
    files = db.get_files_by_username(session['username'])

    # Prepare the file information with timestamps
    file_info = []
    for filename in files:
        # timestamp = filename["files"]
        # file_type, _ = filename["files"]
        file_info.append((filename["file_name"], filename["timestamp"], filename["file_type"]))

    # Sort the files based on the timestamp in descending order
    file_info.sort(key=lambda x: x[1], reverse=True)
    db.connect()
    admin_qr_file = db.get_qr_code_location_by_user_name(session['username'])
    db.close()
    return render_template('admin.html', file_info=file_info, admin_qrcode=admin_qr_file, current_user=session["current_user"])


@app.route('/download_file/<filename>', methods=['GET'])
def download_file(filename):
    # Check if the user is logged in and authorized as an admin
    if not session.get('logged_in'):
        flash('You are not authorized to access this page.', 'error')
        return redirect(url_for('unauthorized'))

    # Serve the file for download if it exists in the 'uploads' directory
    file_path = os.path.join("uploads", filename)
    if os.path.isfile(file_path):
        return send_from_directory('uploads', filename)
    else:
        flash('File not found.', 'error')
        return redirect(url_for('admin'))


@app.route('/delete_file/<filename>', methods=['GET'])
def delete_file(filename):
    # Check if the current user is authenticated and authorized as an admin
    # Implement your authentication and authorization logic here
    if not session.get('logged_in'):
        return render_template('unauthorized.html')

    # Delete the file from the server
    file_path = os.path.join('uploads', filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        db.delete_file_entry(filename)
        message = f'{filename} has been deleted.'
    else:
        message = f'{filename} not found.'

    return redirect(url_for('admin'))
    # return render_template('admin.html', files=files, message=message)


@app.route('/download_qr_code/<username>', methods=['GET'])
def download_qr_code(username):
    # Add code to generate and return the QR code image for the given username
    # qr_code_image_path = generate_qr_code(username, unique_url)
    print(f"UserName: {username}")
    db.connect()
    qr_code_image_path = db.get_qr_code_location_by_user_name(username)
    db.close()
    print(f"QR Path is: {qr_code_image_path}")
    return send_from_directory('static/qrcodes', qr_code_image_path.split("/")[-1])


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")

