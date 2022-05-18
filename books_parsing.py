import argparse
import json
import time
import os
from textwrap import dedent
from urllib.parse import unquote, urljoin, urlsplit

import lxml
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


def text_length_limit(text, limit=140):
    if len(text) <= limit:
        return text
    splited_text = text.split('. ')
    new_text = ' '.join(splited_text[:len(splited_text) - 1])
    if new_text == text:
        return text[:limit]
    else:
        return text_length_limit(new_text)


def was_redirected(original_url, actual_url):
    return original_url != actual_url


def parse_book_page(response, book_url):
    book_metadata = {}

    page_source = bs(response.text, 'lxml')

    book_meta = page_source.find('td', class_='ow_px_td')
    title, author = book_meta.find('h1').text.split('::')
    book_metadata['title'] = title.strip()
    book_metadata['author'] = author.strip()

    cover_path = page_source.find(
        'div', class_='bookimage'
    ).findChild('img').get('src')

    book_metadata['cover_url'] = urljoin(book_url, cover_path)

    comments_fields = page_source.find_all('div', class_='texts')
    book_metadata['comments'] = [comment.find('span').text.strip() for comment in comments_fields]
    
    genres_field = page_source.find('span', class_='d_book')
    book_metadata['genres'] = [genre.text for genre in genres_field.findChildren('a')]
    
    return book_metadata


def download_book(response, book_id, book_name, book_folder = 'Books'):
    os.makedirs(book_folder, exist_ok=True)
    correct_book_name = sanitize_filename(book_name)
    full_path = os.path.join(
        book_folder,
        f'{text_length_limit(f"{book_id}. {correct_book_name}")}.txt'
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

    if was_redirected(cover_url, response.url):
        raise RedirectError(f'Book [{book_id}]: NOT FOUND IMAGE, REDIRECTED TO {response.url}.')

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
            download_book_url = f'https://tululu.org/txt.php?id={book_id}'

            download_book_response = requests.get(download_book_url)
            download_book_response.raise_for_status()

            if was_redirected(download_book_url, download_book_response.url):
                raise RedirectError(f'Book [{book_id}] NOT FOUND: REDIRECTED TO {response.url}.')
            
            book_main_url = f'https://tululu.org/b{book_id}/'

            response = requests.get(book_main_url)
            response.raise_for_status()

            if was_redirected(book_main_url, response.url):
                raise RedirectError(f'Book [{book_id}]: NOT FOUND BOOK INFO, REDIRECTED TO {response.url}.')
            
            book_metadata = parse_book_page(response, book_main_url)
            
            download_book(download_book_response, book_id, book_metadata['title'])
            download_cover(book_metadata['cover_url'])

            print(json.dumps(book_metadata, indent=4, ensure_ascii=False))
            print(f'Book [{book_id}]: DOWNLOADED.')

        except RedirectError as error:
            print(error)
        except requests.exceptions.ConnectionError as error:
            while True:
                print(dedent(
                    f"""
                    {error}
                    
                    Repeating after 5 seconds...
                    """
                ))
                time.sleep(5)
                response = requests.get(error.response.url)
                if response.ok:
                    break

        except requests.exceptions.HTTPError:
            print('HTTP error')
        except requests.exceptions.RequestException:
            print(f'Book [{book_id}]: BAD REQUEST.')
        finally:
            print('-' * 20)
