from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server, shell
from more_itertools import chunked
import shutil
import os


def on_reload():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')
    pages_dir = './pages'
    with open('books.json', 'r') as books_json:
        books = json.load(books_json)

    books_data = list()

    for url, book_data in books.items():
        books_data.append(book_data)

    chunked_books = chunked(books_data, 10)

    if os.path.isdir(pages_dir):
        shutil.rmtree(pages_dir)
    os.mkdir(pages_dir)

    for num, books in enumerate(chunked_books):
        rendered_page = template.render(
            books=list(chunked(books, 2)),
        )
        
        with open(f'{pages_dir}/index{num + 1}.html', 'w', encoding="utf8") as file:
            file.write(rendered_page)


if __name__ == '__main__':
    server = Server()
    server.watch('template.html', on_reload)
    server.serve(root='.')   
