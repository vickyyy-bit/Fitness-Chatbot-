import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

# Database setup
def init_db():
    conn = sqlite3.connect('fitness.db')
    c = conn.cursor()
    
    # Create users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    
    # Create workout_preferences table
    c.execute('''
        CREATE TABLE IF NOT EXISTS workout_preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            goal TEXT NOT NULL,
            target_muscle TEXT NOT NULL,
            location TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Add a new user
def add_user(username, email, password):
    conn = sqlite3.connect('fitness.db')
    c = conn.cursor()
    password_hash = generate_password_hash(password)
    c.execute('INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)', (username, email, password_hash))
    conn.commit()
    conn.close()

# Authenticate a user
def authenticate_user(username, password):
    conn = sqlite3.connect('fitness.db')
    c = conn.cursor()
    c.execute('SELECT password_hash FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    conn.close()
    if user and check_password_hash(user[0], password):
        return True
    return False

# Save workout preferences
def save_workout_preferences(user_id, goal, target_muscle, location):
    conn = sqlite3.connect('fitness.db')
    c = conn.cursor()
    c.execute('INSERT INTO workout_preferences (user_id, goal, target_muscle, location) VALUES (?, ?, ?, ?)', 
              (user_id, goal, target_muscle, location))
    conn.commit()
    conn.close()

# Get user ID by username
def get_user_id(username):
    conn = sqlite3.connect('fitness.db')
    c = conn.cursor()
    c.execute('SELECT id FROM users WHERE username = ?', (username,))
    user_id = c.fetchone()
    conn.close()
    return user_id[0] if user_id else None