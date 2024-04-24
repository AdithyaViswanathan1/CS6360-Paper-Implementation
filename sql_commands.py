'''
SETUP: 
https://www.w3schools.com/python/python_mysql_getstarted.asp
pip install mysql-connector-python
'''
import mysql.connector
import json
import random
import time

def connect_to_db(database_name):
    with open("secrets.json", "r") as file:
        secrets = json.load(file)

    mydb = mysql.connector.connect(
    host = "localhost",
    user = secrets['SQL_USERNAME'],
    password = secrets["SQL_PASSWORD"],
    database = database_name,
    )

    mycursor = mydb.cursor()

    return mydb,mycursor

def get_version(mycursor):
    # Execute a query to retrieve the SQL version
    mycursor.execute("SELECT VERSION()")

    # Fetch the result
    sql_version = mycursor.fetchone()[0]

    # Print the SQL version
    print("SQL version:", sql_version)

def run_query(mycursor, query):
    mycursor.execute(query)
    myresult = mycursor.fetchall()
    #print(myresult)
    return myresult

def get_attribute_names(mycursor, table_name):
    # Execute a query to describe the table structure
    mycursor.execute(f"DESCRIBE {table_name}")

    # Fetch all the rows (attributes)
    attributes = mycursor.fetchall()

    # Extract the attribute names from the result
    attribute_names = [attr[0] for attr in attributes]
    # print("ATTRIBUTES", attribute_names)
    return attribute_names

def get_nullable_attributes(mycursor):
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
        # print("Table:", column_info[0])
        # print("Column:", column_info[1])
        # print("Nullable:", column_info[2])
        # print()
        if nullable == "YES":
            # print(f"{table}.{column}")
            nullable_list.append(f"{table}.{column}")
    #print(columns_info)
    return nullable_list

def run_query1(mycursor, nation, simple=True):
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
                AND l3.l_receiptdate > l3.l_commitdate ) 
                AND s_nationkey = n_nationkey
                AND n_name = "{nation}"'''
    
    start_time = time.time()
    mycursor.execute(query)
    end_time = time.time()
    total_time = end_time - start_time
    myresult = mycursor.fetchall()
    #print(myresult)
    
    if simple:
        return myresult
    return myresult, total_time, nation

def run_query1_modified(mycursor, nation):
    query = f"""SELECT s_suppkey, o_orderkey
                FROM supplier, lineitem l1, orders, nation
                WHERE s_suppkey = l1.l_suppkey
                AND o_orderkey = l1.l_orderkey
                AND o_orderstatus = 'F'
                AND l1.l_receiptdate > l1.l_commitdate
                AND s_nationkey = n_nationkey
                AND n_name = "{nation}"
                AND EXISTS (
                SELECT *
                FROM lineitem l2
                WHERE l2.l_orderkey = l1.l_orderkey
                AND l2.l_suppkey <> l1.l_suppkey )
                AND NOT EXISTS (
                SELECT *
                FROM lineitem l3
                WHERE l3.l_orderkey = l1.l_orderkey
                AND ( l3.l_suppkey <> l1.l_suppkey
                OR l3.l_suppkey IS NULL )
                AND ( l3.l_receiptdate > l3.l_commitdate
                OR l3.l_receiptdate IS NULL
                OR l3.l_commitdate IS NULL ) )"""
    start_time = time.time()
    mycursor.execute(query)
    end_time = time.time()
    total_time = end_time - start_time
    myresult = mycursor.fetchall()
    return myresult, total_time

def run_query2(mycursor, countries, simple=True):
    #countries = ('GERMANY', 'INDIA', 'UNITED STATES', 'INDONESIA', 'UNITED KINGDOM', 'ARGENTINA', 'PERU')
    query = f'''SELECT c_custkey, c_nationkey
                FROM customer
                WHERE c_nationkey IN {countries}
                    AND c_acctbal > (
                                    SELECT avg(c_acctbal) FROM customer
                                    WHERE c_acctbal > 0.00
                                    AND c_nationkey IN {countries} ) 
                    AND NOT EXISTS (
                                    SELECT *
                                    FROM orders
                                    WHERE o_custkey = c_custkey )
            '''
    start_time = time.time()
    mycursor.execute(query)
    end_time = time.time()
    total_time = end_time - start_time
    myresult = mycursor.fetchall()
    #print(myresult)
    if simple:
        return myresult
    return myresult, total_time, countries

def run_query2_modified(mycursor, countries):
    query = f"""SELECT c_custkey, c_nationkey
                FROM customer
                WHERE c_nationkey IN {countries}
                AND c_acctbal > (
                SELECT AVG(c_acctbal)
                FROM customer
                WHERE c_acctbal > 0.00
                AND c_nationkey IN {countries} )
                AND NOT EXISTS (
                SELECT *
                FROM orders
                WHERE o_custkey = c_custkey )
                AND NOT EXISTS (
                SELECT *
                FROM orders
                WHERE o_custkey IS NULL ) """
    start_time = time.time()
    mycursor.execute(query)
    end_time = time.time()
    total_time = end_time - start_time
    myresult = mycursor.fetchall()
    return myresult, total_time

def run_query3(mycursor, simple=True):
    q = "SELECT S_SUPPKEY FROM SUPPLIER ORDER BY RAND() LIMIT 1;"
    mycursor.execute(q)
    supp_key = mycursor.fetchall()[0][0]
    #print("random supp_key", supp_key)

    query = f'''
            SELECT o_orderkey
            FROM orders
            WHERE NOT EXISTS (
            SELECT *
            FROM lineitem
            WHERE l_orderkey = o_orderkey
            AND l_suppkey <> {supp_key} )
    '''
    start_time = time.time()
    mycursor.execute(query)
    end_time = time.time()
    total_time = end_time - start_time
    myresult = mycursor.fetchall()
    myresult = [tup[0] for tup in myresult]
    #print(myresult)
    if simple:
        return myresult
    return myresult, total_time, supp_key

def run_query3_modified(mycursor, s_key):
    query = f'''
            SELECT o_orderkey
            FROM orders
            WHERE NOT EXISTS (
            SELECT *
            FROM lineitem
            WHERE l_orderkey = o_orderkey
            AND ( l_suppkey <> {s_key}
            OR l_suppkey IS NULL ) )
    '''
    
    start_time = time.time()
    mycursor.execute(query)
    end_time = time.time()
    total_time = end_time - start_time
    myresult = mycursor.fetchall()
    myresult = [tup[0] for tup in myresult]
    #print(myresult)
    return myresult,total_time

def run_query4(mycursor, all_nations, simple=True):
    # List of colors in Clause 4.2.3: https://www.tpc.org/tpc_documents_current_versions/pdf/tpc-h_v2.17.1.pdf
    colors = [  "almond", "antique", "aquamarine", "azure", "beige", "bisque", "black", "blanched", "blue",
                "blush", "brown", "burlywood", "burnished", "chartreuse", "chiffon", "chocolate", "coral",
                "cornflower", "cornsilk", "cream", "cyan", "dark", "deep", "dim", "dodger", "drab", "firebrick",
                "floral", "forest", "frosted", "gainsboro", "ghost", "goldenrod", "green", "grey", "honeydew",
                "hot", "indian", "ivory", "khaki", "lace", "lavender", "lawn", "lemon", "light", "lime", "linen",
                "magenta", "maroon", "medium", "metallic", "midnight", "mint", "misty", "moccasin", "navajo",
                "navy", "olive", "orange", "orchid", "pale", "papaya", "peach", "peru", "pink", "plum", "powder",
                "puff", "purple", "red", "rose", "rosy", "royal", "saddle", "salmon", "sandy", "seashell", "sienna",
                "sky", "slate", "smoke", "snow", "spring", "steel", "tan", "thistle", "tomato", "turquoise", "violet",
                "wheat", "white", "yellow"
            ]
    #print(f"{len(colors)} possible colors")
    color = colors[random.randint(0,len(colors)-1)]
    nation = all_nations[random.randint(0,len(all_nations)-1)]
    #print("color", color, "nation", nation)
    query = f"""SELECT o_orderkey
                FROM orders
                WHERE NOT EXISTS (
                SELECT *
                FROM lineitem, part, supplier, nation
                WHERE l_orderkey = o_orderkey
                AND l_partkey = p_partkey
                AND l_suppkey = s_suppkey
                AND p_name LIKE '%{color}%'
                AND s_nationkey = n_nationkey
                AND n_name = '{nation}' )
            """
    start_time = time.time()
    mycursor.execute(query)
    end_time = time.time()
    total_time = end_time - start_time
    myresult = mycursor.fetchall()
    #print(myresult)
    myresult = [tup[0] for tup in myresult]
    #print(len(myresult), myresult[:5])
    if simple:
        return myresult, color, nation
    return myresult, total_time, nation, color

def run_query4_modified(mycursor, nation, color):
    query1 = f"""   CREATE OR REPLACE VIEW part_view AS
                    SELECT p_partkey
                    FROM part
                    WHERE p_name IS NULL
                    UNION
                    SELECT p_partkey
                    FROM part
                    WHERE p_name LIKE '%{color}%';"""
    query2 = f"""   CREATE OR REPLACE VIEW supp_view AS
                    SELECT s_suppkey
                    FROM supplier
                    WHERE s_nationkey IS NULL
                    UNION
                    SELECT s_suppkey
                    FROM supplier, nation
                    WHERE s_nationkey = n_nationkey
                    AND n_name = '{nation}';"""
    query3 = f"""
                SELECT o_orderkey
                FROM orders
                WHERE NOT EXISTS (
                SELECT *
                FROM lineitem, part_view, supp_view
                WHERE l_orderkey = o_orderkey
                AND l_partkey = p_partkey
                AND l_suppkey = s_suppkey )
                AND NOT EXISTS (
                SELECT *
                FROM lineitem, supp_view
                WHERE l_orderkey = o_orderkey
                AND l_partkey IS NULL
                AND l_suppkey = s_suppkey
                AND EXISTS ( SELECT * FROM part_view ) )
                AND NOT EXISTS (
                SELECT *
                FROM lineitem, part_view
                WHERE l_orderkey = o_orderkey
                AND l_partkey = p_partkey
                AND l_suppkey IS NULL
                AND EXISTS ( SELECT * FROM supp_view ) )
                AND NOT EXISTS (
                SELECT *
                FROM lineitem
                WHERE l_orderkey = o_orderkey
                AND l_partkey IS NULL
                AND l_suppkey IS NULL
                AND EXISTS ( SELECT * FROM part_view )
                AND EXISTS ( SELECT * FROM supp_view ) ) """
    
    # print("1st parts")
    mycursor.execute(query1)
    mycursor.execute(query2)
    # print("execution")
    start_time = time.time()
    mycursor.execute(query3)
    end_time = time.time()
    total_time = end_time - start_time
    # print("fetching all")
    myresult = mycursor.fetchall()
    #print(myresult)
    return myresult,total_time

# mydb, mycursor = connect_to_db()
# get_version(mycursor)

# Close the cursor and connection
def close_db(mydb, mycursor):
    mycursor.close()
    mydb.close()
