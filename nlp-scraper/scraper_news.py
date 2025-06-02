import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import re
import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Заголовки для имитации браузера
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Mobile Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
}

BASE_URL = 'https://www.bbc.co.uk'
SECTION_URL = 'https://www.bbc.co.uk/news/world'

def parse_article(url):
    try:
        r = requests.get(url, headers=HEADERS)
        if r.status_code != 200:
            return None, None
        soup = BeautifulSoup(r.text, 'html.parser')
        
        news_paragraphs = soup.select('p.ssrcss-1q0x1qg-Paragraph')
        
        def is_extraneous(text):
            extraneous_phrases = [
                "Follow the twists and turns",
                "This video can not be played",
                "Copyright",
                "The BBC is not responsible",
                "Read about our approach"
            ]
            if text.strip().startswith("Watch:"):
                return True
            for phrase in extraneous_phrases:
                if phrase in text:
                    return True
            return False
        
        filtered_paragraphs = [p.get_text() for p in news_paragraphs if not is_extraneous(p.get_text())]
        text = "\n".join(filtered_paragraphs).strip()
        if text == "":
            text = None

        pub_date = None
        time_tag = soup.find('time')
        if time_tag and time_tag.has_attr('datetime'):
            try:
                pub_date = datetime.fromisoformat(time_tag['datetime'].replace('Z', '+00:00'))
            except Exception:
                pub_date = None

        return text, pub_date
    except Exception as e:
        print("Ошибка при парсинге статьи:", e)
        return None, None

def get_articles_urls(page_num):
    url = f"{SECTION_URL}?page={page_num}"
    print(f"Парсинг страницы {page_num}: {url}")
    articles = []
    try:
        r = requests.get(url, headers=HEADERS)
        if r.status_code != 200:
            return []
        soup = BeautifulSoup(r.text, 'html.parser')
        promo_links = soup.select('a.ssrcss-5wtq5v-PromoLink, a.ssrcss-9haqql-LinkPostLink', )
        
        for idx, a in enumerate(promo_links, start=1):
            href = a.get('href')
            if href and '/news/articles/' in href:
                full_url = BASE_URL + href if href.startswith('/') else href
                print(f"{idx}. scraping {full_url}")
                print("    requesting ...")
                article_body, article_date = parse_article(full_url)
                print("    parsing ...")
                
                headline_tag = a.find('span', {'role': 'text'})
                if headline_tag:
                    headline = headline_tag.get_text(strip=True)
                else:
                    headline = a.get_text(strip=True)
                if headline.startswith("Watch:"):
                    headline = headline.replace("Watch:", "").strip()
                if "published at" in headline:
                    headline = headline.split("published at")[0].strip()
                
                article_id = href.split('/')[-1]
                saved_path = f"/articles/{article_id}.html"
                print(f"    saved in {saved_path}")
                
                articles.append((full_url, article_date, headline, article_body))
        return articles
    except Exception as e:
        print("Ошибка при получении URL:", e)
        return []

def main():
    load_dotenv()
    all_articles = []
    
    for page in range(1, 50):
        arts = get_articles_urls(page)
        if not arts:
            break
        all_articles.extend(arts)
        time.sleep(2)

    if all_articles:
        try:
            db_user = os.getenv('DB_USER')
            db_pass = os.getenv('DB_PASSWORD')
            db_host = os.getenv('DB_HOST')
            db_name = os.getenv('DB_NAME')

            # Создание подключения через SQLAlchemy
            engine = create_engine(f"mysql+pymysql://{db_user}:{db_pass}@{db_host}/{db_name}?charset=utf8mb4")

            df = pd.DataFrame(all_articles, columns=["URL", "Date_scraped", "Headline", "Body"])

            # Вставка с upsert
            with engine.begin() as conn:
                for _, row in df.iterrows():
                    stmt = text("""
                        INSERT INTO articles (URL, Date_scraped, Headline, Body)
                        VALUES (:url, :date, :headline, :body)
                        ON DUPLICATE KEY UPDATE Headline = VALUES(Headline), Body = VALUES(Body);
                    """)
                    conn.execute(stmt, {
                        "url": row.URL,
                        "date": row.Date_scraped,
                        "headline": row.Headline,
                        "body": row.Body
                    })

            print(f"✅ Обновлено {len(df)} записей.")
        except Exception as db_err:
            print("Ошибка при работе с БД через SQLAlchemy:", db_err)
    else:
        print("Нет новых данных для добавления.")

if __name__ == '__main__':
    main()
