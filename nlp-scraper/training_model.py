import pandas as pd
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import learning_curve
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import numpy as np
import pickle
from sklearn.metrics import classification_report, accuracy_score
import re
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import nltk
import logging
import time

# --- Setup logging ---
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')

# --- Download NLTK resources ---
logging.info("Downloading NLTK resources...")
nltk.download('punkt')
nltk.download('stopwords')

# --- Text preprocessing setup ---
stop_words = set(stopwords.words('english'))
stemmer = PorterStemmer()

def clean_text(text):
    return re.sub(r"[^\w\s]", "", text.lower())

def tokenize(text):
    return sent_tokenize(text), word_tokenize(text)

def remove_stopwords(words):
    return [w for w in words if w not in stop_words]

def stem_words(words):
    return [stemmer.stem(w) for w in words]

def preprocess(text):
    text = clean_text(text)
    _, words = tokenize(text)
    words = remove_stopwords(words)
    words = stem_words(words)
    return " ".join(words)

# --- Load training and test data ---
logging.info("Loading data...")
df_train = pd.read_csv("data/bbc_news_train.csv")
df_test = pd.read_csv("data/bbc_news_tests.csv")

# --- Preprocess text data ---
logging.info("Preprocessing training and test texts...")
X_train = df_train['Text'].apply(preprocess)
y_train = df_train['Category']
X_test = df_test['Text'].apply(preprocess)
y_test = df_test['Category']

# --- Define pipeline: TF-IDF + Naive Bayes ---
pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(max_features=10000)),
    ("clf", MultinomialNB())
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

# --- Save the model to disk ---
model_path = "results/topic_classifier.pkl"
with open(model_path, "wb") as f:
    pickle.dump(pipeline, f)
logging.info(f"Model saved to {model_path}")

# --- Generate and save learning curve plot ---
logging.info("Generating learning curves...")
train_sizes, train_scores, val_scores = learning_curve(
    pipeline, X_train, y_train, cv=5, scoring='accuracy',
    train_sizes=np.linspace(0.1, 1.0, 10)
)

plt.figure(figsize=(8,6))
plt.plot(train_sizes, np.mean(train_scores, axis=1), label='Training accuracy')
plt.plot(train_sizes, np.mean(val_scores, axis=1), label='Validation accuracy')
plt.xlabel('Training size')
plt.ylabel('Accuracy')
plt.title('Learning Curves')
plt.legend()
plt.grid(True)
plot_path = "results/learning_curves.png"
plt.savefig(plot_path)
plt.show()
logging.info(f"Learning curve saved to {plot_path}")
