from flask import Flask, render_template, jsonify
import pandas as pd
import numpy as np
from sqlalchemy import create_engine

app = Flask(__name__)

# Database connection string
engine = create_engine('mysql+pymysql://root@localhost/customer_db')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data')
def data():
    # Query to get Customer Distribution by Location and Account Balance Distribution
    customers_query = "SELECT * FROM customers;"
    customers = pd.read_sql(customers_query, engine)

    # Prepare Customer Distribution by Location (Pie Chart)
    location_counts = customers['CustLocation'].value_counts()
    location_pie_chart = {
        'locations': location_counts.index.tolist(),
        'counts': location_counts.values.tolist()
    }

    # Categorize customer account balances into groups (low, medium, high)
    bins = [0, 5000, 20000, np.inf]  # Low (<5000), Medium (5000-20000), High (>20000)
    labels = ['Low Balance', 'Medium Balance', 'High Balance']
    customers['BalanceCategory'] = pd.cut(customers['CustAccountBalance'], bins=bins, labels=labels)

    # Prepare Account Balance Distribution (Pie Chart)
    balance_counts = customers['BalanceCategory'].value_counts()
    balance_pie_chart = {
        'categories': balance_counts.index.tolist(),
        'counts': balance_counts.values.tolist()
    }

    return jsonify({
        'location_pie_chart': location_pie_chart,
        'balance_pie_chart': balance_pie_chart
    })

@app.route('/transaction_details')
def transaction_details():
    return render_template('transaction_details.html')

@app.route('/api/transaction_data')
def transaction_data():
    # Query to get transaction details
    transactions_query = "SELECT * FROM transactions;"
    transactions = pd.read_sql(transactions_query, engine)

    # Categorize transaction amount into low, medium, high
    bins = [0, 1000, 5000, np.inf]  # Low (<1000), Medium (1000-5000), High (>5000)
    labels = ['Low Amount', 'Medium Amount', 'High Amount']
    transactions['AmountCategory'] = pd.cut(transactions['TransactionAmount'], bins=bins, labels=labels)

    # Prepare Transaction Amount Distribution (Bar Chart)
    transaction_counts = transactions.groupby(['CustomerID', 'TransactionID', 'AmountCategory']).size().reset_index(name='Count')
    transaction_chart = {
        'customer_ids': transaction_counts['CustomerID'].tolist(),
        'transaction_ids': transaction_counts['TransactionID'].tolist(),
        'amount_categories': transaction_counts['AmountCategory'].tolist(),
        'counts': transaction_counts['Count'].tolist()
    }

    return jsonify(transaction_chart)

if __name__ == '__main__':
    app.run(debug=True)
