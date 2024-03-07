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

def run_query1():
    query = f'''SELECT s_suppkey, o_orderkey
                FROM supplier, lineitem l1, orders, nation WHERE s_suppkey = l1.l_suppkey
                AND o_orderkey = l1.l_orderkey
                AND o_orderstatus = 'F'
                AND l1.l_receiptdate > l1.l_commitdate AND EXISTS (
                SELECT *
                FROM lineitem l2
                WHERE l2.l_orderkey = l1.l_orderkey
                AND l2.l_suppkey <> l1.l_suppkey ) AND NOT EXISTS (
                SELECT *
                FROM lineitem l3
                WHERE l3.l_orderkey = l1.l_orderkey
                AND l3.l_suppkey <> l1.l_suppkey
                AND l3.l_receiptdate > l3.l_commitdate ) AND s_nationkey = n_nationkey
                AND n_name = "GERMANY"'''
    
    mycursor.execute(query)
    myresult = mycursor.fetchall()
    #print(myresult)
    return myresult

query1 = run_query1()
    
