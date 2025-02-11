from sqlalchemy import create_engine, text
from werkzeug.security import generate_password_hash
import pandas as pd

# Database connection details
DB_USER = "postgres"
DB_PASSWORD = "123456"
DB_HOST = "34.155.51.237"
DB_PORT = "5432"
DB_NAME = "postgres"

# Create the database engine
engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# Fetch all users with their plain-text passwords
query = "SELECT email, password FROM users"
df = pd.read_sql(query, engine)

# Update each user's password with a hashed version
with engine.connect() as connection:
    for _, row in df.iterrows():
        email = row["email"]
        plain_password = row["password"]
        hashed_password = generate_password_hash(plain_password)  # Hash the password

        # Update the database with the hashed password
        update_query = text("UPDATE users SET password = :password WHERE email = :email")
        connection.execute(update_query, {"password": hashed_password, "email": email})

    connection.commit()  # Commit all updates

print("All passwords have been hashed and updated successfully.")