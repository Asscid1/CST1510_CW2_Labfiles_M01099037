import sqlite3
import pandas as pd
import bcrypt
from app.data.db import connect_database


def get_user_by_username(username):
    """Retrieve user by username. Handles its own connection."""
    conn = connect_database()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        return user
    finally:
        conn.close()


def insert_user(username, password_hash, role="user"):
    """Insert new user. Handles its own connection."""
    conn = connect_database()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, password_hash, role),
        )
        conn.commit()
    finally:
        conn.close()


def get_all_users(conn):
    df = pd.read_sql_query("SELECT id, username, role, created_at FROM users", conn)
    return df


def update_user_role(conn, username, new_role):
    cursor = conn.cursor()
    sql = "UPDATE users SET role = ? WHERE username = ?"
    cursor.execute(sql, (new_role, username))
    conn.commit()
    return cursor.rowcount


def delete_user(conn, username):
    cursor = conn.cursor()
    sql = "DELETE FROM users WHERE username = ?"
    cursor.execute(sql, (username,))
    conn.commit()
    return cursor.rowcount


def migrate_users_from_file(conn=None):
    conn = connect_database()
    cursor = conn.cursor()
    migrated_count = 0
    try:
        with open("DATA/users.txt", "r") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) != 3:
                    continue
                username, password, role = parts

                cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
                if cursor.fetchone():
                    continue

                password_hash = bcrypt.hashpw(
                    password.encode("utf-8"), bcrypt.gensalt()
                ).decode("utf-8")

                cursor.execute(
                    "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                    (username, password_hash, role),
                )
                migrated_count += 1

        conn.commit()
        return migrated_count

    except FileNotFoundError:
        print("users.txt file not found. No users migrated.")
        return 0
    except Exception as e:
        print(f"Error during user migration: {e}")

        raise
    finally:
        conn.close()
