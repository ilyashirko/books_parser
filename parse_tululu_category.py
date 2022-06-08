import json
from urllib.parse import urljoin
import time
from contextlib import suppress
import lxml
import requests
from bs4 import BeautifulSoup as bs

from books_parsing import (RedirectError, check_for_redirect, download_book,
                           download_cover, parse_book_page)

TULULU_MAIN = 'https://tululu.org/'

SCIENCE_FICTION_PATH = 'l55'

books_selector = "td.ow_px_td table tr div.bookimage a"

if __name__ == '__main__':
    for page in range(1, 5):
        url = urljoin(TULULU_MAIN, f'{SCIENCE_FICTION_PATH}/{page}')
        response = requests.get(url)
        try:
            check_for_redirect(response)
        except RedirectError:
            break
        
        source = bs(response.text, 'lxml')
        
        books = source.select(books_selector)
        
        for book in books:
            try:
                book_href = book.get('href')

                book_id = ''.join((x for x in book_href if x.isdigit()))

                book_main_url = urljoin(TULULU_MAIN, book_href)
                print(book_main_url)

                response = requests.get(book_main_url)
                book = parse_book_page(response, book_main_url)

                download_book(f'https://tululu.org/txt.php', book_id, book['title'])
                download_cover(book['cover_url'])

                print(json.dumps(book, indent=4, ensure_ascii=False))
                print(f'Book [{book_id}]: DOWNLOADED.')
            except RedirectError as error:
                print(error)
            except requests.exceptions.ConnectionError as error:
                print(error)
                while True:
                    time.sleep(5)
                    print('Trying to reconnect...')
                    with suppress(requests.exceptions.ConnectionError):
                        response = requests.get(error.response.url)
                        if response.ok:
                            break
            except requests.exceptions.HTTPError as error:
                print(f'Book [{book_id}]:\n{error}')
            except requests.exceptions.RequestException:
                print(f'Book [{book_id}]: BAD REQUEST.')
            finally:
                print('-' * 20)