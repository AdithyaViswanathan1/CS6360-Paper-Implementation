import mysql.connector
import json
import random
import time

with open("secrets.json", "r") as file:
    secrets = json.load(file)

NULL_LOG_FILE = "null_log.txt"

def connect_to_database(database_name):
    # Connect to the MySQL database
    mydb = mysql.connector.connect(
    host = "localhost",
    user = secrets['SQL_USERNAME'],
    password = secrets["SQL_PASSWORD"],
    database = database_name,
    )
    return mydb

def timeit(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Execution time of {func.__name__}: {execution_time:.6f} seconds\n")
        return result
    return wrapper

import mysql.connector

@timeit
def copy_database(source_db, dest_db):
    try:
        # Create new database
        mycursor.execute(f"CREATE DATABASE IF NOT EXISTS {dest_db}")
        
        # Export schema and data from source database
        mycursor.execute(f"USE {source_db}")
        mycursor.execute("SHOW TABLES")
        tables = mycursor.fetchall()
        for table in tables:
            table_name = table[0]
            mycursor.execute(f"CREATE TABLE {dest_db}.{table_name} LIKE {source_db}.{table_name}")
            mycursor.execute(f"INSERT INTO {dest_db}.{table_name} SELECT * FROM {source_db}.{table_name}")

        # Commit changes
        mydb.commit()
        print("Database copied successfully!")

    except mysql.connector.Error as error:
        print(f"Error: {error}")

def get_nullable_attributes(database_name):
    # Execute a query to retrieve column information
    query = f"SELECT TABLE_NAME, COLUMN_NAME, IS_NULLABLE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = '{ database_name }'"
    mycursor.execute(query)

    # Fetch all the rows
    columns_info = mycursor.fetchall()

    # Print the column information
    nullable_list = {}
    for column_info in columns_info:
        table = column_info[0]
        column = column_info[1]
        nullable = column_info[2]
        if nullable == "YES":
            # print(f"{table}.{column}")
            if table in nullable_list.keys():
                nullable_list[table].append(column)
            else:
                nullable_list[table] = [column]
    #print(columns_info)
    return nullable_list

def count_nulls(table_name, column_name):
    # Construct the SQL query to count the number of nulls in the column
    query = f"SELECT COUNT(*) FROM {table_name} WHERE {column_name} IS NULL"

    # Execute the SQL query
    mycursor.execute(query)

    # Fetch the result
    null_count = mycursor.fetchone()[0]

    # Print the number of nulls
    print(f"Number of nulls in column '{column_name}': {null_count}")

    return null_count

def get_pk(table_name):
    # Execute the SHOW KEYS statement to retrieve the primary key attribute for the specified table
    query = f"SHOW KEYS FROM {table_name} WHERE Key_name = 'PRIMARY';"
    mycursor.execute(query)

    # Fetch the primary key attribute
    primary_keys = mycursor.fetchall()
    final_pks = []

    if primary_keys:
        #print(f"The primary key attributes for table '{table_name}' are:")
        for key in primary_keys:
            #print(f"- {key[4]}")
            final_pks.append(key[4])
    else:
        print(f"No primary key found for table '{table_name}'.")
    
    return final_pks

@timeit
def insert_nulls(table_name, column_name, null_rate):
    select_query = f"SELECT {column_name} FROM {table_name};"
    mycursor.execute(select_query)

    # Fetch all the rows
    rows = mycursor.fetchall()

    # Print the values of the specified column
    # print(f"Values in column '{column_name}' {len(rows)}:")
    # for row in rows[:5]:
    #     print(row[0])
    

    # Fetch all rows from the table
    select_query = f"SELECT * FROM {table_name};"
    mycursor.execute(select_query)
    rows = mycursor.fetchall()
    
    # Execute a query to describe the table structure
    mycursor.execute(f"DESCRIBE {table_name}")

    # Fetch all the rows (attributes)
    attributes = mycursor.fetchall()

    # Extract the attribute names from the result
    attribute_names = [attr[0] for attr in attributes]
    #print("ATTRIBUTES", attribute_names)

    # Index of column_name in attribute list
    column_index = attribute_names.index(column_name)
    #print(f"Index of {column_name} = {column_index}")

    # get primary key index of the table
    pks = get_pk(table_name)
    pk_indices = [attribute_names.index(pk) for pk in pks]
    #print(pks,pk_indices)

    # Update each row individually based on the null rate
    num_rows_changed = 0
    #random.seed(2311)
    for i,row in enumerate(rows):
        # Generate a random threshold value
        threshold = random.random()  # Random value between 0 and 1
        #print(i,threshold)
        
        # Check if the generated value is less than or equal to the null rate
        if threshold <= null_rate:
            num_rows_changed += 1
            #print("ROW:\n", row)
            #print("Changing value:",row[column_index])
            # Update the specific column to null for the current row
            update_query = f"UPDATE {table_name} SET {column_name} = NULL WHERE "
            if len(pks) == 1:
                update_query += f"{pks[0]} = {row[pk_indices[0]]};"
            elif len(pks) == 2:
                update_query += f"{pks[0]} = {row[pk_indices[0]]} AND {pks[1]} = {row[pk_indices[1]]};"
            #print("QUERY:\n", update_query,"\n")
            mycursor.execute(update_query)
            mydb.commit()
            # #print(f"Value in column '{column_name}' set to NULL for row with primary key {row[pks]}.")

    null_count = count_nulls(table_name,column_name)
    #print(f"{table_name}.{column_name}: {num_rows_changed}/{len(rows)} rows changed ({num_rows_changed/len(rows):.4})")
    log_out = f"{table_name}.{column_name}: {null_count}/{len(rows)} rows changed ({null_count/len(rows):.4})\n"
    with open(NULL_LOG_FILE, 'a') as f:
        f.write(log_out)

with open(NULL_LOG_FILE, 'w') as f:
    f.write(f'NULL LOG\n\n')

# !!! PRIMARY DETERMINANT VARIABLE (determines base db to make copies from) !!!
source_db_name = "tpch_og"
mydb = connect_to_database(source_db_name)
mycursor = mydb.cursor(buffered=True)
nullable = get_nullable_attributes(source_db_name)
#print("Nullable attributes", nullable)

# !!! PRIMARY DETERMINANT LIST (determines null rate of the db copies) !!!
null_rates = [6,8,10]
db_names = []
for null_rate in null_rates:
    db_names.append(f"{source_db_name}_{null_rate}pct")
# EXAMPLE RESULT: db_names = ['tpch_1gb_2pct','tpch_1gb_4pct', 'tpch_1gb_6pct', 'tpch_1gb_8pct', 'tpch_1gb_10pct']

print("Creating db copies:", db_names)
for db_name in db_names:
    print(f"Creating {db_name}")
    start_time = time.time()
    copy_database(source_db_name,db_name)
    end_time = time.time()
    elapsed_time = end_time - start_time
    with open(NULL_LOG_FILE, 'a') as f:
        f.write(f'Created database: {db_name} in {elapsed_time:.4} seconds.\n')


start_time = time.time()

# For given null rates,
# write nulls to every nullable attribute in each of the databases
for null_rate,db_name in zip(null_rates, db_names):
    mydb = connect_to_database(db_name)
    mycursor = mydb.cursor(buffered=True)
    with open(NULL_LOG_FILE, 'a') as f:
        f.write(f'\n!!! Null insertion into {db_name} at rate of {null_rate}% !!!\n\n')
    for table,columns in nullable.items():
        for column in columns:
            insert_nulls(table, column, null_rate/100)

end_time = time.time()
elapsed_time = end_time - start_time
with open(NULL_LOG_FILE, 'a') as f:
    f.write(f'\nTime elapsed: {elapsed_time:.4} seconds')

# Close the cursor and connection
mycursor.close()
mydb.close()