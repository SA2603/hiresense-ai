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

def save_job_description(user_id: int, raw_text: str, company_name: str = None, role_title: str = None) -> int:
    """
    Inserts a new job description row for a given user.
    Returns the new jd_id.
    """
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO job_descriptions (user_id, raw_text, company_name, role_title) VALUES (?, ?, ?, ?)",
        (user_id, raw_text, company_name, role_title)
    )
    conn.commit()
    jd_id = cursor.lastrowid
    conn.close()
    return jd_id


def get_job_descriptions_for_user(user_id: int) -> list:
    """
    Returns all JDs a user has saved, most recent first.
    """
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM job_descriptions WHERE user_id = ? ORDER BY uploaded_at DESC",
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def save_analysis(user_id: int, resume_id: int, jd_id: int = None,
                   ats_score: float = None, ats_breakdown: dict = None,
                   similarity_score: float = None, missing_skills: list = None,
                   matched_skills: list = None, ai_review: str = None,
                   interview_questions: list = None, cover_letter: str = None,
                   career_recommendations: dict = None) -> int:
    """
    Inserts a new analysis row. Every field except user_id and resume_id
    is optional, since analysis happens incrementally across several
    pages (ATS score first, then similarity, then AI review, etc.) -
    we'll UPDATE this row as more data becomes available (see update_analysis below).
    Returns the new analysis_id.
    """
    conn = get_connection()
    cursor = conn.execute(
        """INSERT INTO analyses
           (user_id, resume_id, jd_id, ats_score, ats_breakdown, similarity_score,
            missing_skills, matched_skills, ai_review, interview_questions,
            cover_letter, career_recommendations)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (user_id, resume_id, jd_id, ats_score,
         json.dumps(ats_breakdown) if ats_breakdown else None,
         similarity_score,
         json.dumps(missing_skills) if missing_skills else None,
         json.dumps(matched_skills) if matched_skills else None,
         ai_review,
         json.dumps(interview_questions) if interview_questions else None,
         cover_letter,
         json.dumps(career_recommendations) if career_recommendations else None)
    )
    conn.commit()
    analysis_id = cursor.lastrowid
    conn.close()
    return analysis_id


def update_analysis(analysis_id: int, **fields) -> None:
    """
    Updates specific fields of an existing analysis row.
    Usage: update_analysis(5, ai_review="...", interview_questions=[...])
    JSON-serializable fields (dicts/lists) are automatically converted.
    """
    if not fields:
        return

    json_fields = {"ats_breakdown", "missing_skills", "matched_skills",
                    "interview_questions", "career_recommendations"}

    set_clauses = []
    values = []
    for key, value in fields.items():
        set_clauses.append(f"{key} = ?")
        if key in json_fields and value is not None:
            values.append(json.dumps(value))
        else:
            values.append(value)

    values.append(analysis_id)  # for the WHERE clause

    conn = get_connection()
    conn.execute(
        f"UPDATE analyses SET {', '.join(set_clauses)} WHERE analysis_id = ?",
        values
    )
    conn.commit()
    conn.close()


def get_analyses_for_user(user_id: int) -> list:
    """Returns all analyses for a user, most recent first."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM analyses WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]