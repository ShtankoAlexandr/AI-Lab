import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime

headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Mobile Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
}

base_url = 'https://www.bbc.co.uk'
section_url = 'https://www.bbc.co.uk/news/world'

# Глобальный счётчик ID
global_id_counter = 0

def parse_article(article_url):
    """Получаем тело статьи (текст) по URL."""
    response = requests.get(article_url, headers=headers)
    if response.status_code != 200:
        print(f"Не удалось получить статью {article_url}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    paragraphs = soup.select('div.ssrcss-uf6wea-RichTextComponentWrapper p')
    body = '\n'.join(p.get_text() for p in paragraphs)
    return body.strip()

def get_articles_urls(page_num):
    global global_id_counter  # используем глобальную переменную

    url = f"{section_url}?page={page_num}"
    print(f"Парсинг страницы {page_num} — {url}")

    session = requests.Session()
    response = session.get(url=url, headers=headers)

    if response.status_code != 200:
        print(f"Страница {page_num} не найдена. Стоп.")
        return False

    soup = BeautifulSoup(response.text, 'html.parser')

    promo_links = soup.select('a.ssrcss-5wtq5v-PromoLink, a.ssrcss-9haqql-LinkPostLink')
    if not promo_links:
        print(f"Нет новостей на странице {page_num}. Стоп.")
        return False

    for a in promo_links:
        href = a.get('href')
        if href and '/news/articles/' in href:
            full_url = base_url + href if href.startswith('/') else href
            article_id = href.split('/')[-1]

            global_id_counter += 1

            headline = a.get_text(strip=True)

            date_span = a.find_next('span', class_='visually-hidden')
            date_str = date_span.get_text(strip=True) if date_span else None
            pub_date = None
            if date_str and 'published at' in date_str:
                try:
                    date_part = date_str.split('published at')[-1].strip()
                    pub_date = datetime.strptime(date_part, '%H:%M %d %B')
                    pub_date = pub_date.replace(year=datetime.now().year)
                except Exception:
                    pub_date = None

            print(f"ID{global_id_counter}: {article_id}")
            print(f"URL: {full_url}")
            print(f"Headline: {headline}")
            print(f"Published date (approx): {pub_date}")

            body = parse_article(full_url)
            print(f"Body preview: {body[:200]}...\n")  # первые 200 символов

    return True

def main():
    page = 1
    while page < 5:
        success = get_articles_urls(page)
        if not success:
            break
        time.sleep(2)
        page += 1

if __name__ == '__main__':
    main()
 