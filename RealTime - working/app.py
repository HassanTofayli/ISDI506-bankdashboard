from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from flask import Flask, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from sqlalchemy import create_engine, text
from werkzeug.security import generate_password_hash, check_password_hash
# from sqlalchemy import sessionmaker
from models import db, User  # Import the User model

app = Flask(__name__)
app.secret_key = "123456"  # Required for session management

# Flask-Login setup
# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = "login"  # Redirect unauthorized users to the login page

# Database connection
DB_USER = "postgres"
DB_PASSWORD = "123456"
DB_HOST = "34.155.51.237"
DB_PORT = "5432"
DB_NAME = "postgres"

engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# db = SQLAlchemy(app)

# Initialize database
db.init_app(app)


# Flask-Login setup
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_email):
    return User.query.filter_by(email=user_email).first()  # Load user by email

@app.route('/')
def home():
    embed_url = "https://lookerstudio.google.com/embed/reporting/b445b12f-cf37-41a8-9576-d9dddaef7c32/page/1XMmE"
    return render_template('index.html', embed_url=embed_url)

# # User class for Flask-Login
# class User(UserMixin):
#     def __init__(self, user_id, email):
#         self.id = user_id
#         self.email = email

# Flask-Login: Load user from database
# @login_manager.user_loader
# def load_user(user_id):
#     with engine.connect() as connection:
#         query = text("SELECT email FROM users WHERE email = :email")
#         result = connection.execute(query, {"email": user_id})
#         user = result.fetchone()
#         if user:
#             return User(user["email"], user["email"])
#     return None

# @app.route("/")
# def index():
#     """Render the dashboard."""
#     return render_template("index.html")

# Routes
@app.route("/")
@login_required  # Protect the dashboard route
def index():
    """Render the dashboard."""
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        
        flash('Invalid email or password.', 'danger')

    return render_template('login.html')

#logout
@app.route("/logout")
@login_required
def logout():
    """Log the user out."""
    logout_user()
    return redirect(url_for("login"))

# Ensure tables exist
with app.app_context():
    db.create_all()


@app.route("/api/realtime_transactions", methods=["GET"])
def get_realtime_transactions():
    """Fetch real-time transactions from the database."""
    query = """
    SELECT trans_num, amt, trans_date_trans_time, customer_id
    FROM transactions
    WHERE trans_date_trans_time > NOW() - INTERVAL '1 HOUR'
    """
    df = pd.read_sql(query, engine)

    if df.empty:
        return jsonify({"message": "No recent transactions found"}), 404

    # Prepare data for visualization
    data = {
        "TransactionIDs": df["trans_num"].tolist(),
        "TransactionAmounts": df["amt"].tolist(),
        "Timestamps": df["trans_date_trans_time"].astype(str).tolist(),
        "CustomerIDs": df["customer_id"].tolist(),
    }
    return jsonify(data)

@app.route("/api/customer_transactions", methods=["GET"])
def get_customer_transactions():
    """Fetch customer data for customer transactions chart."""
    query = """
    SELECT customer_id, COUNT(*) AS transaction_count, SUM(amt) AS total_transaction_amount
    FROM transactions
    WHERE trans_date_trans_time > NOW() - INTERVAL '1 HOUR'
    GROUP BY customer_id
    """
    df = pd.read_sql(query, engine)

    if df.empty:
        return jsonify({"message": "No recent customer transactions found"}), 404

    # Prepare data for visualization (Customer ID vs Total Transaction Amount)
    data = {
        "CustomerIDs": df["customer_id"].tolist(),
        "TotalTransactionAmounts": df["total_transaction_amount"].tolist(),
    }
    return jsonify(data)

@app.route("/api/customer_details/<int:customer_id>", methods=["GET"])
def get_customer_details(customer_id):
    """Fetch customer details when clicking a pie chart section."""
    query = """
    SELECT first_name, last_name, email, age, job, marital, education, 
           subscribed_term_deposit, default_credit, personal_loan, state, annual_inc
    FROM customers
    WHERE customer_id = %s
    """
    df = pd.read_sql(query, engine, params=(customer_id,))

    if df.empty:
        return jsonify({"message": "Customer not found"}), 404

    data = df.to_dict(orient="records")[0]
    return jsonify(data)

# @app.route("/api/customer_insights", methods=["GET"])
# def get_customer_insights():
#     """Fetch customer insights for visualization."""
#     query = """
#     SELECT job, COUNT(*) AS count FROM customers GROUP BY job
#     UNION ALL
#     SELECT marital, COUNT(*) AS count FROM customers GROUP BY marital
#     UNION ALL
#     SELECT education, COUNT(*) AS count FROM customers GROUP BY education
#     """
#     df = pd.read_sql(query, engine)
#     return jsonify(df.to_dict(orient="records"))

@app.route("/api/customer_distribution/job", methods=["GET"])
def get_customer_distribution_by_job():
    """Fetch customer distribution by job."""
    query = """
    SELECT job, COUNT(*) AS count
    FROM customers
    GROUP BY job
    """
    df = pd.read_sql(query, engine)
    return jsonify(df.to_dict(orient="list"))

@app.route("/api/customer_distribution/marital", methods=["GET"])
def get_customer_distribution_by_marital():
    """Fetch customer distribution by marital status."""
    query = """
    SELECT marital, COUNT(*) AS count
    FROM customers
    GROUP BY marital
    """
    df = pd.read_sql(query, engine)
    return jsonify(df.to_dict(orient="list"))

@app.route("/api/customer_distribution/education", methods=["GET"])
def get_customer_distribution_by_education():
    """Fetch customer distribution by education."""
    query = """
    SELECT education, COUNT(*) AS count
    FROM customers
    GROUP BY education
    """
    df = pd.read_sql(query, engine)
    return jsonify(df.to_dict(orient="list"))

@app.route("/api/customers_by_category", methods=["GET"])
def get_customers_by_category():
    """Fetch customers by category when clicking on a chart section."""
    category_type = request.args.get("type")  # job, marital, education
    category_value = request.args.get("value")
    
    if category_type not in ["job", "marital", "education"]:
        return jsonify({"error": "Invalid category type"}), 400

    query = """
    SELECT first_name, last_name, email, age, job, marital, education, 
           subscribed_term_deposit, default_credit, personal_loan, state, annual_inc
    FROM customers
    WHERE {} = 'married'
""".format(category_type)
    
    #df = pd.read_sql(query, engine, params=[category_value])
    df = pd.read_sql(query, engine, params={"category_value": category_value})

    return jsonify(df.to_dict(orient="records"))

class Loan(db.Model):
    __tablename__ = 'loans'
    loan_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, nullable=False)
    loan_amnt = db.Column(db.Float, nullable=False)
    term = db.Column(db.String(50), nullable=False)
    int_rate = db.Column(db.Float, nullable=False)
    annual_inc = db.Column(db.Float, nullable=False)
    loan_status = db.Column(db.String(50), nullable=False)
    issue_date = db.Column(db.DateTime, nullable=False)

@app.route('/api/loan_distribution/amount')
def loan_distribution_amount():
    results = db.session.query(Loan.loan_amnt, db.func.count(Loan.loan_amnt)).group_by(Loan.loan_amnt).all()
    data = {"loan_amounts": [row[0] for row in results], "count": [row[1] for row in results]}
    return jsonify(data)

@app.route('/api/loan_distribution/term')
def loan_distribution_term():
    results = db.session.query(Loan.term, db.func.count(Loan.term)).group_by(Loan.term).all()
    data = {"terms": [row[0] for row in results], "count": [row[1] for row in results]}
    return jsonify(data)

@app.route('/api/loan_distribution/status')
def loan_distribution_status():
    results = db.session.query(Loan.loan_status, db.func.count(Loan.loan_status)).group_by(Loan.loan_status).all()
    data = {"statuses": [row[0] for row in results], "count": [row[1] for row in results]}
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
