# text_utils.py
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize, sent_tokenize

nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

stop_words = set(stopwords.words('english'))
stemmer = PorterStemmer()

def clean_text(text):
    return re.sub(r"[^\w\s]", "", text.lower())

def tokenize_words(text):
    return word_tokenize(text)

def remove_stopwords(words):
    return [w for w in words if w not in stop_words]

def stem_words(words):
    return [stemmer.stem(w) for w in words]

def preprocess(text):
    text = clean_text(text)
    words = tokenize_words(text)
    words = remove_stopwords(words)
    words = stem_words(words)
    return " ".join(words)