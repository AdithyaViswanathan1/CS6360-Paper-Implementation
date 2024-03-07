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
  host="localhost",
  user=secrets['SQL_USERNAME'],
  password=secrets["SQL_PASSWORD"]
)

print(mydb)