from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
from jinja2 import Environment, FileSystemLoader, select_autoescape

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

rendered_page = template.render(
    books=books_data,
    
)

with open('index.html', 'w', encoding="utf8") as file:
    file.write(rendered_page)
print('rendered')
server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
server.serve_forever()