import sqlite3
from datetime import datetime

class DebtTracker:
    def __init__(self, db_path="debts.db"):
        self.conn = sqlite3.connect(db_path)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS debts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                date TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def get_debts(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name, amount, description, date FROM debts")
        return cursor.fetchall()
    
    def add_debt(self, name, amount, description, date=None):
        if date is None:
            date = datetime.now().strftime("%d.%m.%Y %H:%M")
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO debts (name, amount, description, date) VALUES (?, ?, ?, ?)",
            (name, amount, description, date)
        )
        self.conn.commit()

    def get_debts(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name, amount, description, date FROM debts")
        return cursor.fetchall()

    def calculate_total_debt(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT SUM(amount) FROM debts")
        result = cursor.fetchone()
        return result[0] if result[0] else 0

    def search_debt(self, query):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, name, amount, description, date FROM debts WHERE name LIKE ? OR description LIKE ?",
            (f"%{query}%", f"%{query}%")
        )
        return cursor.fetchall()

    def delete_debt(self, debt_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM debts WHERE id = ?", (debt_id,))
        self.conn.commit()

    def edit_debt(self, debt_id, name, amount, description, date):
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE debts SET name=?, amount=?, description=?, date=? WHERE id=?",
            (name, amount, description, date, debt_id)
        )
        self.conn.commit()