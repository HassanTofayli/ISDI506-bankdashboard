import mysql.connector
from datetime import datetime
import time
import random

# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",  # No password
    database="customer_db"
)
cursor = conn.cursor()

# Fetch all customer IDs from the customers table
cursor.execute("SELECT CustomerID FROM customers")
customer_ids = [row[0] for row in cursor.fetchall()]

# Simulate real-time data ingestion
while True:
    # Randomly choose a CustomerID from the list of existing CustomerIDs
    customer_id = random.choice(customer_ids)
    
    # Generate a random transaction
    transaction = {
        "CustomerID": customer_id,  # Randomly chosen customer ID from customers table
        "TransactionID": random.randint(1000, 9999),  # Random transaction ID
        "TransactionAmount": round(random.uniform(100, 5000), 2),  # Random transaction amount
        "timestamp": datetime.now()  # Current timestamp
    }

    # Insert the transaction into the database
    query = """
    INSERT INTO realtimetransactions (CustomerID, TransactionID, TransactionAmount, timestamp)
    VALUES (%s, %s, %s, %s)
    """
    cursor.execute(query, (transaction["CustomerID"], transaction["TransactionID"], transaction["TransactionAmount"], transaction["timestamp"]))
    conn.commit()

    print(f"Inserted transaction: {transaction}")

    # Wait for 2 seconds before inserting the next transaction
    time.sleep(2)

# Close the connection (this will never be reached in this example)
cursor.close()
conn.close()
