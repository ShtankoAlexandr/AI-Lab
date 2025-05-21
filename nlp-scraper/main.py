import requests
from bs4 import BeautifulSoup
import time

headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Mobile Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
}

base_url = 'https://www.bbc.co.uk'
section_url = 'https://www.bbc.co.uk/news/world'

# def get_articles_urls(page_num):
#     url = f"{section_url}?page={page_num}"
#     print(f" Парсинг страницы {page_num} — {url}")
    
#     session = requests.Session()
#     response = session.get(url=url, headers=headers)

#     if response.status_code != 200:
#         print(f" Страница {page_num} не найдена. Стоп.")
#         return False

#     soup = BeautifulSoup(response.text, 'html.parser')

#     promo_links = soup.select('a.ssrcss-5wtq5v-PromoLink, a.ssrcss-9haqql-LinkPostLink')
#     if not promo_links:
#         print(f" Нет новостей на странице {page_num}. Стоп.")
#         return False

#     for i, a in enumerate(promo_links, start=1):
#         href = a.get('href')
#         if href and '/news/articles/' in href:
#             full_url = base_url + href if href.startswith('/') else href
#             article_id = href.split('/')[-1]
#             print(f"  ID{i}: {article_id}, URL: {full_url}")
    
#     return True

import re
from bs4 import BeautifulSoup

html = '''
<span class="visually-hidden ssrcss-1f39n02-VisuallyHidden e16en2lz0">
    Watch: Traffic chaos as Spain and Portugal face power outages. Video, 00:00:41, published at 17:22 28 April
</span>
'''

soup = BeautifulSoup(html, 'html.parser')

for span in soup.find_all('span', class_='visually-hidden'):
    text = span.get_text()
    match = re.search(r'published at (\d{2}:\d{2} \d{1,2} \w+)', text)
    if match:
        pub_time = match.group(1)
        print(f"🕒 Найдена дата публикации: {pub_time}")



def main():
    page = 1
    while True:
        success = get_articles_urls(page)
        if not success:
            break
        time.sleep(1)  # пауза, чтобы не нагружать сервер
        page += 1

if __name__ == '__main__':
    main()
