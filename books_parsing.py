from urllib import response
import requests
import os

BOOK_FOLDER = 'Books'
def save_file(file_name, content):
    with open(file_name, 'wb') as new_file:
        new_file.write(content)



if __name__ == '__main__':
    os.makedirs(BOOK_FOLDER, exist_ok=True)
    for id in range(1, 11):
        response = requests.get(f'https://tululu.org/txt.php?id={id}')
        if response.ok and not os.path.exists(f'{BOOK_FOLDER}/{id}.txt'):
            save_file(f'{BOOK_FOLDER}/{id}.txt', response.content)
            