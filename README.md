# Grade-Distributor
This project is designed to help teachers distribute grades individually.
There are 2 different users: students and teachers

Task allocation:
1. Database (MC)
2. Flask (HT)
3. Html (EQ)

Test cases:  
Username: student1  
Password: spw1  

Username: teacher1  
Password: tpw1  

Database tables:

Table 1: login_details
Column names: login_name, password, name, role

Table 2: student_grades
Column names: name (same as login_name from table login_details), Task1, Task2, Total

