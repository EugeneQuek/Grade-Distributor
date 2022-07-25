from flask import Flask, render_template, request
import sqlite3

connection = sqlite3.connect("grade_distributor.db")
cursor = connection.cursor()

def get_login_details(username):
    
    query = """SELECT password, role
                FROM login_details 
                WHERE login_name = ?;"""
    cursor.execute(query, (username,))
    return cursor.fetchone()

login_details = get_login_details("teacher1")
print(login_details)