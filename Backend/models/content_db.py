import os
import sqlite3

class ContentDB:
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.abspath(os.path.join(base_dir, '../../DataBase/content.db'))
        print("Using Content DB at:", self.db_path)
        self.create_table()

    def connect(self):
        return sqlite3.connect(self.db_path)

    def create_table(self):
        with self.connect() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS content (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    emailId TEXT,
                    title TEXT,
                    tag TEXT,
                    link TEXT
                )
            ''')
            conn.commit()

    def add_content(self, emailId, title, tag, link):
        with self.connect() as conn:
            conn.execute('''
                INSERT INTO content (emailId, title, tag, link)
                VALUES (?, ?, ?, ?)
            ''', (emailId, title, tag, link))
            conn.commit()

    def get_user_content(self, emailId):
        with self.connect() as conn:
            cursor = conn.execute('''
                SELECT title, tag, link FROM content
                WHERE emailId=?
                ORDER BY id DESC
            ''', (emailId,))
            content = cursor.fetchall()
            return [
                {"title": row[0], "tag": row[1], "link": row[2]} for row in content
            ]
