import os
import time
import logging
import pandas as pd
import nltk
import spacy
import joblib
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from collections import Counter
from nltk.tokenize import sent_tokenize
from nltk.sentiment import SentimentIntensityAnalyzer
from sentence_transformers import SentenceTransformer, util
from sklearn.feature_extraction.text import CountVectorizer
from text_utils import preprocess  # Ваша собственная функция предобработки

# --- Logging setup ---
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')

# --- Load environment variables ---
load_dotenv()

# --- Ensure required NLTK downloads ---
nltk.download('vader_lexicon', quiet=True)
nltk.download('punkt', quiet=True)

# --- Load SpaCy model ---
try:
    nlp_spacy = spacy.load('en_core_web_sm')
except:
    import spacy.cli
    spacy.cli.download('en_core_web_sm')
    nlp_spacy = spacy.load('en_core_web_sm')

# --- Load classification model ---
model_path = os.getenv("TOPIC_MODEL_PATH", "results/topic_classifier.pkl")
if not os.path.exists(model_path):
    logging.error(f"Topic classifier model not found at {model_path}.")
    exit(1)

model = joblib.load(model_path)

# --- Load embedding model ---
sentence_transf_model = SentenceTransformer('all-MiniLM-L6-v2')

# --- Disaster keywords ---
disaster_keywords = [
    "pollution", "deforestation", "toxic emissions", "chemical leakage", "oil spill",
    "industrial waste", "air pollution", "water contamination", "soil degradation",
    "illegal logging", "forest clearing", "habitat destruction", "overextraction",
    "water depletion", "land degradation", "ecosystem destruction", "biodiversity loss",
    "marine pollution", "greenhouse gas emissions", "carbon footprint", "methane leak"
]
keyword_embeddings = sentence_transf_model.encode(disaster_keywords, convert_to_tensor=True)
logging.info("Disaster keyword embeddings prepared.")

# --- Sentiment Analyzer ---
sia = SentimentIntensityAnalyzer()


# ---------- FUNCTIONS ----------

def analyze_sentiment(text):
    if not text.strip():
        return 0.0
    return sia.polarity_scores(text)['compound']


def extract_entities(text):
    if not text.strip():
        return ""
    doc = nlp_spacy(text[:1000000])
    entities = [ent.text for ent in doc.ents if ent.label_ == 'ORG']
    return ", ".join(list(Counter(entities)))


def compute_disaster_similarity(text, keyword_embeddings, transformer_model, max_sentences=10):
    if not text.strip():
        return 0.0
    sentences = sent_tokenize(text)[:max_sentences]
    if not sentences:
        return 0.0
    sentence_embeddings = transformer_model.encode(sentences, convert_to_tensor=True, show_progress_bar=False)
    sim_matrix = util.cos_sim(sentence_embeddings, keyword_embeddings)
    max_sim_per_sentence = sim_matrix.max(dim=1).values
    return max_sim_per_sentence.mean().item()


# ---------- MAIN EXECUTION ----------

def main():
    start_time = time.time()
    logging.info("Starting NLP pipeline...")

    # --- Connect to database ---
    db_user = os.getenv("DB_USER")
    db_pass = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_name = os.getenv("DB_NAME")

    if not all([db_user, db_pass, db_host, db_name]):
        logging.error("Missing DB credentials. Check your .env file.")
        exit(1)

    db_url = f"mysql+mysqlconnector://{db_user}:{db_pass}@{db_host}/{db_name}"
    engine = create_engine(db_url)

    try:
        with engine.connect() as conn:
            df = pd.read_sql(text("SELECT * FROM articles"), conn)
        logging.info(f"Loaded {len(df)} articles from the database.")
    except Exception as e:
        logging.error(f"Database error: {e}")
        exit(1)

    # --- Save raw data ---
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/articles.csv", index=False)
    logging.info("Saved raw data to data/articles.csv.")

    # --- Text cleanup ---
    df["Headline"] = df["Headline"].fillna("")
    df["Body"] = df["Body"].fillna("")
    df["combined_text"] = df["Headline"] + " " + df["Body"]

    # --- Remove duplicates ---
    df = df.drop_duplicates(subset=["combined_text"])
    logging.info(f"After removing duplicates: {len(df)} articles.")

    # --- Text preprocessing ---
    df["preprocessed_for_topics"] = df["combined_text"].apply(preprocess)
    logging.info("Text preprocessing complete.")

    # --- Extract organizations ---
    df["Org"] = df["combined_text"].apply(extract_entities)
    logging.info("Named entities extracted.")

    # --- Sentiment analysis ---
    df["Sentiment"] = df["combined_text"].apply(analyze_sentiment)
    logging.info("Sentiment analysis complete.")

    # --- Topic classification ---
    df["Topics"] = model.predict(df["preprocessed_for_topics"])
    logging.info("Topic classification complete.")

    # --- Disaster score ---
    df["Disaster_Score"] = df["combined_text"].apply(
        lambda x: compute_disaster_similarity(x, keyword_embeddings, sentence_transf_model)
    )
    logging.info("Disaster score computed.")

    # --- Top words ---
    vectorizer = CountVectorizer(max_features=1000)
    bow_matrix = vectorizer.fit_transform(df["preprocessed_for_topics"])
    word_counts = bow_matrix.sum(axis=0)
    word_freq = [(word, word_counts[0, idx]) for word, idx in vectorizer.vocabulary_.items()]
    top_words = sorted(word_freq, key=lambda x: x[1], reverse=True)[:10]

    logging.info("Top 10 frequent words:")
    for word, freq in top_words:
        logging.info(f"{word}: {freq}")

    # --- Save result ---
    os.makedirs("results", exist_ok=True)
    df.drop(['combined_text', 'preprocessed_for_topics'], axis=1).to_csv("results/enhanced_news.csv", index=False)
    logging.info("Final results saved to results/enhanced_news.csv.")

    # --- Final summary ---
    exec_time = time.time() - start_time
    logging.info(f"Execution time: {exec_time:.2f} sec, processed {len(df)} articles "
                 f"at {len(df)/exec_time:.2f} articles/sec.")


if __name__ == "__main__":
    main()
