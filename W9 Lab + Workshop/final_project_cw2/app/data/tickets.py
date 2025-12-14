import pandas as pd
from pathlib import Path
from app.data.db import connect_database


def insert_ticket(
    ticket_id,
    priority,
    status,
    category,
    subject,
    description,
    created_date,
    resolved_date=None,
    assigned_to=None,
):
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO it_tickets 
        (ticket_id, priority, status, category, subject, description, created_date, resolved_date, assigned_to)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            ticket_id,
            priority,
            status,
            category,
            subject,
            description,
            created_date,
            resolved_date,
            assigned_to,
        ),
    )
    conn.commit()
    db_id = cursor.lastrowid
    conn.close()
    return db_id


def get_all_tickets():
    conn = connect_database()
    df = pd.read_sql_query("SELECT * FROM it_tickets ORDER BY id DESC", conn)
    conn.close()
    return df


def get_tickets_by_priority(priority):
    conn = connect_database()
    df = pd.read_sql_query(
        "SELECT * FROM it_tickets WHERE priority = ? ORDER BY id DESC",
        conn,
        params=(priority,),
    )
    conn.close()
    return df


def get_tickets_by_status(status):
    conn = connect_database()
    df = pd.read_sql_query(
        "SELECT * FROM it_tickets WHERE status = ? ORDER BY id DESC",
        conn,
        params=(status,),
    )
    conn.close()
    return df


def update_ticket_status(ticket_id, new_status, resolved_date=None):
    conn = connect_database()
    cursor = conn.cursor()

    if resolved_date:
        cursor.execute(
            "UPDATE it_tickets SET status = ?, resolved_date = ? WHERE ticket_id = ?",
            (new_status, resolved_date, ticket_id),
        )
    else:
        cursor.execute(
            "UPDATE it_tickets SET status = ? WHERE ticket_id = ?",
            (new_status, ticket_id),
        )

    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    return rows_affected > 0


def delete_ticket(ticket_id):
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM it_tickets WHERE ticket_id = ?", (ticket_id,))
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    return rows_affected > 0


def get_ticket_statistics():
    """Calculates and returns key metrics for the IT Tickets dashboard."""
    conn = connect_database()
    try:
        total_tickets_df = pd.read_sql_query("SELECT COUNT(id) FROM it_tickets", conn)
        total_tickets = total_tickets_df.iloc[0, 0] if not total_tickets_df.empty else 0

        open_tickets_df = pd.read_sql_query(
            "SELECT COUNT(id) FROM it_tickets WHERE status='Open'", conn
        )
        open_tickets = open_tickets_df.iloc[0, 0] if not open_tickets_df.empty else 0

        priority_counts_df = pd.read_sql_query(
            "SELECT priority, COUNT(*) as count FROM it_tickets GROUP BY priority", conn
        )
        by_priority = priority_counts_df.to_dict("records")

        category_counts_df = pd.read_sql_query(
            "SELECT category, COUNT(*) as count FROM it_tickets GROUP BY category", conn
        )
        by_category = category_counts_df.to_dict("records")

        status_counts_df = pd.read_sql_query(
            "SELECT status, COUNT(*) as count FROM it_tickets GROUP BY status", conn
        )
        by_status = status_counts_df.to_dict("records")

        return {
            "total": int(total_tickets),
            "open_tickets": int(open_tickets),
            "by_priority": by_priority,
            "by_category": by_category,
            "by_status": by_status,
        }

    except Exception as e:
        print(f"Error calculating ticket statistics: {e}")
        return {
            "total": 0,
            "open_tickets": 0,
            "by_priority": [],
            "by_category": [],
            "by_status": [],
        }
    finally:
        conn.close()
