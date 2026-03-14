import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'shuttlego.db')
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), '..', 'sql', 'schema.sql')


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    with open(SCHEMA_PATH, 'r') as f:
        conn.executescript(f.read())

    # Set real hashed passwords for seed users
    admin_pw = generate_password_hash('admin123')
    user_pw  = generate_password_hash('user123')
    conn.execute("UPDATE users SET password=? WHERE username='admin'", (admin_pw,))
    conn.execute("UPDATE users SET password=? WHERE username='anand'", (user_pw,))
    conn.commit()
    conn.close()
    print("[DB] Initialized successfully.")
