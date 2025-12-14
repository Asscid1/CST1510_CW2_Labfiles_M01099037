def create_users_table(conn):
    """Create the users table if it doesn't exist."""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'user'
    );
    """
    cursor = conn.cursor()
    cursor.execute(create_table_sql)
    conn.commit()


def create_cyber_incidents_table(conn):
    """Create cyber_incidents table."""
    cursor = conn.cursor()
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS cyber_incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            description TEXT,
            reported_by TEXT,
            date_reported TEXT,
            status TEXT DEFAULT 'Open'
    );
    """
    cursor.execute(create_table_sql)
    conn.commit()


def create_datasets_metadata_table(conn):
    """Create datasets_metadata table."""
    cursor = conn.cursor()
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS datasets_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dataset_name TEXT NOT NULL,
            category TEXT,
            source TEXT,
            last_updated TEXT,
            record_count INTEGER,
            file_size_mb REAL
    );
    """
    cursor.execute(create_table_sql)
    conn.commit()


def create_it_tickets_table(conn):
    """Create it_tickets table."""
    cursor = conn.cursor()
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS it_tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id TEXT NOT NULL,
            priority TEXT,
            status TEXT,
            category TEXT,
            subject TEXT,
            description TEXT,
            created_date TEXT,
            resolved_date TEXT,
            assigned_to TEXT
    );
    """
    cursor.execute(create_table_sql)
    conn.commit()


def create_all_tables(conn):
    """Create all tables."""
    create_users_table(conn)
    create_cyber_incidents_table(conn)
    create_datasets_metadata_table(conn)
    create_it_tickets_table(conn)
