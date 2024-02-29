from flask import Flask, request, jsonify
import psycopg2
from config import load_config
from connect import connect

app = Flask(__name__)

def db_version():
    try:
        print("Connecting to PostgreSQL database...")
        conn = connect()
        cursor = conn.cursor()
        print('PostgreSQL database version: ')
        cursor.execute('SELECT version()')
        db_version = cursor.fetchone()
        print(db_version)
        cursor.close()
    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print("Database connection closed.")


@app.route('/')
def index():
    return "Hello World!"

@app.route('/<name>')
def print_name(name):
    return 'fuck you, {}'.format(name)

@app.route('/books', methods=['GET', 'POST'])
def books():
    conn = connect()
    cursor = conn.cursor()
    if request.method == 'GET':
        cursor.execute('SELECT * FROM books;')
        books = [
            dict(id=row[0], author=row[1], language=row[2], title=row[3])
            for row in cursor.fetchall()
        ]
        if books is not None:
            return jsonify(books)
    if request.method == 'POST':
        new_author = request.form['author']
        new_lang = request.form['language']
        new_title = request.form['title']
        sql = """INSERT INTO books (author, language, title)
        VALUES (%s, %s, %s) RETURNING id;"""
        cursor.execute(sql, (new_author, new_lang, new_title))
        conn.commit()
        return f"Book with id {cursor.fetchone()[0]} created successfully."
    cursor.close()
    print("Cursor closed.")
    conn.close()
    print("Database connection closed.")
        
@app.route('/book/<int:id>', methods=["GET", "PUT", "DELETE"])
def single_book(id):
    conn = connect()
    cursor = conn.cursor()
    book = None
    if request.method == 'GET':
        cursor.execute('SELECT * FROM books WHERE id=%s', (id,))
        rows = cursor.fetchall()
        for r in rows:
            book = r
        if book is not None:
            return jsonify(book), 200
        else:
            return "An error occurred.", 404
    if request.method == 'PUT':
        sql = """UPDATE books SET author=%s, language=%s, 
        title=%s WHERE id=%s"""
        author = request.form['author']
        language = request.form['language']
        title = request.form['title']
        updated_book = {
            'id': id,
            'author': author,
            'language': language,
            'title': title
            }
        cursor.execute(sql, (author, language, title, id))
        conn.commit()
        return jsonify(updated_book)
    if request.method == 'DELETE':
        sql = """DELETE FROM books WHERE id=%s"""
        cursor.execute(sql, (id,))
        conn.commit()
        return "Book with id: {} has been deleted.".format(id), 200
    cursor.close()
    print("Cursor closed.")
    conn.close()
    print("Database connection closed.")

if __name__ == '__main__':
    app.run(debug=True)
