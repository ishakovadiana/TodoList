import sqlite3
from datetime import date

DATABASE = 'todos.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            created_at DATE NOT NULL
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            category TEXT NOT NULL,
            done INTEGER DEFAULT 0,
            created_at DATE NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("База данных создана!")

def add_user(username, password):
    conn = get_db_connection()
    try:
        conn.execute(
            'INSERT INTO users (username, password, created_at) VALUES (?, ?, ?)',
            (username, password, date.today().isoformat())
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user(username, password):
    conn = get_db_connection()
    user = conn.execute(
        'SELECT * FROM users WHERE username = ? AND password = ?',
        (username, password)
    ).fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return user

def add_task(user_id, title, description, category):
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO tasks (user_id, title, description, category, done, created_at) VALUES (?, ?, ?, ?, ?, ?)',
        (user_id, title, description, category, 0, date.today().isoformat())
    )
    conn.commit()
    conn.close()

def get_tasks_by_user(user_id, category=None):
    conn = get_db_connection()
    if category and category != 'все':
        tasks = conn.execute(
            'SELECT * FROM tasks WHERE user_id = ? AND category = ? ORDER BY created_at DESC',
            (user_id, category)
        ).fetchall()
    else:
        tasks = conn.execute(
            'SELECT * FROM tasks WHERE user_id = ? ORDER BY created_at DESC',
            (user_id,)
        ).fetchall()
    conn.close()
    return tasks

def delete_task(task_id, user_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM tasks WHERE id = ? AND user_id = ?', (task_id, user_id))
    conn.commit()
    conn.close()

def toggle_task(task_id, user_id):
    conn = get_db_connection()
    task = conn.execute('SELECT done FROM tasks WHERE id = ? AND user_id = ?', (task_id, user_id)).fetchone()
    if task:
        new_status = 0 if task['done'] else 1
        conn.execute('UPDATE tasks SET done = ? WHERE id = ? AND user_id = ?', (new_status, task_id, user_id))
        conn.commit()
    conn.close()

def search_tasks(user_id, query):
    conn = get_db_connection()
    tasks = conn.execute(
        'SELECT * FROM tasks WHERE user_id = ? AND (title LIKE ? OR description LIKE ?) ORDER BY created_at DESC',
        (user_id, f'%{query}%', f'%{query}%')
    ).fetchall()
    conn.close()
    return tasks

def get_task_by_id(task_id, user_id):
    conn = get_db_connection()
    task = conn.execute('SELECT * FROM tasks WHERE id = ? AND user_id = ?', (task_id, user_id)).fetchone()
    conn.close()
    return task

def update_task(task_id, user_id, title, description, category):
    conn = get_db_connection()
    conn.execute(
        'UPDATE tasks SET title = ?, description = ?, category = ? WHERE id = ? AND user_id = ?',
        (title, description, category, task_id, user_id)
    )
    conn.commit()
    conn.close()