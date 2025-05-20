import requests
from bs4 import BeautifulSoup


headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Mobile Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
   
}



def get_articles_urls(url):
    s=requests.Session()
    response=s.get(url=url,headers=headers)

    soup=BeautifulSoup(response.text, 'lxml')
    pagination = soup.find('div', class_='pagination')
    if not pagination:
        print("Пагинация не найдена.")
        return None

    page_links = pagination.find_all('a', class_='page-numbers')
    if not page_links:
        print("Ссылок на страницы не найдено.")
        return None

    page_numbers = []
    for link in page_links:
        text = link.text.strip()
        if text.isdigit():
            page_numbers.append(int(text))

    if page_numbers:
        total_pages = max(page_numbers)
        print(f"Всего страниц: {total_pages}")
        return total_pages
    else:
        print("Числовых ссылок на страницы нет.")
        return None
    # with open('index.html','w', encoding='utf-8') as file:
    #     file.write(response.text)



def main():
    get_articles_urls(url='https://www.hitechgp.co.uk/news/')

if __name__=='__main__':
    main()
    