import argparse
import json
import os
import time

from contextlib import suppress
from textwrap import dedent
from urllib.parse import urljoin

import lxml
import requests

from bs4 import BeautifulSoup as bs

from books_parsing import (RedirectError, check_for_redirect, download_book,
                           download_cover, parse_book_page)


def make_parser():
    parser = argparse.ArgumentParser(
        description='This app download science fiction books from tululu.'
    )
    default_json_path = os.path.join(os.getcwd(), 'books.json')
    parser.add_argument(
        '-s',
        '--start_page',
        type=int,
        default=1,
        help='искать "от"',
        metavar=''
    )
    parser.add_argument(
        '-e',
        '--end_page',
        type=int,
        default=10,
        help='искать "до" (должно быть больше чем "от")',
        metavar=''
    )
    parser.add_argument(
        '--skip_imgs',
        action='store_true',
        default=False,
        help='не скачивать обложки'
    )
    parser.add_argument(
        '--skip_txt',
        action='store_true',
        default=False,
        help='не скачивать тексты книг'
    )
    parser.add_argument(
        '--dest_folder',
        default=None,
        help='директория для загруженных файлов',
        metavar=''
    )
    parser.add_argument(
        '--json_path',
        default=default_json_path,
        help=f'директория для json с информацией о книгах (напр: {default_json_path})',
        metavar=''
    )
    return parser


def main():
    parser = make_parser()
    args = parser.parse_args()

    start_page = args.start_page
    end_page = args.end_page
    dest_folder = args.dest_folder
    
    if end_page < start_page:
        print(
            dedent(
                '''
                "--end_id" должно быть больше числа "--start_id"
                Например: python3 books_parsing.py --start_id 12 --end_id 19
                '''
            ) 
        )
        exit()

    tululu_main = 'https://tululu.org/'

    sciene_fiction_path = 'l55'

    books = dict()

    for page in range(start_page, end_page + 1):
        url = urljoin(tululu_main, f'{sciene_fiction_path}/{page}')

        response = requests.get(url)
        try:
            check_for_redirect(response)
        except RedirectError:
            print('NOT FOUND: ', response.url)
            break
        
        source = bs(response.text, 'lxml')
        
        books_tags = source.select("td.ow_px_td table tr div.bookimage a")
        
        for book in books_tags:
            try:
                book_href = book.get('href')

                book_id = ''.join((x for x in book_href if x.isdigit()))

                book_main_url = urljoin(tululu_main, book_href)
                
                response = requests.get(book_main_url)
                response.raise_for_status()
                
                book = parse_book_page(response, book_main_url)

                if not args.skip_txt:
                    download_book(
                        f'https://tululu.org/txt.php',
                        book_id,
                        book['title'],
                        book_folder=dest_folder
                    )
                
                if not args.skip_imgs:
                    download_cover(book['cover_url'], cover_folder=dest_folder)

                books.update({book_main_url: book})
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
                
    with open(args.json_path, 'w') as books_json:
        json.dump(books, books_json, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    main()