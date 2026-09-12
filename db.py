import os
import sqlite3
from pathlib import Path

DB_PATH = Path(os.environ.get('DATABASE_PATH', Path(__file__).parent / 'academy.db'))


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS apartments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            slug TEXT NOT NULL UNIQUE,
            description TEXT NOT NULL DEFAULT '',
            features TEXT NOT NULL DEFAULT '',
            image_filename TEXT NOT NULL DEFAULT '',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS enquiries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT DEFAULT '',
            move_date TEXT DEFAULT '',
            applicant_type TEXT DEFAULT 'student',
            apartment_type TEXT DEFAULT 'unsure',
            message TEXT DEFAULT '',
            contacted INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS login_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            ip_address TEXT DEFAULT '',
            success INTEGER NOT NULL DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    conn.commit()

    count = conn.execute('SELECT COUNT(*) FROM apartments').fetchone()[0]
    if count == 0:
        conn.executemany(
            '''INSERT INTO apartments (name, slug, description, features, image_filename)
               VALUES (?,?,?,?,?)''',
            [
                (
                    "Studio Apartment", "studio",
                    "A self-contained space with its own kitchen and bathroom, a full bed, "
                    "desk and storage built in.",
                    "Fully furnished, Private kitchen & bathroom, Bills included",
                    "apartment-studio.jpg",
                ),
                (
                    "One-Bedroom Apartment", "onebed",
                    "A larger layout with a separate living area, suited to those who want "
                    "more room to settle in or study.",
                    "Fully furnished, Separate living area, Bills included",
                    "apartment-onebed.jpg",
                ),
            ],
        )
        conn.commit()
    conn.close()
