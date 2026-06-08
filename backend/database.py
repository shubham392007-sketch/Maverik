import sqlite3
import os
from datetime import datetime

DB_PATH = "maverik.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create History Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            command TEXT NOT NULL,
            action_type TEXT,
            status TEXT,
            execution_time REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create Chat Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            action_type TEXT,
            status TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create Settings Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    
    # Create File Index Table for Maverik Search
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS file_index (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            path TEXT UNIQUE NOT NULL,
            extension TEXT,
            size_bytes INTEGER,
            modified_timestamp REAL,
            is_folder BOOLEAN DEFAULT 0
        )
    ''')
    
    # Create Custom Apps Table for App Learning
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS custom_apps (
            app_name TEXT PRIMARY KEY,
            path TEXT NOT NULL
        )
    ''')
    
    # Create Favorites Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS favorites (
            name TEXT PRIMARY KEY,
            path TEXT NOT NULL
        )
    ''')
    
    # Create File Stats Table for Recent/Most Opened
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS file_stats (
            path TEXT PRIMARY KEY,
            open_count INTEGER DEFAULT 1,
            last_opened REAL
        )
    ''')
    
    # Create indexes for faster searching
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_filename ON file_index(filename)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_extension ON file_index(extension)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_is_folder ON file_index(is_folder)')
    
    conn.commit()
    conn.close()

# Helper functions
def add_chat_message(role: str, content: str, action_type: str = None, status: str = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chat (role, content, action_type, status) VALUES (?, ?, ?, ?)",
        (role, content, action_type, status)
    )
    conn.commit()
    conn.close()

def get_chat_history(limit=50):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM chat ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in reversed(rows)]

def clear_chat_history():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat")
    conn.commit()
    conn.close()

def add_command_history(command: str, action_type: str, status: str, execution_time: float):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO history (command, action_type, status, execution_time) VALUES (?, ?, ?, ?)",
        (command, action_type, status, execution_time)
    )
    conn.commit()
    conn.close()

def get_command_history(limit=50):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM history ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in reversed(rows)]

def clear_command_history():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM history")
    conn.commit()
    conn.close()

def set_setting(key: str, value: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
        (key, value)
    )
    conn.commit()
    conn.close()

def get_setting(key: str, default: str = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row['value'] if row else default

def add_custom_app(app_name: str, path: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO custom_apps (app_name, path) VALUES (?, ?)",
        (app_name.lower(), path)
    )
    conn.commit()
    conn.close()

def get_custom_app_path(app_name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT path FROM custom_apps WHERE app_name = ?", (app_name.lower(),))
    row = cursor.fetchone()
    conn.close()
    return row['path'] if row else None

def add_favorite(name: str, path: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO favorites (name, path) VALUES (?, ?)",
        (name.lower(), path)
    )
    conn.commit()
    conn.close()

def get_favorite(name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT path FROM favorites WHERE name = ?", (name.lower(),))
    row = cursor.fetchone()
    conn.close()
    return row['path'] if row else None
