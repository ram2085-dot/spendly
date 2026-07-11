import os
import sqlite3
from datetime import date

from werkzeug.security import check_password_hash, generate_password_hash

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "spendly.db"
)

CATEGORIES = ["Food", "Transport", "Bills", "Health", "Entertainment", "Shopping", "Other"]


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    conn.commit()
    conn.close()


def get_user_by_email(email):
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM users WHERE email = ?",
        (email,),
    ).fetchone()
    conn.close()
    return row


def create_user(name, email, password):
    conn = get_db()
    password_hash = generate_password_hash(password)
    cursor = conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        (name, email, password_hash),
    )
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return user_id


def verify_user(email, password):
    user = get_user_by_email(email)
    if user is None:
        return None
    if not check_password_hash(user["password_hash"], password):
        return None
    return user


def seed_db():
    conn = get_db()
    count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if count > 0:
        conn.close()
        return

    password_hash = generate_password_hash("demo123")
    cursor = conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Demo User", "demo@spendly.com", password_hash),
    )
    user_id = cursor.lastrowid

    month_prefix = date.today().strftime("%Y-%m")
    sample_expenses = [
        (user_id, 45.50, "Food", f"{month_prefix}-01", "Groceries"),
        (user_id, 12.00, "Transport", f"{month_prefix}-03", "Bus fare"),
        (user_id, 89.99, "Bills", f"{month_prefix}-05", "Electricity bill"),
        (user_id, 25.00, "Health", f"{month_prefix}-09", "Pharmacy"),
        (user_id, 15.75, "Entertainment", f"{month_prefix}-12", "Movie tickets"),
        (user_id, 60.00, "Shopping", f"{month_prefix}-16", "New shoes"),
        (user_id, 8.25, "Other", f"{month_prefix}-20", "Miscellaneous"),
        (user_id, 32.40, "Food", f"{month_prefix}-24", "Dinner out"),
    ]

    conn.executemany(
        """
        INSERT INTO expenses (user_id, amount, category, date, description)
        VALUES (?, ?, ?, ?, ?)
        """,
        sample_expenses,
    )
    conn.commit()
    conn.close()
