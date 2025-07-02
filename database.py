from werkzeug.security import generate_password_hash
import sqlite3

def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    conn.commit()

    # Insert admin user (username: admin, password: admin123)
    try:
        hashed_pw = generate_password_hash('admin123')
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                       ('admin', hashed_pw, 'admin'))
    except sqlite3.IntegrityError:
        pass  # Already added

    conn.commit()
    conn.close()
