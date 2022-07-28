from flask import Flask, render_template, request
import sqlite3
import csv
import os

app = Flask(__name__)

# get login details of a user by login name
def get_login_details(username):

    connection = sqlite3.connect("grade_distributor.db")
    cursor = connection.cursor()
    query = """SELECT password, role, name
                FROM login_details 
                WHERE login_name = ?;"""

    cursor.execute(query, (username, ))
    data = cursor.fetchone()
    connection.close()
    return data

# get all components of assessments
def get_components():
    connection = sqlite3.connect("grade_distributor.db")
    cursor = connection.cursor()
    query = "SELECT * FROM student_grades"
    header = cursor.execute(query)
    connection.close()
    
    data = [item[0] for item in header.description]
        
    return data[1:]
  
# get individual student grade for student view
def get_grades(username):

    connection = sqlite3.connect("grade_distributor.db")
    cursor = connection.cursor()
    components = get_components()
    components_str = ",".join(components)
    query = """SELECT """ + components_str + """ FROM student_grades 
            WHERE name = ?;"""

    cursor.execute(query, (username, ))
    data = cursor.fetchone()
    connection.close()
    return data


# get all student grades for teacher view
def get_all_grades():

    connection = sqlite3.connect("grade_distributor.db")
    cursor = connection.cursor()
    components = get_components()
    components_str = ",".join(components)
    query = """SELECT login_name, login_details.name,""" + components_str + """ FROM login_details,student_grades WHERE login_details.login_name = student_grades.name;"""

    cursor.execute(query)
    data = cursor.fetchall()
    connection.close()
    return data


def get_student_usernames():
    connection = sqlite3.connect("grade_distributor.db")
    cursor = connection.cursor()
    query = """SELECT login_name, role FROM login_details;"""
    cursor.execute(query)
    data = cursor.fetchall()
    connection.close()

    student_usernames = []

    for item in data:
        if item[1] == 'student': # check role
            student_usernames.append(item[0])

    return student_usernames


def get_username():

    connection = sqlite3.connect("grade_distributor.db")
    cursor = connection.cursor()
    query = """SELECT login_name FROM login_details;"""
    cursor.execute(query)
    data = cursor.fetchall()
    connection.close()

    usernames = []
    for item in data:
        usernames.append(item[0])

    return usernames

# check username against database
def is_valid_username(username):

    return username in get_username()


@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template('index.html')
    #post
    username = request.form.get("user")
    password = request.form.get("pw")


    if not is_valid_username(username):
        return render_template('index.html', message="Invalid username!")

    # get_login_details returns password and role in a tuple
    login_details = get_login_details(username)

    if password == login_details[0]:
        if login_details[1] == 'student':
            return render_template('student_view.html',
                                   student_name=login_details[2],
                                   grades=get_grades(username),
                                   components=get_components())
        else:
            return render_template('teacher_view.html',
                                   student_grades=get_all_grades(),
                                   usernames=get_student_usernames(),
                                   headers=get_header(),
                                   components=get_components())
    else:
        return render_template('index.html', message="Wrong password!")

# get components minus total
def get_header():
    connection = sqlite3.connect("grade_distributor.db")
    cursor = connection.cursor()
    query = "SELECT * FROM student_grades"
    header = cursor.execute(query)
    connection.close()
    
    data = [item[0] for item in header.description]
        
    return data[1:-1]

def edit_marks(username, task, new_marks):
    connection = sqlite3.connect("grade_distributor.db")
    cursor = connection.cursor()
    query = "UPDATE student_grades SET " + task + "= ? WHERE name = ?;"
    cursor.execute(query, (new_marks, username))
    connection.commit()

    header = get_header()
    concatenate_header = ""
    for item in header:
      concatenate_header += item + "+"

    concatenate_header = concatenate_header[:-1] # remove the last "+"
    query = "SELECT SUM(" + concatenate_header + ") FROM student_grades WHERE name = ?"
    cursor.execute(query, (username,))
    data = cursor.fetchone()

    query = "UPDATE student_grades SET Total= ? WHERE name = ?;"
    cursor.execute(query, (data[0], username))
    connection.commit()
  
    connection.close()


# Method for edit marks
@app.route("/editmarks", methods=["POST"])
def editmarks():
    # get new marks from student to update DB
    student_id = request.form.get("usernames")
    task = request.form.get("qn_num")
    marks = request.form.get("new_marks")

    edit_marks(student_id, task, marks)
    return render_template('teacher_view.html',
                           student_grades=get_all_grades(),
                           usernames=get_student_usernames(),
                           message="Successfully updated!", headers=get_header())

# drop student_grades table
def reset_student_grades():
	connection = sqlite3.connect("grade_distributor.db")
	connection.execute("DROP TABLE IF EXISTS student_grades")
	connection.close()

def read_file(filename):
    
    with open(filename, 'r') as f:
        data = list(csv.reader(f))

    return data

# create login_details and student_grades tables
def create_tables(headers):
    connection = sqlite3.connect("grade_distributor.db")
    cursor = connection.cursor()
    query = """CREATE TABLE IF NOT EXISTS login_details (  
            login_name TEXT PRIMARY KEY, 
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            role TEXT NOT NULL
            ); """
    cursor.execute(query)
    
    query = """CREATE TABLE IF NOT EXISTS student_grades (  
            name TEXT PRIMARY KEY,"""
    for header in headers:
        query += header + " INTEGER NOT NULL,"
    query = query[:-1]
    query += ");"

    cursor.execute(query)
    
    connection.commit()
    connection.close()

# insert student_grades data and maybe login_details (comment out)
def insert_data(student_grades):
    connection = sqlite3.connect("grade_distributor.db")
    cursor = connection.cursor()
##    for data in login_details[1:]:
##        query = "INSERT INTO login_details (login_name,password,name,role) VALUES (?,?,?,?);"
##        cursor.execute(query,(data[0],data[1],data[2],data[3]))
##        connection.commit()
        
    for data in student_grades[1:]:
        query = 'INSERT INTO student_grades VALUES ('
        query += "?," * len(data)
        query = query[:-1]
        query +=""");"""
        
        cursor.execute(query,(data))
        connection.commit()
    connection.close()


# upload csv to create database
@app.route("/createdb", methods=["GET", "POST"])
def createdb():
    if request.method == "GET":
        return render_template('createdb.html')

    data_file = request.files['filename']
    path = os.path.join(os.getcwd(), data_file.filename)
    data_file.save(path)
    student_grades = read_file(data_file.filename)
    headers = student_grades[0][1:]
    create_tables(headers)
    insert_data(student_grades)
    return render_template('createdb.html', message="Successful upload!")



app.run(host='0.0.0.0', port=81)
