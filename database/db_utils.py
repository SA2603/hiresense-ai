import sqlite3
import bcrypt
import os
import json
from datetime import datetime

# Path to the actual database file - it will be created automatically on first run
DB_PATH = os.path.join(os.path.dirname(__file__), "hiresense.db")


def get_connection():
    """
    Opens and returns a connection to the SQLite database file.
    Every function below calls this to get access to the database.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # lets us access columns by name, e.g. row["username"]
    return conn


def init_db():
    """
    Reads schema.sql and executes it, creating all tables if they don't
    already exist. Safe to call every time the app starts.
    """
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, "r") as f:
        schema_sql = f.read()

    conn = get_connection()
    conn.executescript(schema_sql)
    conn.commit()
    conn.close()


def create_user(username: str, email: str, password: str) -> bool:
    """
    Hashes the password and inserts a new user row.
    Returns True on success, False if username/email already exists.
    """
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, password_hash.decode("utf-8"))
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # This fires if username or email UNIQUE constraint is violated
        return False
    finally:
        conn.close()


def verify_user(username: str, password: str):
    """
    Checks a login attempt against the stored hash.
    Returns the user row (as a dict) if valid, otherwise None.
    """
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()
    conn.close()

    if row is None:
        return None  # no such username

    stored_hash = row["password_hash"].encode("utf-8")
    if bcrypt.checkpw(password.encode("utf-8"), stored_hash):
        return dict(row)  # convert sqlite3.Row to a plain dict
    return None  # password didn't match


def save_resume(user_id: int, filename: str, raw_text: str, parsed_data: dict = None) -> int:
    """
    Inserts a new resume row for a given user.
    parsed_data is a dict (we'll start using this properly in Stage 4) -
    stored as a JSON string since SQLite has no native dict/list type.
    Returns the new resume_id.
    """
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO resumes (user_id, filename, raw_text, parsed_data) VALUES (?, ?, ?, ?)",
        (user_id, filename, raw_text, json.dumps(parsed_data) if parsed_data else None)
    )
    conn.commit()
    resume_id = cursor.lastrowid  # SQLite tells us the auto-generated ID of the row we just inserted
    conn.close()
    return resume_id


def get_resumes_for_user(user_id: int) -> list:
    """
    Returns all resumes a user has uploaded, most recent first.
    Used later for the dashboard/history feature.
    """
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM resumes WHERE user_id = ? ORDER BY uploaded_at DESC",
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]