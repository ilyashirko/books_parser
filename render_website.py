import json
import os
import shutil

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked

PAGES_DIR = 'pages'

BOOKS_PER_PAGE = 10

RENDER_COLUMNS = 2

def on_reload():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')
    
    with open('books.json', 'r') as books_json:
        books = json.load(books_json)
    
    chunked_books = list(chunked(list(books.values()), BOOKS_PER_PAGE))
    
    if os.path.isdir(PAGES_DIR):
        shutil.rmtree(PAGES_DIR)
    os.mkdir(PAGES_DIR)
    
    for num, books in enumerate(chunked_books):
        rendered_page = template.render(
            books=list(chunked(books, BOOKS_PER_PAGE), RENDER_COLUMNS),
            pages=len(chunked_books),
            current=num+1 
        )
        with open(f'{PAGES_DIR}/index{num+1}.html', 'w', encoding="utf8") as file:
            file.write(rendered_page)


if __name__ == '__main__':
    server = Server()
    on_reload()
    server.watch('template.html', on_reload)
    server.serve(root='.', default_filename=f'{PAGES_DIR}/index1.html')   
