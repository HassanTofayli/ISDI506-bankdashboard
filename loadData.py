import pandas as pd
from sqlalchemy import create_engine

# Load the single CSV file
df = pd.read_csv('customerDetails.csv')

# Split into Customers and Transactions DataFrames
customers = df[['CustomerID', 'CustomerDOB', 'CustGender', 'CustLocation', 'CustAccountBalance']].drop_duplicates()

transactions = df[['TransactionID', 'CustomerID', 'TransactionDate', 'TransactionTime', 'TransactionAmount (INR)']]

# Rename columns to match MySQL schema
customers.rename(columns={'CustGender': 'CustGender',
                          'CustLocation': 'CustLocation',
                          'CustAccountBalance': 'CustAccountBalance',
                          'CustomerDOB': 'CustomerDOB'}, inplace=True)

transactions.rename(columns={'TransactionAmount (INR)': 'TransactionAmount'}, inplace=True)

# Connect to MySQL
engine = create_engine('mysql+pymysql://root:@localhost/customer_db')

# Ensure tables are empty or replace existing data
customers.to_sql('customers', con=engine, if_exists='replace', index=False)
transactions.to_sql('transactions', con=engine, if_exists='replace', index=False)

print("Data successfully loaded into MySQL!")
# Check for duplicate CustomerIDs in customers table
assert customers['CustomerID'].is_unique, "CustomerID must be unique in Customers table!"

# Check for foreign key integrity
missing_customers = transactions[~transactions['CustomerID'].isin(customers['CustomerID'])]
if not missing_customers.empty:
    print("Warning: The following transactions have CustomerIDs not found in the Customers table:")
    print(missing_customers)
