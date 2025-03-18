import spacy
import pandas as pd
import joblib
from nltk.sentiment import SentimentIntensityAnalyzer
import requests
from bs4 import BeautifulSoup

def check_libraries():
    try:
        # Проверка spaCy
        spacy.load("en_core_web_sm")
        print("spaCy успешно загружен")

        # Проверка pandas
        pd.DataFrame({"test": [1, 2, 3]})
        print("pandas успешно загружен")

        # Проверка joblib
        joblib.dump([1, 2, 3], 'test.pkl')
        joblib.load('test.pkl')
        print("joblib успешно загружен")

        # Проверка SentimentIntensityAnalyzer
        sia = SentimentIntensityAnalyzer()
        print("nltk SentimentIntensityAnalyzer успешно загружен")

        # Проверка requests
        response = requests.get('https://example.com')
        print("requests успешно загружен")

        # Проверка BeautifulSoup
        response = requests.get('https://example.com')
        soup = BeautifulSoup(response.text, 'html.parser')
        print("BeautifulSoup успешно загружен")

    except Exception as e:
        print(f"Ошибка при загрузке библиотеки: {e}")

if __name__ == "__main__":
    check_libraries()
