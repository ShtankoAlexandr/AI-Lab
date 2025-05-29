import os
import re
import nltk
import pandas as pd
import mysql.connector
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
from dotenv import load_dotenv
import spacy
from collections import Counter

# Download necessary NLTK  and spacy resources
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('vader_lexicon')
nlp_spacy=spacy.load('en_core_web_trf')


# Initialize NLP tools
stop_words = set(stopwords.words('english'))
stemmer = PorterStemmer()
sia = SentimentIntensityAnalyzer()

# --- Text processing functions ---
def clean_text(text):
    """Lowercase and remove punctuation."""
    text = text.lower()
    return re.sub(r"[^\w\s]", "", text)

def tokenize(text):
    """Tokenize text into sentences and words."""
    return sent_tokenize(text), word_tokenize(text)

def remove_stopwords(words):
    """Remove common stopwords."""
    return [w for w in words if w not in stop_words]

def stem_words(words):
    """Apply stemming to reduce words to their base form."""
    return [stemmer.stem(w) for w in words]

def preprocess(text):
    """Full preprocessing pipeline."""
    text = clean_text(text)
    _, words = tokenize(text)
    words = remove_stopwords(words)
    words = stem_words(words)
    return " ".join(words)

def analyze_sentiment(text):
    """Return compound sentiment score (-1 to 1)."""
    score = sia.polarity_scores(text)
    return score['compound']

def extract_entities(text):
    """Extract entities"""
    doc=nlp_spacy(text)
    entities = [ent.text for ent in doc.ents  if ent.label_=='ORG']
    return ", ".join(list(Counter(entities)))



# --- Main execution ---
if __name__ == "__main__":
    load_dotenv()

    # Connect to the database
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

    query = "SELECT * FROM articles"
    df = pd.read_sql(query, conn)
    conn.close()

    # Save raw data
    df.to_csv("data/articles.csv", index=False)

    # Merge headline and body for analysis
    df["combined_text"] = df["Headline"].fillna("") + " " + df["Body"].fillna("")
    df["preprocessed_text"] = df["combined_text"].apply(preprocess)

    # Extract organizations
    df['Org']=df['combined_text'].apply(extract_entities)
    

    # Perform sentiment analysis on raw text
    df["Sentiment"] = df["combined_text"].apply(analyze_sentiment)
    

    # Bag-of-Words model for keyword frequency
    vectorizer = CountVectorizer()
    bow_matrix = vectorizer.fit_transform(df["preprocessed_text"])
    word_counts = bow_matrix.sum(axis=0)

    word_freq = [(word, word_counts[0, idx]) for word, idx in vectorizer.vocabulary_.items()]
    top_words = sorted(word_freq, key=lambda x: x[1], reverse=True)[:10]

    print("Top 10 words (after preprocessing):")
    for word, freq in top_words:  
        print(f"{word}: {freq}")

    df = df.drop('combined_text', axis=1)
    df = df.drop('preprocessed_text', axis=1)

    # Save enriched dataset
    df.to_csv("results/enhanced_news.csv", index=False, encoding="utf-8", mode='w')# mode w if file already exist
    print("NLP processing complete. Saved to results/enhanced_news.csv.")
