import pandas as pd
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import learning_curve
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
import numpy as np
import pickle
from sklearn.metrics import classification_report, accuracy_score
import logging
import time
from text_utils import preprocess  
import os

# --- Setup logging ---
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')

# --- Load training and test data ---
logging.info("Loading data...")
try:
    df_train = pd.read_csv("data/bbc_news_train.csv")
    df_test = pd.read_csv("data/bbc_news_tests.csv")  
except FileNotFoundError as e:
    logging.error(f"File not found: {str(e)}")
    exit(1)

# --- Preprocess text data with COMMON function ---
logging.info("Preprocessing training and test texts...")
X_train = df_train['Text'].apply(preprocess)
y_train = df_train['Category']
X_test = df_test['Text'].apply(preprocess)
y_test = df_test['Category']

# --- Define pipeline: TF-IDF 
pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(max_features=10000, ngram_range=(1, 2))),
    ("clf", LinearSVC(
    C=0.01,  # Decrease C for stronger regularization (was 0.1)
    class_weight='balanced',
    penalty='l2',  # Explicit L2 regularization
    max_iter=2000  # Ensure convergence
)
     
     
     )
])

# --- Train the classifier ---
logging.info("Training topic classifier...")
start_time = time.time()
pipeline.fit(X_train, y_train)
logging.info(f"Training completed in {time.time() - start_time:.2f} seconds.")

# --- Evaluate on test set ---
logging.info("Evaluating model on test set...")
y_pred = pipeline.predict(X_test)
acc = accuracy_score(y_test, y_pred)
logging.info(f"Test accuracy: {acc:.4f}")
logging.info("Classification report:\n" + classification_report(y_test, y_pred))

# --- Save the model and vectorizer ---
os.makedirs("results", exist_ok=True)
model_path = "results/topic_classifier.pkl"
with open(model_path, "wb") as f:
    pickle.dump(pipeline, f)
logging.info(f"Model saved to {model_path}")

# --- Save label encoder for mapping ---
from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
y_encoded = le.fit_transform(y_train)
label_mapping = dict(zip(le.classes_, le.transform(le.classes_)))
with open("results/label_encoder.pkl", "wb") as f:
    pickle.dump(label_mapping, f)
logging.info("Label mapping saved.")

# --- Generate learning curve ---
logging.info("Generating learning curves...")
train_sizes, train_scores, val_scores = learning_curve(
    pipeline, X_train, y_train, cv=5, scoring='accuracy',
    train_sizes=np.linspace(0.1, 1.0, 5),  
    n_jobs=-1
)

plt.figure(figsize=(10, 6))
plt.plot(train_sizes, np.mean(train_scores, axis=1), 'o-', label='Training accuracy')
plt.plot(train_sizes, np.mean(val_scores, axis=1), 'o-', label='Validation accuracy')
plt.xlabel('Training examples')
plt.ylabel('Accuracy')
plt.title('Learning Curves')
plt.legend()
plt.grid(True)
plot_path = "results/learning_curves.png"
plt.savefig(plot_path, dpi=150)
logging.info(f"Learning curve saved to {plot_path}")