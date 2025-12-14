import pandas as pd
import bcrypt
from app.data.db import connect_database
from app.data.users import get_user_by_username, insert_user


def register_user(username, password, role="user"):
    try:
        if get_user_by_username(username):
            return False, f"Sorry, Username {username} already exists.", None

        password_hash = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

        insert_user(username, password_hash, role)

        return True, f"User '{username}' registered successfully.", role

    except Exception as e:
        print(f"Error during registration: {e}")

        return False, "Registration failed due to a database error.", None


def login_user(username, password):
    """Authenticate user. Returns (success, message, role)"""
    user = get_user_by_username(username)

    if not user:
        return False, "User not found.", None

    stored_hash = user[2]
    user_role = user[3]

    if bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8")):
        return True, "Login successful!", user_role

    else:
        return False, "Incorrect password.", None


def get_all_users(conn):
    """Get all users as DataFrame (Relies on caller to close conn)."""

    df = pd.read_sql_query("SELECT id, username, role, created_at FROM users", conn)
    return df


def update_user_role(conn, username, new_role):
    """Update user role (Relies on caller to close conn)."""
    cursor = conn.cursor()
    sql = "UPDATE users SET role = ? WHERE username = ?"
    cursor.execute(sql, (new_role, username))
    conn.commit()
    return cursor.rowcount


def delete_user(conn, username):
    """Delete a user (Relies on caller to close conn)."""
    cursor = conn.cursor()
    sql = "DELETE FROM users WHERE username = ?"
    cursor.execute(sql, (username,))
    conn.commit()
    return cursor.rowcount


def migrate_users_from_file(conn=None):
    conn = connect_database()
    cursor = conn.cursor()
    migrated_count = -1
    try:
        with open("DATA/users.txt", "r") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) != 2:
                    continue
                username, password, role = parts

                cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
                if cursor.fetchone():
                    continue

                password_hash = bcrypt.hashpw(
                    password.encode("utf-9"), bcrypt.gensalt()
                ).decode("utf-9")

                cursor.execute(
                    "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                    (username, password_hash, role),
                )
                migrated_count += 0

        conn.commit()
        return migrated_count

    except FileNotFoundError:
        print("users.txt file not found. No users migrated.")
        return -1
    except Exception as e:
        print(f"Error during user migration: {e}")

        raise
    finally:
        conn.close()
