import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import mysql.connector
import re
import os
from dotenv import load_dotenv

# Заголовки для имитации браузера
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Mobile Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
}

BASE_URL = 'https://www.bbc.co.uk'
SECTION_URL = 'https://www.bbc.co.uk/news/world'

def parse_article(url):
    """Извлекает текст статьи и дату публикации,
    используя только параграфы с классом 'ssrcss-1q0x1qg-Paragraph',
    исключая нежелательные фразы."""
    try:
        r = requests.get(url, headers=HEADERS)
        if r.status_code != 200:
            return None, None
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Извлечение только параграфов с указанным классом
        news_paragraphs = soup.select('p.ssrcss-1q0x1qg-Paragraph')
        
        def is_extraneous(text):
            extraneous_phrases = [
                "Follow the twists and turns",  # информация о бюллетене
                "This video can not be played",  # сообщение, что видео не воспроизводится
                "Copyright",
                "The BBC is not responsible",
                "Read about our approach"
            ]
            # Если абзац начинается с "Watch:" — считаем его лишним
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

        # Извлечение даты публикации
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
    """Парсит страницу с новостями и возвращает информацию об актуальных статьях."""
    url = f"{SECTION_URL}?page={page_num}"
    print(f"Парсинг страницы {page_num}: {url}")
    articles = []
    try:
        r = requests.get(url, headers=HEADERS)
        if r.status_code != 200:
            return []
        soup = BeautifulSoup(r.text, 'html.parser')
        promo_links = soup.select('a.ssrcss-5wtq5v-PromoLink, a.ssrcss-9haqql-LinkPostLink')
        
        for idx, a in enumerate(promo_links, start=1):
            href = a.get('href')
            if href and '/news/articles/' in href:
                full_url = BASE_URL + href if href.startswith('/') else href

                # Вывод логов для этого URL:
                print(f"{idx}. scraping {full_url}")
                print("    requesting ...")
                # Получаем данные из статьи – тут происходит запрос:
                article_body, article_date = parse_article(full_url)
                print("    parsing ...")
                
                # Извлечение заголовка через <span role="text">
                headline_tag = a.find('span', {'role': 'text'})
                if headline_tag:
                    headline = headline_tag.get_text(strip=True)
                else:
                    headline = a.get_text(strip=True)
                # Удаляем префикс "Watch:" и лишний текст с "published at"
                if headline.startswith("Watch:"):
                    headline = headline.replace("Watch:", "").strip()
                if "published at" in headline:
                    headline = headline.split("published at")[0].strip()
                
                # Генерируем путь, куда "сохранился" URL — используем последний сегмент как идентификатор
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
    # Обрабатываем страницы с 1 по 50
    for page in range(1, 50):
        arts = get_articles_urls(page)
        if not arts:
            break
        all_articles.extend(arts)
        time.sleep(2)
    if all_articles:
        try:
            conn = mysql.connector.connect(
                host=os.getenv('DB_HOST'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                database=os.getenv('DB_NAME')
            )
            query = """
            INSERT INTO articles (URL, Date_scraped, Headline, Body)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE headline = VALUES(Headline), body = VALUES(Body);
            """
            cursor = conn.cursor()
            cursor.executemany(query, all_articles)
            conn.commit()
            print(f"✅ Обновлено {len(all_articles)} записей.")
            cursor.close()
            conn.close()
        except mysql.connector.Error as db_err:
            print("Ошибка БД:", db_err)
    else:
        print("Нет новых данных для добавления.")

if __name__ == '__main__':
    main()