from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)


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


# get individual student grade
def get_grades(username):

    connection = sqlite3.connect("grade_distributor.db")
    cursor = connection.cursor()
    query = """SELECT Task1,Task2,Total
                FROM student_grades 
                WHERE name = ?;"""

    cursor.execute(query, (username, ))
    data = cursor.fetchone()
    connection.close()
    return data


# get all student grades for teacher view
def get_all_grades():

    connection = sqlite3.connect("grade_distributor.db")
    cursor = connection.cursor()
    query = """SELECT login_details.name, Task1,Task2,Total 
              FROM login_details,student_grades 
              WHERE login_details.login_name = student_grades.name;"""

    cursor.execute(query)
    data = cursor.fetchall()
    connection.close()
    return data


def is_valid_username(username):
    connection = sqlite3.connect("grade_distributor.db")
    cursor = connection.cursor()
    query = """SELECT login_name FROM login_details;"""
    cursor.execute(query)
    data = cursor.fetchall()
    connection.close()

    return (username, ) in data


@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template('index.html')
    #post
    username = request.form.get("user")
    password = request.form.get("pw")
    # username = request.form["user"]
    # password = request.form["pw"]

    if not is_valid_username(username):
        return render_template('index.html', message="Invalid username!")

    # get_login_details returns password and role in a tuple
    login_details = get_login_details(username)

    if password == login_details[0]:
        if login_details[1] == 'student':
            return render_template('student_view.html',
                                   student_name=login_details[2],
                                   grades=get_grades(username))
        else:
            return render_template('teacher_view.html',
                                   student_grades=get_all_grades())
    else:
        return render_template('index.html', message="Wrong password!")
        # return render_template('error.html',
        #                        username=username,
        #                        password=login_details[1])


app.run(host='0.0.0.0', port=81)
