import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import mysql.connector
import re
import pandas as pd
import os
from dotenv import load_dotenv

headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Mobile Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
}

base_url = 'https://www.bbc.co.uk'
section_url = 'https://www.bbc.co.uk/news/world'

# Глобальный счётчик ID
global_id_counter = 0

def parse_article(article_url):
    """Получаем тело статьи (текст) и дату публикации по URL."""
    try:
        response = requests.get(article_url, headers=headers)
        if response.status_code != 200:
            print(f"Не удалось получить статью {article_url}")
            return None, None
        soup = BeautifulSoup(response.text, 'html.parser')

        body = None

        # 1. Попытка получить тело статьи через основной селектор BBC
        paragraphs = soup.select('div.ssrcss-uf6wea-RichTextComponentWrapper p')
        if paragraphs:
            body = '\n'.join(p.get_text() for p in paragraphs).strip()

        # 2. Если не нашли, пытаемся из <article>
        if not body:
            article_tag = soup.find('article')
            if article_tag:
                ps = article_tag.find_all('p')
                if ps:
                    body = '\n'.join(p.get_text() for p in ps).strip()

        # 3. Если всё ещё нет текста — собираем все параграфы страницы
        if not body:
            ps = soup.find_all('p')
            if ps:
                body = '\n'.join(p.get_text() for p in ps).strip()

        if body == '':
            body = None

        # Поиск даты публикации
        pub_date = None

        # Из тега <time datetime="...">
        time_tag = soup.find('time')
        if time_tag and time_tag.has_attr('datetime'):
            try:
                pub_date = datetime.fromisoformat(time_tag['datetime'].replace('Z', '+00:00'))
            except Exception:
                pub_date = None

        # Из meta article:published_time
        if not pub_date:
            meta_time = soup.find('meta', attrs={'property': 'article:published_time'})
            if meta_time and meta_time.has_attr('content'):
                try:
                    pub_date = datetime.fromisoformat(meta_time['content'].replace('Z', '+00:00'))
                except Exception:
                    pub_date = None

        return body, pub_date

    except Exception as e:
        print(f"Ошибка при парсинге статьи: {e}")
        return None, None


def get_articles_urls(page_num):
    global global_id_counter

    url = f"{section_url}?page={page_num}"
    print(f"\nПарсинг страницы {page_num} — {url}")

    try:
        session = requests.Session()
        response = session.get(url=url, headers=headers)

        if response.status_code != 200:
            print(f"Страница {page_num} не найдена. Стоп.")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')

        promo_links = soup.select('a.ssrcss-5wtq5v-PromoLink, a.ssrcss-9haqql-LinkPostLink')
        if not promo_links:
            print(f"Нет новостей на странице {page_num}. Стоп.")
            return []

        art_data = []
        for a in promo_links:
            href = a.get('href')
            if href and '/news/articles/' in href:
                full_url = base_url + href if href.startswith('/') else href
                article_id = href.split('/')[-1]
                global_id_counter += 1

                headline_tag = a.find('h3') or a.find('p') or a
                headline = headline_tag.get_text(strip=True) if headline_tag else "No headline"

                # Попытка найти дату в анонсе
                pub_date = None
                time_tag = a.find_next('time', {'data-testid': 'timestamp'})
                if time_tag and time_tag.has_attr('datetime'):
                    try:
                        pub_date = datetime.fromisoformat(time_tag['datetime'].replace('Z', '+00:00'))
                    except Exception:
                        pub_date = None
                else:
                    date_span = a.find_next('span', class_='visually-hidden')
                    if date_span:
                        date_text = date_span.get_text(strip=True)
                        match = re.search(r'(\d{1,2}:\d{2})\s(\d{1,2}\s\w+)', date_text)
                        if match:
                            try:
                                date_str = f"{match.group(1)} {match.group(2)}"
                                pub_date = datetime.strptime(date_str, "%H:%M %d %B")
                                pub_date = pub_date.replace(year=datetime.now().year)
                            except Exception:
                                pub_date = None

                # Если даты нет — получить из статьи
                body, pub_date_article = parse_article(full_url)
                if pub_date is None:
                    pub_date = pub_date_article

                print(f"ID{global_id_counter}: {article_id}")
                print(f"URL: {full_url}")
                print(f"Headline: {headline}")
                print(f"Published date (approx): {pub_date}")
                print(f"Body preview: {body[:200] if body else 'None'}...\n")

                art_data.append((full_url, pub_date, headline, body))

        return art_data

    except Exception as e:
        print(f"Ошибка при получении данных: {e}")
        return []


def main():
    page = 1
    all_data = []

    while True:
        articles = get_articles_urls(page)
        if not articles:
            break
        all_data.extend(articles)
        time.sleep(2)  # задержка между запросами
        page += 1
        if page > 16:  # ограничение по количеству страниц
            break

    if all_data:
        try:
            load_dotenv()
            conn = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
            )
            insert_query = """
            INSERT INTO articles (URL, dateOfPubl, headline, body)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE headline = VALUES(headline), body = VALUES(body);
            """
            cursor = conn.cursor()
            cursor.executemany(insert_query, all_data)
            conn.commit()
            print(f"\n✅ Уникальные статьи добавлены или обновлены: {len(all_data)} записей.")
            cursor.close()
            conn.close()
        except mysql.connector.Error as db_err:
            print(f"Ошибка при работе с базой данных: {db_err}")
    else:
        print("⚠️ Нет новых данных для добавления.")


if __name__ == '__main__':
    main()
