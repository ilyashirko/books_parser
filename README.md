# Парсер книжной [библиотеки](https://tululu.org/)
Программа парсит книжную библиотеку, проверяет каждый id в заданном диапазоне и если книга найдена, выдает по ней информацию.
## Установка
Для установки клонируйте репозиторий, активируйте виртуальное окружение и установите зависимости
```
git clone https://github.com/ilyashirko/books_parser/
cd books_parser
python3 -m venv env
source env/bin/activate
pip3 install -r requirements.txt
```
## books_parsing.py
Скрипт скачивает все доступные книги в заданном диапазоне.  

Для запуска вам необходимо указать аргументы  
`--start_id` (значение по умолчанию "1")  
и  
`--end_id` (значение по умолчанию "10").  
"end_id" должно быть больше либо равно "start_id" иначе программа завершит работу с ошибкой.  
Запустить программу можно командой:
```
python3 books_parsing.py --start_id 15 --end_id 35
```
И программа покажет вам информацию о книгах с уникальными номерами от 15 до 35 влючительно.

## parse_tululu_category.py
Скрипт скачивает все доступные книги, обложку и информацию о книге, жанра "научная фантастика" со всех указанных страниц.  

Программа принимает следующие аргументы:  
1. `-s` или `--start_page` - число больше нуля - первая страница на которой производится поиск книг.
2. `-e` или `--end_page` - число больше `start_page` - последняя страница, на которой производится поиск книг.
3. `--skip_imgs` - пропустить загрузку обложек.
4. `--skip_txt` - не скачивать файлы книг.
5. `--dest_folder` - задать директорию сохранения книг и обложек (по умолчанию - корневая директория проекта).
6. `--json_path` - задать директорию и название .json-файла (по умолчанию - корневая директория проекта, на).

Для запуска введите `python3 parse_tululu_category.py` с необходимыми аргументами.  
Например если хотите скачать книги с 20 по 23 страницу сайта без обложек введите:
```
python3 parse_tululu_category.py -s 20 -e 23 --skip_imgs
```
## render_website.py
Данный скрипт создан для генерации страниц сайта по шаблону `template.html` используя данные из `books.json` и для локального запуска сайта.  
Для корректной работы вам необходимо скачать базу данных выполнив один из скриптов выше, запустить `render_website.py`:
```
python3 render_website.py
```
и далее необходимо пересохранить файл `template.html`. Скрипт поймет что информация обновилась и переопределит все страницы сайта. Сайт будет доступен по адресу [Reading books](http://127.0.0.1:5500/).  
## Ознакомиться с сайтом
Можно на странице [GitHub Pages](https://ilyashirko.github.io/books_parser/pages/index1.html)