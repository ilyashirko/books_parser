from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup as bs
import lxml


TULULU_MAIN = 'https://tululu.org/'

SCIENCE_FICTION_PATH = 'l55'



if __name__ == '__main__':
    url = urljoin(TULULU_MAIN, SCIENCE_FICTION_PATH)
    response = requests.get(url)
    source = bs(response.text, 'lxml')
    
    books = source.find('div', id='content').findChildren('table')
    
    for book in books:
        book_data = book.findChildren('tr')
        book_id = book_data[1].findChild('a').get('href')
        print(book_id)