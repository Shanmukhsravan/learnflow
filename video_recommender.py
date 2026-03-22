import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import os

MODEL_PATH = "video_recommender.pkl"
VECTORIZER_PATH = "video_vectorizer.pkl"
VIDEO_DATA_PATH = "video_catalog.pkl"

# A synthetic catalog of educational videos
VIDEO_CATALOG = [
    # Computer Science Videos
    {
        "id": 101,
        "title": "Computer Hardware Basics: CPU, RAM, and Storage",
        "description": "Learn about central processing units, memory, random access memory, hard drives, and how the brain of the computer works.",
        "url": "https://www.youtube.com/watch?v=ExxezPlOUyQ",
        "course_id": 1 # Assuming 1 is CS
    },
    {
        "id": 102,
        "title": "Operating Systems Explained",
        "description": "Find out what an operating system is, how it manages hardware resources, Windows, Linux, macOS, networking.",
        "url": "https://www.youtube.com/watch?v=vBURTt97EkA",
        "course_id": 1
    },
    {
        "id": 103,
        "title": "Data Structures: Arrays, Linked Lists, Stacks, Queues",
        "description": "Deep dive into nodes, memory allocation, LIFO stacks, FIFO queues, and basic data structures.",
        "url": "https://www.youtube.com/watch?v=bum_19loj9A",
        "course_id": 1
    },
    {
        "id": 104,
        "title": "Algorithms & Time Complexity (Big O)",
        "description": "Understand O(n), O(log n), binary search, merge sort, bubble sort, and efficient logic.",
        "url": "https://www.youtube.com/watch?v=D6xkbGLQesk",
        "course_id": 1
    },
    {
        "id": 105,
        "title": "Database Fundamentals: SQL vs NoSQL",
        "description": "Structured Query Language, primary keys, MongoDB, PostgreSQL, relational vs non-relational mapping.",
        "url": "https://www.youtube.com/watch?v=ztHopE5Wnpc",
        "course_id": 1
    },
    {
        "id": 106,
        "title": "Object Oriented Programming (OOP)",
        "description": "Learn encapsulation, inheritance, polymorphism, classes, and abstraction.",
        "url": "https://www.youtube.com/watch?v=pTB0EiLXUC8",
        "course_id": 1
    },
    {
        "id": 107,
        "title": "Advanced Operating Systems & Concurrency",
        "description": "Mutex, semaphores, deadlock, race conditions, threads vs processes, virtual memory.",
        "url": "https://www.youtube.com/watch?v=olQjWEHn4rI",
        "course_id": 1
    },

    # Data Science Videos
    {
        "id": 201,
        "title": "Python Data Manipulation with Pandas",
        "description": "CSV files, formatting, dataframes, categorical variables, and data cleaning.",
        "url": "https://www.youtube.com/watch?v=vmEHCJofslg",
        "course_id": 2 # Assuming 2 is DS
    },
    {
        "id": 202,
        "title": "Statistics for Data Science",
        "description": "Mean, median, mode, correlation coefficient, outliers, variance.",
        "url": "https://www.youtube.com/watch?v=xxpc-HPKN28",
        "course_id": 2
    },
    {
        "id": 203,
        "title": "Machine Learning: Classification & Regression",
        "description": "Logistic regression, linear regression, predicting continuous values, cross-validation.",
        "url": "https://www.youtube.com/watch?v=RNwIAH1D0H0",
        "course_id": 2
    },
    {
        "id": 204,
        "title": "Feature Engineering & Scaling",
        "description": "MinMaxScaler, StandardScaler, converting raw data into ML inputs.",
        "url": "https://www.youtube.com/watch?v=U3jE2-x_SgM",
        "course_id": 2
    },
    {
        "id": 205,
        "title": "Advanced ML: PCA and Dimensionality Reduction",
        "description": "Principal Component Analysis, curse of dimensionality, unsupervised learning.",
        "url": "https://www.youtube.com/watch?v=FgakZw6K1QQ",
        "course_id": 2
    },
    {
        "id": 206,
        "title": "Ensemble Methods: Random Forest & SVM",
        "description": "Combining models, kernel trick, hyperplane, support vector machines, decision trees.",
        "url": "https://www.youtube.com/watch?v=J4Wdy0Wc_xQ",
        "course_id": 2
    },

    # Business Videos
    {
        "id": 301,
        "title": "Business Fundamentals: Revenue & ROI",
        "description": "Return on investment, maximizing shareholder value, basic accounting principles.",
        "url": "https://www.youtube.com/watch?v=Ima_vIt6X8c",
        "course_id": 3 # Assuming 3 is Business
    },
    {
        "id": 302,
        "title": "Marketing to Your Target Market",
        "description": "B2B, B2C, target market identification, unique selling proposition (USP).",
        "url": "https://www.youtube.com/watch?v=tP2uN2L2Y3U",
        "course_id": 3
    },
    {
        "id": 303,
        "title": "Financial Metrics: KPI, LTV, and CAC",
        "description": "Key performance indicators, lifetime value, customer acquisition cost, break-even point.",
        "url": "https://www.youtube.com/watch?v=W3fRzBv2wEE",
        "course_id": 3
    },
    {
        "id": 304,
        "title": "Agile & Lean Startup Methodology",
        "description": "Minimum viable product (MVP), iterative approach, validated learning, venture capital.",
        "url": "https://www.youtube.com/watch?v=fEvM-OUbaKs",
        "course_id": 3
    },
    {
        "id": 305,
        "title": "Strategic Business Moves: Blue Ocean & Six Sigma",
        "description": "Reducing defects, eliminating competition, vertical integration.",
        "url": "https://www.youtube.com/watch?v=r0bICw8sKqY",
        "course_id": 3
    },

    # AI Videos
    {
        "id": 401,
        "title": "Introduction to Neural Networks",
        "description": "Machine learning, nodes, dataset, activation functions, loss functions.",
        "url": "https://www.youtube.com/watch?v=aircAruvnKk",
        "course_id": 4 # Assuming 4 is AI
    },
    {
        "id": 402,
        "title": "Deep Learning: Epochs, Dropout & Overfitting",
        "description": "Preventing overfitting, memorizing training data, epochs, tensors, TensorFlow.",
        "url": "https://www.youtube.com/watch?v=p66VDVKb_gI",
        "course_id": 4
    },
    {
        "id": 403,
        "title": "Convolutional Neural Networks (CNN) for Images",
        "description": "Downsampling, pooling, computer vision, identifying patterns in pictures.",
        "url": "https://www.youtube.com/watch?v=YRhxdVk_sIs",
        "course_id": 4
    },
    {
        "id": 404,
        "title": "Natural Language Processing (NLP) & Transformers",
        "description": "BERT, Attention is All You Need, handling textual data, RNNs.",
        "url": "https://www.youtube.com/watch?v=zxQyTK8quyY",
        "course_id": 4
    },
    {
        "id": 405,
        "title": "Advanced AI: GANs, Backpropagation, and Reinforcement Learning",
        "description": "Generative adversarial networks, chain rule, exploding gradient, interacting with environment.",
        "url": "https://www.youtube.com/watch?v=Ilg3gGewQ5U",
        "course_id": 4
    }
]

def train_recommender():
    """
    Trains a simple Content-Based Filtering Recommender using TF-IDF and Cosine Similarity.
    """
    print("Training Video Recommender Engine...")
    df = pd.DataFrame(VIDEO_CATALOG)
    
    # Text data representing the video content
    df['content'] = df['title'] + " " + df['description']
    
    # Initialize TF-IDF Vectorizer
    vectorizer = TfidfVectorizer(stop_words='english')
    
    # Fit and transform the video text into a mathematical matrix
    tfidf_matrix = vectorizer.fit_transform(df['content'])
    
    # Save the vectorizer and matrix for later use
    joblib.dump(vectorizer, VECTORIZER_PATH)
    joblib.dump(tfidf_matrix, MODEL_PATH)
    df.to_pickle(VIDEO_DATA_PATH)
    
    print("Video Recommender trained and saved.")

def get_video_recommendation_for_question(failed_question_text):
    """
    Given the text of a question the user failed, this function predicts 
    which video is most relevant.
    """
    if not os.path.exists(MODEL_PATH) or not os.path.exists(VECTORIZER_PATH):
        train_recommender()
        
    vectorizer = joblib.load(VECTORIZER_PATH)
    tfidf_matrix = joblib.load(MODEL_PATH)
    df = pd.read_pickle(VIDEO_DATA_PATH)
    
    # Transform the failed question into the same vector space
    question_vec = vectorizer.transform([failed_question_text])
    
    # Calculate cosine similarity between the question and all videos
    # Computes how close the question's text matches the video's title+description
    similarities = cosine_similarity(question_vec, tfidf_matrix).flatten()
    
    # Find the index of the highest similarity score
    best_match_idx = similarities.argmax()
    
    # Check if there is a meaningful match (similarity > 0)
    if similarities[best_match_idx] > 0.05:
        best_video = df.iloc[best_match_idx]
        return {
            "title": best_video["title"],
            "url": best_video["url"],
            "course_id": int(best_video["course_id"])
        }
    else:
        # Fallback to a generic recommendation if no strong match is found
        return {
            "title": "General Learning Strategies",
            "url": "https://www.youtube.com/watch?v=1",
            "course_id": 1 
        }

if __name__ == "__main__":
    train_recommender()
    
    # Quick Test
    test_q = "What does CPU stand for?"
    print(f"Testing for question: '{test_q}'")
    print("Recommendation:", get_video_recommendation_for_question(test_q))
