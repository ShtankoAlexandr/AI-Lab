import os
import re
import nltk
import pandas as pd
from sqlalchemy import create_engine, text
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
from dotenv import load_dotenv
import spacy
from collections import Counter
import joblib
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim
import logging
import time


# --- Logging ---
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')

# --- Load resources ---
load_dotenv()
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('vader_lexicon')

logging.info("Loading models...")
nlp_spacy = spacy.load('en_core_web_trf')
model = joblib.load("results/topic_classifier.pkl")
sentence_transf_model = SentenceTransformer('all-MiniLM-L6-v2')

# Keywords
disaster_keywords = [
    "pollution", "deforestation", "toxic emissions", "chemical leakage", "oil spill",
    "industrial waste", "air pollution", "water contamination", "soil degradation",
    "illegal logging", "forest clearing", "habitat destruction", "overextraction",
    "water depletion", "land degradation", "ecosystem destruction", "biodiversity loss",
    "marine pollution", "greenhouse gas emissions", "carbon footprint", "methane leak"
]
keyword_embeddings = sentence_transf_model.encode(disaster_keywords, convert_to_tensor=True)
logging.info("Keyword embeddings generated.")


# --- NLP Tools ---
stop_words = set(stopwords.words('english'))
stemmer = PorterStemmer()
sia = SentimentIntensityAnalyzer()

# --- Text Processing Functions ---
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

def analyze_sentiment(text):
    return sia.polarity_scores(text)['compound']

def extract_entities(text):
    doc = nlp_spacy(text)
    entities = [ent.text for ent in doc.ents if ent.label_ == 'ORG']
    return ", ".join(list(Counter(entities)))

def compute_disaster_similarity(text, keyword_embeddings, model):
    sentences = sent_tokenize(text)
    sentence_embeddings = model.encode(sentences, convert_to_tensor=True)
    sim_matrix = cos_sim(sentence_embeddings, keyword_embeddings)
    max_sim_per_sentence = sim_matrix.max(dim=1).values
    return max_sim_per_sentence.mean().item()

# --- Main Execution ---
if __name__ == "__main__":
    start_time = time.time()

    logging.info("Connecting to database...")
    db_user = os.getenv("DB_USER")
    db_pass = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_name = os.getenv("DB_NAME")
    db_url = f"mysql+mysqlconnector://{db_user}:{db_pass}@{db_host}/{db_name}"
    engine = create_engine(db_url, echo=False)

    query = "SELECT * FROM articles"
    with engine.connect() as conn:
        df = pd.read_sql_query(text(query), conn)
    logging.info(f"Loaded {len(df)} records from DB.")

    df.to_csv("data/articles.csv", index=False)
    logging.info("Raw data saved to data/articles.csv.")

    df["combined_text"] = df["Headline"].fillna("") + " " + df["Body"].fillna("")
    df["preprocessed_text"] = df["combined_text"].apply(preprocess)
    logging.info("Text preprocessing completed.")

    # df["Org"] = df["combined_text"].apply(extract_entities)
    # logging.info("Organizations extracted.")

    df["Sentiment"] = df["combined_text"].apply(analyze_sentiment)
    logging.info("Sentiment analysis completed.")

    df["Topics"] = model.predict(df["preprocessed_text"])
    logging.info("Topic classification completed.")

    logging.info("Calculating disaster scores...")
    df["Disaster_Score"] = df["combined_text"].apply(
        lambda x: compute_disaster_similarity(x, keyword_embeddings, sentence_transf_model)
    )
    logging.info("Disaster similarity scoring completed.")

    vectorizer = CountVectorizer()
    bow_matrix = vectorizer.fit_transform(df["preprocessed_text"])
    word_counts = bow_matrix.sum(axis=0)
    word_freq = [(word, word_counts[0, idx]) for word, idx in vectorizer.vocabulary_.items()]
    top_words = sorted(word_freq, key=lambda x: x[1], reverse=True)[:10]

    logging.info("Top 10 words after preprocessing:")
    for word, freq in top_words:
        logging.info(f"{word}: {freq}")

    df.drop(['combined_text', 'preprocessed_text'], axis=1, inplace=True)
    df.to_csv("results/enhanced_news.csv", index=False, encoding="utf-8", mode='w')
    logging.info("NLP processing complete. Saved to results/enhanced_news.csv.")

    logging.info(f"Total execution time: {time.time() - start_time:.2f} seconds.")
 