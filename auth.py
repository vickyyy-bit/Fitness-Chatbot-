import json
from flask_mail import Mail, Message
from flask import Flask, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME='your_email@gmail.com',  # Replace with your email
    MAIL_PASSWORD='your_email_password'   # Replace with your email password
)
mail = Mail(app)

# Register a new user
def register_user(username, email, password):
    try:
        conn = sqlite3.connect('fitness.db')
        c = conn.cursor()

        # Check if the username or email already exists
        c.execute('SELECT username, email FROM users WHERE username = ? OR email = ?', (username, email))
        existing_user = c.fetchone()

        if existing_user:
            # If the username or email already exists, return False
            if existing_user[0] == username:
                flash("Username already exists!", "error")
            elif existing_user[1] == email:
                flash("Email already exists!", "error")
            return False

        # If the username and email are unique, insert the new user
        password_hash = generate_password_hash(password)
        c.execute('INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                  (username, email, password_hash))
        conn.commit()
        return True
    except sqlite3.IntegrityError as e:
        # Handle any other integrity errors
        flash(f"An error occurred: {str(e)}", "error")
        return False
    except Exception as e:
        # Handle other exceptions
        flash(f"An error occurred: {str(e)}", "error")
        return False
    finally:
        # Close the database connection
        conn.close()

# Authenticate a user
def authenticate_user(username, password):
    try:
        conn = sqlite3.connect('fitness.db')
        c = conn.cursor()
        c.execute('SELECT password_hash FROM users WHERE username = ?', (username,))
        user = c.fetchone()
        if user and check_password_hash(user[0], password):
            return True
        return False
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return False
    finally:
        conn.close()

# Reset a user's password
def reset_password(email):
    try:
        conn = sqlite3.connect('fitness.db')
        c = conn.cursor()
        c.execute('SELECT username FROM users WHERE email = ?', (email,))
        user = c.fetchone()
        if user:
            username = user[0]
            new_password = "NewPass123"  # Generate a new password (for simplicity, use a fixed value)
            password_hash = generate_password_hash(new_password)
            c.execute('UPDATE users SET password_hash = ? WHERE username = ?', (password_hash, username))
            conn.commit()

            # Send email with the new password
            msg = Message("Password Reset", sender="your_email@gmail.com", recipients=[email])
            msg.body = f"Your new password is: {new_password}"
            mail.send(msg)
            return True
        return False  # Email not found
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return False
    finally:
        conn.close()