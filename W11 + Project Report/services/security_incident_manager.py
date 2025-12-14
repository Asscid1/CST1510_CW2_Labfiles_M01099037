import pandas as pd
from app.data.db import connect_database
from models.security_incident import SecurityIncident


class SecurityIncidentManager:
    """
    Manages database operations and business logic related to Security Incidents.
    """

    def __init__(self, db_connector):
        """Initializes the manager with a database connector/function."""
        self.connect_db = db_connector

    def get_all_incidents(self):
        """Fetches all incidents and returns a list of SecurityIncident objects."""
        conn = self.connect_db()
        try:
            query = "SELECT id, incident_type, severity, status, description FROM cyber_incidents"
            df = pd.read_sql_query(query, conn)

            incidents = []
            for index, row in df.iterrows():
                incident = SecurityIncident(
                    incident_id=row["id"],
                    incident_type=row["incident_type"],
                    severity=row["severity"],
                    status=row["status"],
                    description=row["description"],
                )
                incidents.append(incident)
            return incidents
        except Exception as e:
            print(f"Error fetching all incidents: {e}")
            return []
        finally:
            conn.close()

    def get_incident_statistics(self):
        """
        Calculates and returns key metrics used by the dashboard.
        """
        conn = self.connect_db()
        try:
            total_df = pd.read_sql_query(
                "SELECT COUNT(id) AS total FROM cyber_incidents", conn
            )
            open_df = pd.read_sql_query(
                "SELECT COUNT(id) AS open_incidents FROM cyber_incidents WHERE status='Open'",
                conn,
            )
            severity_df = pd.read_sql_query(
                "SELECT severity, COUNT(*) as count FROM cyber_incidents GROUP BY severity",
                conn,
            )
            status_df = pd.read_sql_query(
                "SELECT status, COUNT(*) as count FROM cyber_incidents GROUP BY status",
                conn,
            )

            stats = {
                "total": int(total_df.iloc[0, 0]) if not total_df.empty else 0,
                "open_incidents": int(open_df.iloc[0, 0]) if not open_df.empty else 0,
                "by_severity": severity_df.to_dict("records"),
                "by_status": status_df.to_dict("records"),
            }
            return stats
        except Exception as e:
            print(f"Error calculating incident statistics: {e}")
            return {"total": 0, "open_incidents": 0, "by_severity": [], "by_status": []}
        finally:
            conn.close()

    def update_incident_status(self, incident_id, new_status):
        """
        Updates the status of a specific security incident.
        (Refactored from standalone function to class method)
        """
        conn = self.connect_db()
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

    def delete_incident(self, incident_id):
        """
        Deletes a specific security incident.
        (Refactored from standalone function to class method)
        """
        conn = self.connect_db()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM cyber_incidents WHERE id = ?", (incident_id,))
            conn.commit()
            rows_changed = cursor.rowcount
            return rows_changed
        finally:
            conn.close()
