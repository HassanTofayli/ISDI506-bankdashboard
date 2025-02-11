import random
import time
from datetime import datetime, date
import psycopg2
from sqlalchemy import create_engine

# Database connection parameters
DB_USER = 'postgres'
DB_PASSWORD = '123456'
DB_HOST = '34.155.51.237'
DB_PORT = '5432'
DB_NAME = 'postgres'

# Create SQLAlchemy engine
engine = create_engine(f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
)
cursor = conn.cursor()

# Fetch all customer IDs and corresponding jobs from the customers table
cursor.execute("SELECT customer_id, job FROM customers")
customers = cursor.fetchall()
customer_data = {cust[0]: cust[1] for cust in customers}  # Dictionary mapping customer_id to job

# Fetch all merchants and corresponding categories from the transactions table
cursor.execute("SELECT DISTINCT merchant, category FROM transactions")
merchants = cursor.fetchall()

# Fetch all cities and corresponding states from the transactions table
cursor.execute("SELECT DISTINCT city, state FROM transactions")
cities = cursor.fetchall()

# Simulate real-time data ingestion
while True:
    # Randomly choose a CustomerID and its corresponding job
    customer_id = random.choice(list(customer_data.keys()))
    job = customer_data[customer_id]
    
    # Randomly choose a merchant and its category
    merchant, category = random.choice(merchants)
    
    # Randomly choose a city and its corresponding state
    city, state = random.choice(cities)
    
    # Generate a random transaction
    transaction = {
        "customer_id": customer_id,
        "trans_date_trans_time": datetime.now(),
        "cc_num": str(random.randint(4000000000000000, 4999999999999999)),
        "merchant": merchant,
        "category": category,
        "amt": round(random.uniform(1, 5000), 2),
        "gender": random.choice(["M", "F"]),
        "street": f"{random.randint(1, 9999)} Main St",
        "city": city,
        "state": state,
        "zip": str(random.randint(10000, 99999)),
        "customer_lat": round(random.uniform(-90, 90), 6),
        "customer_long": round(random.uniform(-180, 180), 6),
        "city_pop": random.randint(80, 1000000),
        "job": job,
        "dob": date(random.randint(1950, 2005), random.randint(1, 12), random.randint(1, 28)),
        "trans_num": "".join(random.choices("abcdef0123456789", k=32)),
        "unix_time": time.time(),
        "merch_lat": round(random.uniform(-90, 90), 6),
        "merch_long": round(random.uniform(-180, 180), 6),
        "is_fraud": False
    }

    # Insert the transaction into the database
    query = """
    INSERT INTO transactions (
        customer_id, trans_date_trans_time, cc_num, merchant, category, amt, gender, street, city, state, zip, 
        customer_lat, customer_long, city_pop, job, dob, trans_num, unix_time, merch_lat, merch_long, is_fraud
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, tuple(transaction.values()))
    conn.commit()

    print(f"Inserted transaction: {transaction}")

    # Wait for 2 seconds before inserting the next transaction
    time.sleep(2)

# Close the connection (this will never be reached in this example)
cursor.close()
conn.close()
