# query_data.py
import mysql.connector
import pandas as pd

# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",  # No password
    database="customer_db"
)

# Query real-time data
query = "SELECT * FROM `realtimetransactions` WHERE `timestamp` > NOW() - INTERVAL 1 HOUR;"
data = pd.read_sql(query, conn)

# Print the data
print(data)

# Close the connection
conn.close()