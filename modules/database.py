import sqlite3
from config import Config


class Database:
    def __init__(self):
        self.conn = sqlite3.connect(Config.DATABASE_URI)
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.check_and_update_schema()

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS resumes (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                filename TEXT NOT NULL,
                content BLOB,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                company TEXT NOT NULL,
                position TEXT NOT NULL,
                job_description TEXT,
                contact_person TEXT,
                date TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        self.conn.commit()

    def check_and_update_schema(self):
        # Check if job_description column exists in applications table
        self.cursor.execute("PRAGMA table_info(applications)")
        columns = [column[1] for column in self.cursor.fetchall()]

        if 'job_description' not in columns:
            print("Adding job_description column to applications table")
            self.cursor.execute("ALTER TABLE applications ADD COLUMN job_description TEXT")
            self.conn.commit()
    def close(self):
        self.conn.close()

    def add_user(self, username, password, role='user'):
        self.cursor.execute('''
            INSERT INTO users (username, password, role)
            VALUES (?, ?, ?)
        ''', (username, password, role))
        self.conn.commit()

    def get_user(self, username):
        self.cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        return self.cursor.fetchone()

    def get_user_by_id(self, user_id):
        self.cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        return self.cursor.fetchone()

    def update_user_password(self, user_id, new_password):
        self.cursor.execute('UPDATE users SET password = ? WHERE id = ?', (new_password, user_id))
        self.conn.commit()

    def delete_user(self, user_id):
        self.cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        self.conn.commit()

    def add_resume(self, user_id, filename, content):
        self.cursor.execute('''
            INSERT INTO resumes (user_id, filename, content)
            VALUES (?, ?, ?)
        ''', (user_id, filename, content))
        self.conn.commit()

    def get_resumes(self, user_id):
        self.cursor.execute('SELECT * FROM resumes WHERE user_id = ?', (user_id,))
        return self.cursor.fetchall()

    def get_resume_by_filename(self, user_id, filename):
        self.cursor.execute('SELECT * FROM resumes WHERE user_id = ? AND filename = ?', (user_id, filename))
        return self.cursor.fetchone()

    def delete_resume(self, user_id, filename):
        self.cursor.execute('DELETE FROM resumes WHERE user_id = ? AND filename = ?', (user_id, filename))
        self.conn.commit()

    def add_application(self, user_id, company, position, job_description, contact_person, date):
        self.cursor.execute('''
            INSERT INTO applications (user_id, company, position, job_description, contact_person, date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, company, position, job_description, contact_person, date))
        self.conn.commit()

    def get_applications(self, user_id):
        self.cursor.execute('SELECT * FROM applications WHERE user_id = ?', (user_id,))
        return self.cursor.fetchall()

    def get_application_by_company_position(self, user_id, company, position):
        self.cursor.execute("""
            SELECT * FROM applications
            WHERE user_id = ? AND company = ? AND position = ?
            ORDER BY date DESC
            LIMIT 1
        """, (user_id, company, position))
        return self.cursor.fetchone()

    def delete_application(self, user_id, company, position, date):
        self.cursor.execute('''
            DELETE FROM applications 
            WHERE user_id = ? AND company = ? AND position = ? AND date = ?
        ''', (user_id, company, position, date))
        self.conn.commit()

        def get_application_by_company_position(self, user_id, company, position):
            self.cursor.execute("""
                SELECT * FROM applications
                WHERE user_id = ? AND company = ? AND position = ?
                ORDER BY date DESC
                LIMIT 1
            """, (user_id, company, position))
            return self.cursor.fetchone()