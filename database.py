import sqlite3

# Создание таблиц (один раз при запуске, можно отдельно вызвать)
def init_db():
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            user_name TEXT,
            user_first_name TEXT
        )
        """)
        conn.commit()

    with sqlite3.connect("movies.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS films (
            code INTEGER PRIMARY KEY,
            title TEXT,
            description TEXT,
            image_url TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS likedFilms (
            userId INTEGER,
            code INTEGER,
            FOREIGN KEY (userId) REFERENCES users(user_id),
            FOREIGN KEY (code) REFERENCES films(code),
            PRIMARY KEY (userId, code)
            )
        """)
        conn.commit()

def add_user(user_id: int, user_name: str, first_name: str):
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO users (user_id, user_name, user_first_name) VALUES (?, ?, ?)", (user_id, user_name, first_name, ))
        conn.commit()

def get_user_count() -> int:
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        return cursor.fetchone()[0]

def show_movie(code: int) -> tuple:
    with sqlite3.connect("movies.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT title, description, image_url FROM films WHERE code = ?", (code,))
        return cursor.fetchone()

def add_movie(code: int, title: str, description: str, image_url: str):
    with sqlite3.connect("movies.db") as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO films (code, title, description, image_url) VALUES (?, ?, ?, ?)",
            (code, title, description, image_url)
        )
        conn.commit()

def delete_movie(code: int):
    with sqlite3.connect("movies.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM films WHERE code = ?", (code,))
        conn.commit()

def get_liked_movies(user_id: int):
    with sqlite3.connect("movies.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT code FROM likedFilms WHERE userId = ?", (user_id,))
        return [row[0] for row in cursor.fetchall()]

def add_liked_movie(user_id: int, movie_code: int):
    with sqlite3.connect("movies.db") as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO likedFilms (userId, code) VALUES (?, ?)", (user_id, movie_code))
        conn.commit()

def remove_liked_movie(user_id: int, movie_code: int):
    with sqlite3.connect("movies.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM likedFilms WHERE userId = ? AND code = ?", (user_id, movie_code))
        conn.commit()

def sendPostPeople():
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users")
        return [row[0] for row in cursor.fetchall()]

def show_all_movies():
    with sqlite3.connect("movies.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM films")
        return cursor.fetchall()

def show_all_users():
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        return cursor.fetchall()
    
def editFilmTitle(code: int, new_title: str):
    with sqlite3.connect("movies.db") as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE films SET title = ? WHERE code = ?", (new_title, code))
        conn.commit()

def editFilmDescription(code: int, new_description: str):
    with sqlite3.connect("movies.db") as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE films SET description = ? WHERE code = ?", (new_description, code))
        conn.commit()

def editFilmImage(code: int, new_image_url: str):
    with sqlite3.connect("movies.db") as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE films SET image_url = ? WHERE code = ?", (new_image_url, code))
        conn.commit()
    
init_db()