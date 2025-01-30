from flask import Flask, render_template, jsonify
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import pickle

app = Flask(__name__)

# Load churn data
data = pd.read_csv('churn.csv')

# Preprocess data
le = LabelEncoder()
data['Status'] = le.fit_transform(data['Status'])  # Encode Status column (if categorical)

# Features and target
features = [
    'Call  Failure', 'Complains', 'Subscription  Length', 'Charge  Amount', 
    'Seconds of Use', 'Frequency of use', 'Frequency of SMS', 
    'Distinct Called Numbers', 'Age Group', 'Tariff Plan', 'Age', 'Customer Value'
]
X = data[features]
y = data['Churn']

# Split data into training and testing
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a classification model
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# Save the model
pickle.dump(model, open('churn_model.pkl', 'wb'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/predictions')
def get_predictions():
    # Load the trained model
    model = pickle.load(open('churn_model.pkl', 'rb'))
    # Predict on test data
    predictions = model.predict(X_test)
    results = pd.DataFrame({
        'Actual': y_test,
        'Predicted': predictions
    })
    return jsonify(results.to_dict(orient='records'))

@app.route('/api/summary')
def get_summary():
    summary = {
        'Total Customers': len(data),
        'Churned Customers': data['Churn'].sum(),
        'Retention Rate': (1 - data['Churn'].mean()) * 100,
    }
    return jsonify(summary)

@app.route('/api/charts')
def get_chart_data():
    # Data for visualizations
    churn_by_age = data.groupby('Age Group')['Churn'].mean()
    usage_by_churn = data.groupby('Churn')['Seconds of Use'].mean()
    avg_subscription_length = data.groupby('Churn')['Subscription  Length'].mean()

    chart_data = {
        'ChurnByAge': churn_by_age.to_dict(),
        'UsageByChurn': usage_by_churn.to_dict(),
        'SubscriptionByChurn': avg_subscription_length.to_dict()
    }
    return jsonify(chart_data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
