import requests
import os

BOOK_FOLDER = 'Books'

class AlreadyDownloaded(Exception):
    pass


def book_request(link):
    response = requests.get(book_link)
    response.raise_for_status()
    if response.url != link:
        raise requests.HTTPError
    if not os.path.exists(f'{BOOK_FOLDER}/{id}.txt'):
        with open(f'{BOOK_FOLDER}/{id}.txt', 'wb') as new_book:
            new_book.write(response.content)
    else:
        raise AlreadyDownloaded


if __name__ == '__main__':
    os.makedirs(BOOK_FOLDER, exist_ok=True)
    for id in range(1, 11):
        try:
            book_link = f'https://tululu.org/txt.php?id={id}'
            book_request(book_link)
            print(f'Book [{id}]: DOWNLOADED.')
        except requests.HTTPError:
            print(f'Book [{id}]: NOT FOUND.')
        except AlreadyDownloaded:
            print(f'Book [{id}]: ALREADY DOWNLOADED.')
        except requests.exceptions.RequestException:
            print(f'Book [{id}]: BAD REQUEST.')
                
        
            