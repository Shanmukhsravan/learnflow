import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
import joblib
import os
from db import get_connection

MODEL_PATH = "course_recommender.pkl"

def get_all_courses():
    con = get_connection()
    cur = con.cursor(dictionary=True)
    cur.execute("SELECT * FROM courses")
    courses = cur.fetchall()
    con.close()
    return pd.DataFrame(courses)

def train_model():
    print("Fetching courses from database...")
    df = get_all_courses()
    
    if len(df) < 5:
        print("Not enough courses to train a meaningful model yet.")
        return False
        
    print(f"Training on {len(df)} courses...")
    
    # Fill NaN values to prevent TfidfVectorizer errors
    df.fillna('', inplace=True)
    
    # Feature 1: The 'Content' of the course (Title + Subject + Description + Level)
    # We combine them to let the TF-IDF vectorizer find text patterns
    df['content'] = df['title'] + " " + df['subject'] + " " + df['description'] + " " + df['level']
    
    # Since we don't have user click history (cold-start), we simulate training data.
    # We will train the Random Forest to understand which 'content' belongs to which 'subject'.
    # This allows it to learn the text patterns associated with the user's preferred subject.
    
    X = df['content']
    y = df['subject'] # The labels the model tries to predict
    
    # Create an ML Pipeline
    # 1. TfidfVectorizer: Converts text into a mathematical matrix of token counts
    # 2. RandomForestClassifier: An ensemble of decision trees to classify text into subjects
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(stop_words='english', max_features=1000)),
        ('rf', RandomForestClassifier(n_estimators=100, random_state=42))
    ])
    
    pipeline.fit(X, y)
    
    from sklearn.metrics import accuracy_score
    predictions = pipeline.predict(X)
    accuracy = accuracy_score(y, predictions)
    print("\n==================================")
    print(f"🎯 Course Recommender AI Training Accuracy: {accuracy * 100:.2f}%")
    print("==================================\n")
    
    # Save the trained model
    joblib.dump(pipeline, MODEL_PATH)
    print("Model trained and saved successfully.")
    return True

def get_recommendations(user_subject, top_n=3):
    # Load model if it exists, else train it
    if not os.path.exists(MODEL_PATH):
        success = train_model()
        if not success:
            return []
            
    try:
        model = joblib.load(MODEL_PATH)
    except:
        train_model()
        model = joblib.load(MODEL_PATH)

    df = get_all_courses()
    if df.empty:
        return []
        
    df.fillna('', inplace=True)
    df['content'] = df['title'] + " " + df['subject'] + " " + df['description'] + " " + df['level']
    
    # The user wants courses related to 'user_subject'. 
    # Our Random Forest was trained to predict the 'subject' from the text.
    # So we ask the model: "What is the probability that each course belongs to the user's subject?"
    
    # Get probability matrix for all classes
    probas = model.predict_proba(df['content'])
    
    # Find the column index that corresponds to the user's requested subject
    if user_subject in model.classes_:
        class_idx = np.where(model.classes_ == user_subject)[0][0]
        # Extract the probability that each course belongs to the requested subject
        course_probabilities = probas[:, class_idx]
    else:
        # If the subject is completely unknown to the model, fallback to text similarity scoring
        # (For this MVP, we just assign random probabilities to unknown subjects to avoid crashing)
        course_probabilities = np.random.rand(len(df))
        
    # Append scores to dataframe
    df['relevance_score'] = course_probabilities
    
    # Sort by the highest relevance score and take the Top N
    recommendations = df.sort_values(by='relevance_score', ascending=False).head(top_n)
    
    # Convert back to list of dictionaries for Flask
    return recommendations.to_dict('records')

if __name__ == "__main__":
    train_model()
