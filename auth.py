import sqlite3
from flask import session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

def refresh_session_role():
    if 'user' in session:
        username = session['user']['username']
        user = get_user(username)
        if user:
            session['user']['role'] = user[3]  # Update role from DB


def get_user(username):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def login_user(username, password):
    user = get_user(username)
    if user and check_password_hash(user[2], password):  # ✅ check hashed password
        session['user'] = {'username': user[1], 'role': user[3]}
        return True
    return False

def is_logged_in():
    return 'user' in session

def is_admin():
    return session['user']['role'] == 'admin' if 'user' in session else False

def logout_user():
    session.pop('user', None)

def create_user(username, password, role='user'):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    hashed = generate_password_hash(password)  # 🔒 hash password

    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                       (username, hashed, role))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_all_users():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role FROM users")
    users = cursor.fetchall()
    conn.close()
    return users

def update_user(user_id, username, password, role):
    import sqlite3
    from werkzeug.security import generate_password_hash

    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    if password.strip():  # Only hash + update if password is NOT blank
        hashed = generate_password_hash(password)
        c.execute(
            'UPDATE users SET username=?, password=?, role=? WHERE id=?',
            (username, hashed, role, user_id)
        )
    else:
        c.execute(
            'UPDATE users SET username=?, role=? WHERE id=?',
            (username, role, user_id)
        )

    conn.commit()
    conn.close()




