from flask import Flask, render_template, request, jsonify
import numpy as np
import pickle
import os
import csv
import io
from sklearn.ensemble import RandomForestClassifier

app = Flask(__name__)

# Train a simple Titanic survival model on synthetic data
# In production, you'd use the real Titanic dataset
def train_model():
    # Synthetic training data based on Titanic patterns
    np.random.seed(42)
    n_samples = 1000
    
    # Features: Pclass, Sex, Age, SibSp, Parch, Fare, Embarked
    pclass = np.random.choice([1, 2, 3], n_samples)
    sex = np.random.choice([0, 1], n_samples)  # 0=female, 1=male
    age = np.random.normal(30, 14, n_samples).clip(0, 80)
    sibsp = np.random.choice([0, 1, 2, 3, 4, 5, 8], n_samples, p=[0.68, 0.23, 0.03, 0.02, 0.02, 0.01, 0.01])
    parch = np.random.choice([0, 1, 2, 3, 4, 5, 6], n_samples, p=[0.76, 0.13, 0.09, 0.01, 0.004, 0.003, 0.003])
    fare = np.random.exponential(32, n_samples).clip(0, 500)
    embarked = np.random.choice([0, 1, 2], n_samples, p=[0.72, 0.19, 0.09])  # S, C, Q
    
    # Create survival target based on known Titanic patterns
    survival_score = (
        (2 - pclass) * 0.3 +          # Higher class = better survival
        (1 - sex) * 0.4 +              # Female = better survival
        (age < 16) * 0.2 +             # Children = better survival
        (fare > 50) * 0.1 -            # Higher fare = slightly better
        (age > 60) * 0.1               # Elderly = worse survival
    )
    survived = (survival_score + np.random.normal(0, 0.1, n_samples) > 0.4).astype(int)
    
    X = np.column_stack([pclass, sex, age, sibsp, parch, fare, embarked])
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, survived)
    return model

# Ensure directories exist
os.makedirs('model', exist_ok=True)
os.makedirs('data', exist_ok=True)

# Load or train model
model_path = os.path.join('model', 'titanic_model.pkl')
if os.path.exists(model_path):
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
else:
    model = train_model()
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    
    pclass = int(data.get('pclass', 3))
    sex = 1 if data.get('sex', 'male') == 'male' else 0
    age = float(data.get('age', 30))
    sibsp = int(data.get('sibsp', 0))
    parch = int(data.get('parch', 0))
    fare = float(data.get('fare', 32))
    embarked = data.get('embarked', 'S')
    embarked_map = {'S': 0, 'C': 1, 'Q': 2}
    embarked_code = embarked_map.get(embarked, 0)
    
    features = np.array([[pclass, sex, age, sibsp, parch, fare, embarked_code]])
    
    prediction = model.predict(features)[0]
    probability = model.predict_proba(features)[0]
    
    survival_prob = float(probability[1]) * 100
    
    # Determine risk level
    if survival_prob >= 70:
        risk_level = "Low Risk"
        risk_color = "green"
    elif survival_prob >= 40:
        risk_level = "Medium Risk"
        risk_color = "orange"
    else:
        risk_level = "High Risk"
        risk_color = "red"
    
    return jsonify({
        'survived': bool(prediction),
        'survival_probability': round(survival_prob, 2),
        'risk_level': risk_level,
        'risk_color': risk_color,
        'message': f"Survival Probability: {round(survival_prob, 2)}%"
    })

def get_risk_info(prob):
    if prob >= 70:
        return "Low Risk", "green"
    elif prob >= 40:
        return "Medium Risk", "orange"
    else:
        return "High Risk", "red"

@app.route('/predict_csv', methods=['POST'])
def predict_csv():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '' or not file.filename.endswith('.csv'):
        return jsonify({'error': 'Please upload a valid CSV file'}), 400
    
    try:
        stream = io.StringIO(file.stream.read().decode('utf-8'))
        reader = csv.DictReader(stream)
        
        results = []
        for row in reader:
            try:
                pclass = int(row.get('Pclass', row.get('pclass', 3)))
                sex_val = row.get('Sex', row.get('sex', 'male')).lower()
                sex = 1 if sex_val == 'male' else 0
                age = float(row.get('Age', row.get('age', 30)))
                sibsp = int(row.get('SibSp', row.get('sibsp', 0)))
                parch = int(row.get('Parch', row.get('parch', 0)))
                fare = float(row.get('Fare', row.get('fare', 32)))
                embarked = row.get('Embarked', row.get('embarked', 'S'))
                embarked_map = {'S': 0, 'C': 1, 'Q': 2}
                embarked_code = embarked_map.get(embarked, 0)
                
                features = np.array([[pclass, sex, age, sibsp, parch, fare, embarked_code]])
                prediction = model.predict(features)[0]
                probability = model.predict_proba(features)[0]
                survival_prob = float(probability[1]) * 100
                risk_level, risk_color = get_risk_info(survival_prob)
                
                results.append({
                    'pclass': pclass,
                    'sex': 'Male' if sex == 1 else 'Female',
                    'age': age,
                    'sibsp': sibsp,
                    'parch': parch,
                    'fare': fare,
                    'embarked': embarked,
                    'survived': bool(prediction),
                    'survival_probability': round(survival_prob, 2),
                    'risk_level': risk_level,
                    'risk_color': risk_color
                })
            except (ValueError, KeyError) as e:
                continue
        
        if not results:
            return jsonify({'error': 'No valid data found in CSV. Ensure columns: Pclass, Sex, Age, SibSp, Parch, Fare, Embarked'}), 400
        
        return jsonify({'results': results})
        
    except Exception as e:
        return jsonify({'error': f'Error processing CSV: {str(e)}'}), 500

@app.route('/api/folders')
def get_folders():
    """Return project folder structure for sidebar"""
    return jsonify({
        'name': 'Titanic Prediction',
        'type': 'root',
        'children': [
            {
                'name': 'backend',
                'type': 'folder',
                'children': [
                    {'name': 'app.py', 'type': 'file'},
                    {'name': 'model', 'type': 'folder', 'children': [
                        {'name': 'titanic_model.pkl', 'type': 'file'}
                    ]},
                    {'name': 'data', 'type': 'folder', 'children': [
                        {'name': 'train.csv', 'type': 'file'},
                        {'name': 'test.csv', 'type': 'file'}
                    ]}
                ]
            },
            {
                'name': 'frontend',
                'type': 'folder',
                'children': [
                    {'name': 'index.html', 'type': 'file'},
                    {'name': 'css', 'type': 'folder', 'children': [
                        {'name': 'style.css', 'type': 'file'}
                    ]},
                    {'name': 'js', 'type': 'folder', 'children': [
                        {'name': 'main.js', 'type': 'file'}
                    ]},
                    {'name': 'images', 'type': 'folder', 'children': [
                        {'name': 'titanic.jpg', 'type': 'file'}
                    ]}
                ]
            },
            {
                'name': 'templates',
                'type': 'folder',
                'children': [
                    {'name': 'index.html', 'type': 'file'}
                ]
            },
            {
                'name': 'static',
                'type': 'folder',
                'children': [
                    {'name': 'css', 'type': 'folder', 'children': [
                        {'name': 'style.css', 'type': 'file'}
                    ]},
                    {'name': 'js', 'type': 'folder', 'children': [
                        {'name': 'main.js', 'type': 'file'}
                    ]},
                    {'name': 'images', 'type': 'folder', 'children': [
                        {'name': 'titanic.jpg', 'type': 'file'}
                    ]}
                ]
            },
            {'name': 'requirements.txt', 'type': 'file'},
            {'name': 'README.md', 'type': 'file'}
        ]
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
