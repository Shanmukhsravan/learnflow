import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import os

MODEL_PATH = "quiz_ai_model.pkl"
SCALER_PATH = "quiz_ai_scaler.pkl"

def train_quiz_ai():
    print("Training Quiz Evaluation AI...")
    
    # Generate synthetic training data
    # Features: [score_percentage, time_taken_seconds, difficulty_level (1-3)]
    # Target: 1 (Pass) or 0 (Fail)
    
    data = []
    
    for _ in range(2000):
        difficulty = np.random.choice([1, 2, 3])
        # Score ranges from 0 to 100
        score = np.random.uniform(0, 100)
        
        # Time taken: harder questions take longer. Average 60s per level.
        time_taken = np.random.uniform(10, 180 * difficulty)
        
        # Determine Pass/Fail based on logic that the model will try to learn:
        # Pass requires: High score AND reasonable time OR Perfect score despite long time
        # Higher difficulty means we are slightly more lenient on time
        
        passed = 0
        if score >= 80:
            passed = 1
        elif score >= 60 and time_taken < (60 * difficulty):
            passed = 1
        elif difficulty == 3 and score >= 50 and time_taken < 120:
            passed = 1
            
        data.append([score, time_taken, difficulty, passed])
        
    df = pd.DataFrame(data, columns=['score', 'time_taken', 'difficulty', 'passed'])
    
    X = df[['score', 'time_taken', 'difficulty']]
    y = df['passed']
    
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, classification_report
    
    # Split the dataset into 80% Training Data and 20% Testing Data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
    model.fit(X_train_scaled, y_train)
    
    # Calculate Accuracy on the highly-withheld 20% Testing Dataset
    predictions = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, predictions)
    
    print("\n==================================")
    print(f"🎯 Quiz Engine AI Model Accuracy: {accuracy * 100:.2f}%")
    print("==================================\n")
    print("Classification Report:")
    print(classification_report(y_test, predictions))
    
    joblib.dump(model, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    print("Quiz Evaluation AI trained and saved successfully.")

def check_model():
    if not os.path.exists(MODEL_PATH) or not os.path.exists(SCALER_PATH):
        train_quiz_ai()

def evaluate_performance(score_percentage, time_taken_sec, level):
    """
    Evaluates the student's performance using the trained AI model.
    Returns True if passed, False if failed.
    """
    check_model()
    
    try:
        model = joblib.load(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
        
        # Prepare input
        X_input = pd.DataFrame([[score_percentage, time_taken_sec, level]], 
                               columns=['score', 'time_taken', 'difficulty'])
        
        X_scaled = scaler.transform(X_input)
        
        prediction = model.predict(X_scaled)[0]
        return bool(prediction == 1)
        
    except Exception as e:
        print(f"AI Evaluation Error: {e}")
        # Fallback logic if model fails
        return score_percentage >= 60

if __name__ == "__main__":
    train_quiz_ai()
