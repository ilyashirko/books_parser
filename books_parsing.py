import argparse
import json
import os

from urllib.parse import unquote, urljoin, urlsplit

import requests

from bs4 import BeautifulSoup as bs
from pathvalidate import sanitize_filename

BASE_TULULU_URL = 'https://tululu.org/'

BOOK_FOLDER = 'Books'

COVER_FOLDER = 'Covers'

APP_DESCRIPTION = (
    'Программа парсит сайт tululu.org, скачивает книги и информацию о них'
)


def get_valid_book(book_id):
    url = f'https://tululu.org/txt.php?id={book_id}'
    response = requests.get(url)
    response.raise_for_status()
    if response.url != url:
        raise requests.HTTPError
    return response


def parse_book_page(page_source):
    book_info = {}

    book_meta = page_source.find('td', class_='ow_px_td')
    title, author = book_meta.find('h1').text.split('::')
    book_info.update(
        {
            'title': title.strip(),
            'author': author.strip()
        }
    )

    book_cover_path = page_source.find(
        'div', class_='bookimage'
    ).findChild('img').get('src')

    book_info.update(
        {
            'cover_url': urljoin(BASE_TULULU_URL, book_cover_path)
        }
    )

    book_comments_fields = page_source.find_all('div', class_='texts')
    if book_comments_fields:
        book_info.update(
            {
                'comments': [comment.find('span').text.strip() for comment in book_comments_fields]
            }
        )
    else:
        book_info.update({'comments': None})

    book_genres_field = page_source.find('span', class_='d_book')
    if book_genres_field:
        book_info.update(
            {
                'genres': [genre.text for genre in book_genres_field.findChildren('a')]
            }
        )
    else:
        book_info.update({'genres': None})

    return book_info


def download_book(response, book_id, book_name):
    correct_book_name = sanitize_filename(book_name)
    full_path = os.path.join(
        BOOK_FOLDER,
        f'{book_id}. {correct_book_name}.txt'
    )
    with open(full_path, 'wb') as new_book:
        new_book.write(response.content)


def download_cover(cover_url):
    _, photo_name = os.path.split(unquote(urlsplit(cover_url).path))
    full_path = os.path.join(COVER_FOLDER, photo_name)

    if not os.path.exists(full_path):
        response = requests.get(cover_url)
        response.raise_for_status()
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

    if end_id >= start_id:
        for book_id in range(start_id, end_id + 1):
            try:
                book_response = get_valid_book(book_id)
                if book_response.ok:
                    book_info_url = f'https://tululu.org/b{book_id}/'

                    book_info_response = requests.get(book_info_url)
                    book_info_page_source = bs(
                        book_info_response.text,
                        'html.parser'
                        )

                    book_info = parse_book_page(book_info_page_source)

                    print(json.dumps(book_info, indent=4, ensure_ascii=False))
                    print(f'Book [{book_id}]: DOWNLOADED.')

            except requests.HTTPError:
                print(f'Book [{book_id}]: NOT FOUND.')
            except requests.exceptions.RequestException:
                print(f'Book [{book_id}]: BAD REQUEST.')
            finally:
                print('-' * 20)
    else:
        print(
            '--end_id" должно быть больше числа "--start_id".\n'
            'Например: python3 books_parsing.py --start_id 12 --end_id 19'
        )
