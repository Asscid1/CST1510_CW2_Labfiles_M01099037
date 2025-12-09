"""
Database connection module
Handles SQLite database connections for the Multi-Domain Intelligence Platform
"""

import sqlite3
from pathlib import Path

# Database path
DATA_DIR = Path("DATA")
DB_PATH = Path("DATA") / "intelligence_platform.db"

def connect_database(db_path=DB_PATH):
    """
    Connect to the SQLite database.
    Creates the database file if it doesn't exist.
    
    Args:
        db_path: Path to the database file
        
    Returns:
        sqlite3.Connection: Database connection object
    """
    # Ensure DATA directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect(str(db_path))
    
    return conn

def close_connection(conn):
    """
    Close database connection safely.
    
    Args:
        conn: Database connection to close
    """
    if conn:
        conn.close()
