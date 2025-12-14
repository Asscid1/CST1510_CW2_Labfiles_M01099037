class SecurityIncident:
    """
    Represents a Security Incident entity in the system.
    """

    def __init__(self, incident_id, incident_type, severity, status, description):
        """Initializes the SecurityIncident object."""
        self.id = incident_id
        self.incident_type = incident_type
        self.severity = severity
        self.status = status
        self.description = description

    def update_status(self, new_status):
        """Updates the status attribute of the incident."""
        self.status = new_status
        # In a full OOP app, this method would also call the Manager to update the DB.

    def get_severity_level(self):
        """Converts severity string to an integer level for comparison/sorting."""
        levels = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}
        return levels.get(self.severity, 0)

    def __str__(self):
        """Returns a string representation of the incident object."""
        return f"Incident {self.id} | Type: {self.incident_type} | Severity: {self.severity} | Status: {self.status}"
