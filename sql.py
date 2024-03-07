'''
SETUP: 
https://www.w3schools.com/python/python_mysql_getstarted.asp
pip install mysql-connector-python
'''
import mysql.connector
import json

with open("secrets.json", "r") as file:
    secrets = json.load(file)

mydb = mysql.connector.connect(
  host = "localhost",
  user = secrets['SQL_USERNAME'],
  password = secrets["SQL_PASSWORD"],
  database = secrets["DATABASE_NAME"],
)

mycursor = mydb.cursor()

mycursor.execute("SELECT N_NATIONKEY, N_Name FROM NATION WHERE N_Name LIKE '%AN%'")

myresult = mycursor.fetchall()

print(myresult)