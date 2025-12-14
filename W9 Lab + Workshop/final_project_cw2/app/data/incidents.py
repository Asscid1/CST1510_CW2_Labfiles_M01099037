import pandas as pd
from app.data.db import connect_database


def insert_incident(
    date_reported, incident_type, severity, status, description, reported_by=None
):
    """Insert new incident."""
    conn = connect_database()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO cyber_incidents 
            (date_reported, incident_type, severity, status, description, reported_by)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (date_reported, incident_type, severity, status, description, reported_by),
        )
        conn.commit()
        incident_id = cursor.lastrowid
        return incident_id
    except Exception as e:
        print(f"Error inserting incident: {e}")
        return None
    finally:
        conn.close()


def get_all_incidents():
    """Get all incidents as DataFrame. Handles its own connection."""
    conn = connect_database()
    try:
        df = pd.read_sql_query("SELECT * FROM cyber_incidents ORDER BY id DESC", conn)
        return df
    finally:
        conn.close()


def update_incident_status(incident_id, new_status):
    conn = connect_database()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE cyber_incidents SET status = ? WHERE id = ?",
            (new_status, incident_id),
        )
        conn.commit()
        rows_changed = cursor.rowcount
        return rows_changed
    finally:
        conn.close()


def delete_incident(incident_id):
    conn = connect_database()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cyber_incidents WHERE id = ?", (incident_id,))
        conn.commit()
        rows_changed = cursor.rowcount
        return rows_changed
    finally:
        conn.close()


def get_incidents_by_type_count(conn):
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT incident_type, COUNT(*) as count
        FROM cyber_incidents
        GROUP BY incident_type
        ORDER BY count DESC
        """
    )
    return pd.read_sql_query(cursor.statement, conn)


def get_incidents_by_severity_count(conn):
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT severity, COUNT(*) as count
        FROM cyber_incidents
        GROUP BY severity
        ORDER BY count DESC
        """
    )
    return pd.read_sql_query(cursor.statement, conn)


def get_incident_statistics():
    """Calculates and returns key metrics for the Cyber Incidents dashboard."""
    conn = connect_database()
    try:
        total_incidents_df = pd.read_sql_query(
            "SELECT COUNT(id) FROM cyber_incidents", conn
        )
        total_incidents = (
            total_incidents_df.iloc[0, 0] if not total_incidents_df.empty else 0
        )

        open_incidents_df = pd.read_sql_query(
            "SELECT COUNT(id) FROM cyber_incidents WHERE status='Open'", conn
        )
        open_incidents = (
            open_incidents_df.iloc[0, 0] if not open_incidents_df.empty else 0
        )

        top_severity_df = pd.read_sql_query(
            "SELECT severity, COUNT(*) as count FROM cyber_incidents GROUP BY severity ORDER BY count DESC LIMIT 1",
            conn,
        )
        top_severity = (
            top_severity_df["severity"].iloc[0] if not top_severity_df.empty else "N/A"
        )

        severity_counts_df = pd.read_sql_query(
            "SELECT severity, COUNT(*) as count FROM cyber_incidents GROUP BY severity",
            conn,
        )
        severity_counts = severity_counts_df.to_dict("records")

        status_counts_df = pd.read_sql_query(
            "SELECT status, COUNT(*) as count FROM cyber_incidents GROUP BY status",
            conn,
        )
        status_counts = status_counts_df.to_dict("records")

        return {
            "total": int(total_incidents),
            "open_incidents": int(open_incidents),
            "top_severity": top_severity,
            "by_severity": severity_counts,
            "by_status": status_counts,
        }
    except Exception as e:
        print(f"Error calculating incident statistics: {e}")
        return {
            "total_incidents": 0,
            "open_incidents": 0,
            "top_severity": "Error",
            "by_severity": [],
            "by_status": [],
        }
    finally:
        conn.close()
