"""
IT Tickets CRUD operations
Functions for managing IT support tickets
"""

import pandas as pd
from pathlib import Path

def insert_ticket(conn, ticket_id, priority, status, category, subject, description, created_date, resolved_date=None, assigned_to=None):
    """
    Insert a new IT ticket.
    
    Args:
        conn: Database connection
        ticket_id: Unique ticket identifier
        priority: Priority level
        status: Current status
        category: Ticket category
        subject: Subject line
        description: Detailed description
        created_date: Creation date
        resolved_date: Resolution date (optional)
        assigned_to: Assigned team/person (optional)
        
    Returns:
        int: ID of newly inserted ticket
    """
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO it_tickets 
        (ticket_id, priority, status, category, subject, description, created_date, resolved_date, assigned_to)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (ticket_id, priority, status, category, subject, description, created_date, resolved_date, assigned_to))
    conn.commit()
    return cursor.lastrowid

def get_all_tickets(conn):
    """
    Get all tickets as DataFrame.
    
    Returns:
        pandas.DataFrame: All tickets
    """
    df = pd.read_sql_query(
        "SELECT * FROM it_tickets ORDER BY id DESC",
        conn
    )
    return df

def get_tickets_by_priority(conn, priority):
    """
    Get tickets filtered by priority.
    
    Args:
        priority: Priority level to filter by
        
    Returns:
        pandas.DataFrame: Filtered tickets
    """
    df = pd.read_sql_query(
        "SELECT * FROM it_tickets WHERE priority = ? ORDER BY id DESC",
        conn,
        params=(priority,)
    )
    return df

def get_tickets_by_status(conn, status):
    """
    Get tickets filtered by status.
    
    Args:
        status: Status to filter by
        
    Returns:
        pandas.DataFrame: Filtered tickets
    """
    df = pd.read_sql_query(
        "SELECT * FROM it_tickets WHERE status = ? ORDER BY id DESC",
        conn,
        params=(status,)
    )
    return df

def update_ticket_status(conn, ticket_id, new_status, resolved_date=None):
    """
    Update ticket status.
    
    Args:
        ticket_id: Ticket ID to update
        new_status: New status value
        resolved_date: Resolution date (if resolved)
        
    Returns:
        bool: True if successful
    """
    cursor = conn.cursor()
    
    if resolved_date:
        cursor.execute(
            "UPDATE it_tickets SET status = ?, resolved_date = ? WHERE ticket_id = ?",
            (new_status, resolved_date, ticket_id)
        )
    else:
        cursor.execute(
            "UPDATE it_tickets SET status = ? WHERE ticket_id = ?",
            (new_status, ticket_id)
        )
    
    conn.commit()
    return cursor.rowcount > 0

def delete_ticket(conn, ticket_id):
    """
    Delete a ticket.
    
    Args:
        ticket_id: Ticket ID to delete
        
    Returns:
        bool: True if successful
    """
    cursor = conn.cursor()
    cursor.execute("DELETE FROM it_tickets WHERE ticket_id = ?", (ticket_id,))
    conn.commit()
    return cursor.rowcount > 0

def load_tickets_from_csv(conn, csv_path="DATA/it_tickets.csv"):
    """
    Load tickets from CSV file.
    
    Args:
        conn: Database connection
        csv_path: Path to CSV file
        
    Returns:
        int: Number of rows loaded
    """
    path = Path(csv_path)
    
    if not path.exists():
        print(f"⚠️  Warning: {csv_path} not found.")
        return 0
    
    df = pd.read_sql_query("SELECT COUNT(*) as count FROM it_tickets", conn)
    existing_count = df.iloc[0]['count']
    
    if existing_count > 0:
        print(f"ℹ️  {existing_count} tickets already in database. Skipping CSV load.")
        return 0
    
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    
    print(f"📊 Loading {len(df)} tickets from CSV...")
    df.to_sql('it_tickets', conn, if_exists='append', index=False)
    
    print(f"✅ Loaded {len(df)} tickets into database")
    return len(df)

def get_ticket_statistics(conn):
    """
    Get statistical summary of tickets.
    
    Returns:
        dict: Statistics dictionary
    """
    cursor = conn.cursor()
    
    stats = {}
    
    # Total tickets
    cursor.execute("SELECT COUNT(*) FROM it_tickets")
    stats['total'] = cursor.fetchone()[0]
    
    # By priority
    cursor.execute("""
        SELECT priority, COUNT(*) as count 
        FROM it_tickets 
        GROUP BY priority
    """)
    stats['by_priority'] = dict(cursor.fetchall())
    
    # By status
    cursor.execute("""
        SELECT status, COUNT(*) as count 
        FROM it_tickets 
        GROUP BY status
    """)
    stats['by_status'] = dict(cursor.fetchall())
    
    # By category
    cursor.execute("""
        SELECT category, COUNT(*) as count 
        FROM it_tickets 
        GROUP BY category
        ORDER BY count DESC
        LIMIT 5
    """)
    stats['top_categories'] = dict(cursor.fetchall())
    
    return stats
