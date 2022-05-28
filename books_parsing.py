import argparse
import json
import os
import time
from contextlib import suppress
from textwrap import dedent
from urllib.parse import unquote, urljoin, urlsplit

import requests
from bs4 import BeautifulSoup as bs
from pathvalidate import sanitize_filename

APP_DESCRIPTION = (
    'Программа парсит сайт tululu.org, скачивает книги и информацию о них'
)

class RedirectError(Exception):
    def __init__(self, text='произошел редирект...'):
        self.text = text

    def __str__(self):
        return self.text


def check_for_redirect(response):
    if response.history:
        raise RedirectError(f'REDIRECTED TO "{response.url}".')


def text_length_limit(text, limit=140):
    if len(text) <= limit:
        return text
    splited_text = text.split('. ')
    new_text = ' '.join(splited_text[:len(splited_text) - 1])
    if new_text == text:
        return text[:limit]
    else:
        return text_length_limit(new_text)


def parse_book_page(response, book_url):
    page_source = bs(response.text, 'lxml')

    book_meta = page_source.find('td', class_='ow_px_td')
    title, author = book_meta.find('h1').text.split('::')
    
    cover_path = page_source.find(
        'div', class_='bookimage'
    ).findChild('img').get('src')

    comments_fields = page_source.find_all('div', class_='texts')
    
    genres_field = page_source.find('span', class_='d_book')
    
    book = {
        'title': title.strip(),
        'author': author.strip(),
        'cover_url': urljoin(book_url, cover_path),
        'comments': [comment.find('span').text.strip() for comment in comments_fields],
        'genres': [genre.text for genre in genres_field.findChildren('a')]
    }
    return book


def download_book(book_url, book_id, book_name, book_folder = 'Books'):
    response = requests.get(book_url, params={'id': book_id})
    response.raise_for_status()
    
    check_for_redirect(response)

    os.makedirs(book_folder, exist_ok=True)
    correct_book_name = f"{book_id}. {sanitize_filename(book_name)}.txt"
    full_path = os.path.join(
        book_folder,
        text_length_limit(correct_book_name)
    )
    with open(full_path, 'wb') as new_book:
        new_book.write(response.content)


def download_cover(cover_url, cover_folder = 'Covers'):
    os.makedirs(cover_folder, exist_ok=True)
    _, photo_name = os.path.split(unquote(urlsplit(cover_url).path))
    full_path = os.path.join(cover_folder, photo_name)

    if os.path.exists(full_path):
        return

    response = requests.get(cover_url)
    response.raise_for_status()

    check_for_redirect(response)
    
    with open(full_path, 'wb') as photo:
        photo.write(response.content)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=APP_DESCRIPTION)

    parser.add_argument(
        '--start_id',
        type=int,
        default=1,
        help='искать "от"'
    )
    parser.add_argument(
        '--end_id',
        type=int,
        default=10,
        help='искать "до" (должно быть больше чем "от")'
    )

    args = parser.parse_args()

    start_id = args.start_id
    end_id = args.end_id

    if end_id < start_id:
        print(
            dedent(
                '''
                "--end_id" должно быть больше числа "--start_id"
                Например: python3 books_parsing.py --start_id 12 --end_id 19
                '''
            ) 
        )
        exit()

    for book_id in range(start_id, end_id + 1):
        try:
            book_main_url = f'https://tululu.org/b{book_id}/'

            response = requests.get(book_main_url)
            response.raise_for_status()

            check_for_redirect(response)

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
                with suppress(requests.exceptions):
                    response = requests.get(error.response.url)
                    if response.ok:
                        break
        except requests.exceptions.HTTPError as error:
            print(f'Book [{book_id}]:\n{error}')
        except requests.exceptions.RequestException:
            print(f'Book [{book_id}]: BAD REQUEST.')
        finally:
            print('-' * 20)
