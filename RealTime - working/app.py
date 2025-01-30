from flask import Flask, render_template, jsonify
from sqlalchemy import create_engine
import pandas as pd

app = Flask(__name__)

# Database connection
engine = create_engine("mysql+pymysql://root:@localhost/customer_db")

@app.route("/")
def index():
    """Render the dashboard."""
    return render_template("index.html")

@app.route("/api/realtime_transactions", methods=["GET"])
def get_realtime_transactions():
    """Fetch real-time transactions from the database."""
    query = """
    SELECT TransactionID, TransactionAmount, timestamp, CustomerID
    FROM realtimetransactions
    WHERE timestamp > NOW() - INTERVAL 1 HOUR
    """
    df = pd.read_sql(query, engine)

    if df.empty:
        return jsonify({"message": "No recent transactions found"}), 404

    # Prepare data for visualization
    data = {
        "TransactionIDs": df["TransactionID"].tolist(),
        "TransactionAmounts": df["TransactionAmount"].tolist(),
        "Timestamps": df["timestamp"].astype(str).tolist(),
        "CustomerIDs": df["CustomerID"].tolist(),
    }
    return jsonify(data)

@app.route("/api/customer_transactions", methods=["GET"])
def get_customer_transactions():
    """Fetch customer data for customer transactions chart."""
    query = """
    SELECT CustomerID, COUNT(*) AS TransactionCount, SUM(TransactionAmount) AS TotalTransactionAmount
    FROM realtimetransactions
    WHERE timestamp > NOW() - INTERVAL 1 HOUR
    GROUP BY CustomerID
    """
    df = pd.read_sql(query, engine)

    if df.empty:
        return jsonify({"message": "No recent customer transactions found"}), 404

    # Prepare data for visualization (Customer ID vs Total Transaction Amount)
    data = {
        "CustomerIDs": df["CustomerID"].tolist(),
        "TotalTransactionAmounts": df["TotalTransactionAmount"].tolist(),
    }
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
