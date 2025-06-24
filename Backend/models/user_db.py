import os
import sqlite3

class User:
    def __init__(self, emailId, password, name):
        self.emailId = emailId
        self.password = password
        self.name = name

class UserDB:
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.abspath(os.path.join(base_dir, '../../DataBase/users.db'))
        print("Using User DB at:", self.db_path)
        self.create_table()

    def connect(self):
        return sqlite3.connect(self.db_path)

    def create_table(self):
        with self.connect() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    emailId TEXT UNIQUE,
                    password TEXT,
                    name TEXT
                )
            ''')
            conn.commit()

    def add_user(self, user):
        try:
            with self.connect() as conn:
                conn.execute('''
                    INSERT INTO users (emailId, password, name)
                    VALUES (?, ?, ?)
                ''', (user.emailId, user.password, user.name))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False

    def validate_user(self, emailId, password):
        with self.connect() as conn:
            cursor = conn.execute('''
                SELECT * FROM users
                WHERE emailId=? AND password=?
            ''', (emailId, password))
            return cursor.fetchone()

    def get_all_users(self):
        with self.connect() as conn:
            cursor = conn.execute("SELECT name, emailId FROM users")
            return [{"name": row[0], "email": row[1]} for row in cursor.fetchall()]
