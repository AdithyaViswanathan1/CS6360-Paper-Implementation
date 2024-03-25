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

def get_version():
    # Execute a query to retrieve the SQL version
    mycursor.execute("SELECT VERSION()")

    # Fetch the result
    sql_version = mycursor.fetchone()[0]

    # Print the SQL version
    print("SQL version:", sql_version)

def get_nullable_attributes():
    # Execute a query to retrieve column information
    query = f"SELECT TABLE_NAME, COLUMN_NAME, IS_NULLABLE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = '{ secrets['DATABASE_NAME'] }'"
    mycursor.execute(query)

    # Fetch all the rows
    columns_info = mycursor.fetchall()

    # Print the column information
    nullable_list = []
    for column_info in columns_info:
        table = column_info[0]
        column = column_info[1]
        nullable = column_info[2]
        if nullable == "YES":
            # print(f"{table}.{column}")
            nullable_list.append(f"{table}.{column}")
    #print(columns_info)
    return nullable_list

get_version()
nullable = get_nullable_attributes()
print(nullable)

# Close the cursor and connection
mycursor.close()
mydb.close()