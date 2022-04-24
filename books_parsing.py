import requests
import os
from bs4 import BeautifulSoup as bs
from pathvalidate import sanitize_filename

BOOK_FOLDER = 'Books'


def get_valid_response(book_id):
    url = f'https://tululu.org/txt.php?id={book_id}'
    response = requests.get(url)
    response.raise_for_status()
    if response.url != url:
        raise requests.HTTPError
    return response
    

def get_book_info(book_id):
    url = f'https://tululu.org/b{book_id}/'
    response = requests.get(url)
    response.raise_for_status()
    page_source = bs(response.text, 'html.parser')
    book_info = page_source.find('td', class_='ow_px_td')
    book_name, book_author = book_info.find('h1').text.split('::')
    return book_name.strip(), book_author.strip()


def save_book(response, book_id, book_name):
    correct_book_name = sanitize_filename(book_name)
    full_path = os.path.join(
        BOOK_FOLDER,
        f'{book_id}. {correct_book_name}.txt'
    )
    with open(full_path, 'wb') as new_book:
        new_book.write(response.content)


if __name__ == '__main__':
    os.makedirs(BOOK_FOLDER, exist_ok=True)
    for book_id in range(1, 11):
        try:
            response = get_valid_response(book_id)
            if response.ok:
                book_name, book_author = get_book_info(book_id)
                save_book(response, book_id, book_name)
                print(f'Book [{book_id}]: DOWNLOADED.')
                
        except requests.HTTPError:
            print(f'Book [{book_id}]: NOT FOUND.')
        except requests.exceptions.RequestException:
            print(f'Book [{book_id}]: BAD REQUEST.')
                
        
            