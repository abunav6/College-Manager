import re

from mysql import connector as mysql


class Login:
    def __init__(self):
        self.sql_data = {}
        regex = "(.*)\s+=\s+\"(.*)\""
        with open("/Users/anubhavdinkar/Desktop/CollegeManager/sql_data.txt", "r") as file:
            lines = file.readlines()
            for line in lines:
                temp = re.findall(regex, line)[0]
                self.sql_data[temp[0]] = temp[1]

    def connect(self):
        cnx = mysql.connect(user=self.sql_data['uname'], password=self.sql_data['pwd'], host=self.sql_data['host'],
                            buffered=True)
        cur = cnx.cursor()
        cur.execute("create database if not exists College_Manager")
        cnx.database = "College_Manager"
        cur.execute("use College_Manager")
        cur.execute("create table if not exists Subject_Data (subject_name LONGTEXT, credits INT, lab INT)")
        cur.execute("create table if not exists Attendance_Data (subject_name LONGTEXT, missed INT, total INT)")
        cur.execute("create table if not exists Test_Data (subject_name LONGTEXT, t1 REAL, q1 REAL, t2 REAL, q2 REAL, "
                    "t3 REAL, q3 REAL, ss REAL, grade VARCHAR(20), percentage REAL)")
        cnx.autocommit = True
        return cnx, cur
