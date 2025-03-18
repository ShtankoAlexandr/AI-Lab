# Тестовый файл для проверки библиотек с MySQL
def check_library(library_name, import_statement, pip_name=None):
    """Проверка импорта библиотеки"""
    try:
        exec(import_statement)
        print(f"✓ {library_name} успешно загружена")
        return True
    except ImportError:
        print(f"✗ Ошибка: {library_name} не установлена")
        print(f"   Установите с помощью: pip install {pip_name or library_name.lower()}")
        return False
    except Exception as e:
        print(f"✗ Ошибка при загрузке {library_name}: {str(e)}")
        return False

def check_nltk_resources():
    """Проверка ресурсов NLTK"""
    import nltk
    resources = {
        'punkt': 'Токенизатор пунктуации',
        'stopwords': 'Список стоп-слов'
    }
    all_good = True
    
    for resource, description in resources.items():
        try:
            nltk.data.find(f'tokenizers/{resource}' if resource == 'punkt' else f'corpora/{resource}')
            print(f"✓ NLTK ресурс '{description}' доступен")
        except LookupError:
            print(f"✗ NLTK ресурс '{description}' не найден")
            print(f"   Загрузите с помощью: nltk.download('{resource}')")
            all_good = False
    return all_good

def check_mysql_connection():
    """Проверка подключения к MySQL"""
    try:
        import mysql.connector
        import os
        from dotenv import load_dotenv

        load_dotenv()
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            user=os.getenv('DB_USER'),        
            password=os.getenv('DB_PASSWORD'),  
            database=os.getenv('DB_NAME')  
        )
        conn.close()
        print("✓ Подключение к MySQL успешно")
        return True
    except mysql.connector.Error as e:
        print(f"✗ Ошибка подключения к MySQL: {str(e)}")
        print("   Убедитесь, что MySQL сервер запущен и параметры верны")
        return False
    except ImportError:
        print("✗ MySQL Connector не установлен")
        return False

def run_tests():
    """Основная функция для выполнения всех проверок"""
    print("Проверка необходимых библиотек...\n")
    
    # Список проверок, включая mysql.connector
    checks = [
        ("Requests", "import requests"),
        ("BeautifulSoup", "from bs4 import BeautifulSoup", "beautifulsoup4"),
        ("Pandas", "import pandas as pd"),
        ("NLTK", "import nltk"),
        ("NLTK.tokenize", "from nltk.tokenize import word_tokenize, sent_tokenize"),
        ("NLTK.corpus", "from nltk.corpus import stopwords"),
        ("NLTK.stem", "from nltk.stem import PorterStemmer"),
        ("Scikit-learn CountVectorizer", "from sklearn.feature_extraction.text import CountVectorizer", "scikit-learn"),
        ("Regular Expressions (re)", "import re"),
        ("MySQL Connector", "import mysql.connector", "mysql-connector-python"),  # Добавлено здесь
        ("Datetime", "from datetime import datetime, timedelta"),
        ("UUID", "import uuid")
    ]
    
    all_libraries_good = True
    
    # Проверка всех библиотек
    for name, statement, *pip_name in checks:
        pip = pip_name[0] if pip_name else None
        if not check_library(name, statement, pip):
            all_libraries_good = False
    
    # Проверка ресурсов NLTK
    if all_libraries_good:
        print("\nПроверка ресурсов NLTK...")
        if not check_nltk_resources():
            all_libraries_good = False
    
    # Проверка подключения к MySQL
    if all_libraries_good:
        print("\nПроверка подключения к базе данных...")
        if not check_mysql_connection():
            all_libraries_good = False
    
    # Итоговый результат
    print("\n" + "="*50)
    if all_libraries_good:
        print("✓ Все библиотеки, ресурсы и подключение к MySQL готовы к работе!")
    else:
        print("✗ Некоторые компоненты отсутствуют. Установите их перед началом работы.")

if __name__ == "__main__":
    run_tests()