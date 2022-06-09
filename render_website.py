from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server, shell
from more_itertools import chunked


def on_reload():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')

    with open('books.json', 'r') as books_json:
        books = json.load(books_json)

    books_data = list()

    for url, book_data in books.items():
        books_data.append(book_data)

    shit = list(chunked(books_data, 2))
    
    rendered_page = template.render(
        chunked_books=list(chunked(books_data, 2)),
    )
    
    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)


if __name__ == '__main__':
    server = Server()
    server.watch('template.html', on_reload)
    server.serve(root='.')   
