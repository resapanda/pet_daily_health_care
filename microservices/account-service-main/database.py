import sqlite3

USERS_DB = 'users.db'

# Initializes users database if one doesn't exist
def init_db():
    conn = sqlite3.connect(USERS_DB, timeout = 10)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

# Resets database for testing
def reset_db():
    conn = sqlite3.connect(USERS_DB, timeout=10)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM Users')
    cursor.execute('DELETE FROM sqlite_sequence WHERE name="Users"')

    conn.commit()
    conn.close()

    print("Database cleared for testing.")

if __name__ == "__main__":
    init_db()
