import streamlit as st
import plotly.express as px
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.data.db import connect_database
from app.data.cyber_incidents import (
    get_all_incidents,
    get_incidents_by_severity,
    get_incidents_by_status,
    insert_incident,
    update_incident_status,
    delete_incident,
    get_incident_statistics
)

# Page configuration
st.set_page_config(
    page_title="Cyber Incidents Dashboard",
    page_icon="🛡️",
    layout="wide"
)

# ==================== AUTHENTICATION GUARD ====================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.error("🔒 You must be logged in to view this page")
    if st.button("Go to Login"):
        st.switch_page("Home.py")
    st.stop()

# ==================== DASHBOARD CONTENT ====================
st.title("🛡️ Cybersecurity Incidents Dashboard")
st.markdown(f"**Welcome, {st.session_state.username}** | Role: *{st.session_state.role}*")
st.divider()

# Connect to database
conn = connect_database()

# Sidebar for filters and navigation
with st.sidebar:
    st.header("🎛️ Controls")
    
    # Filters
    severity_filter = st.multiselect(
        "Filter by Severity",
        ["Low", "Medium", "High", "Critical"],
        default=["Low", "Medium", "High", "Critical"]
    )
    
    status_filter = st.multiselect(
        "Filter by Status",
        ["Open", "In Progress", "Resolved", "Closed"],
        default=["Open", "In Progress", "Resolved", "Closed"]
    )
    
    st.divider()
    
    # Navigation
    st.subheader("📍 Navigate")
    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("Home.py")
    if st.button("📊 Data Science", use_container_width=True):
        st.switch_page("pages/2_Data_Science.py")
    if st.button("⚙️ IT Operations", use_container_width=True):
        st.switch_page("pages/3_IT_Operations.py")

# ==================== METRICS ====================
st.subheader("📊 Key Metrics")

# Get statistics from database
stats = get_incident_statistics(conn)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Incidents", f"{stats['total']:,}")
with col2:
    critical_count = stats['by_severity'].get('Critical', 0)
    st.metric("Critical", critical_count, delta=f"+{critical_count}" if critical_count > 0 else "0")
with col3:
    open_count = stats['by_status'].get('Open', 0)
    st.metric("Open", open_count)
with col4:
    resolved_count = stats['by_status'].get('Resolved', 0)
    st.metric("Resolved", resolved_count)

st.divider()

# ==================== VISUALIZATIONS ====================
# Get all incidents from database
df = get_all_incidents(conn)

# Apply filters
if len(df) > 0:
    filtered_df = df[
        (df['severity'].isin(severity_filter)) &
        (df['status'].isin(status_filter))
    ]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Incidents by Severity")
        severity_counts = filtered_df['severity'].value_counts()
        fig1 = px.bar(
            x=severity_counts.index,
            y=severity_counts.values,
            labels={'x': 'Severity', 'y': 'Count'},
            color=severity_counts.index,
            color_discrete_map={
                'Critical': '#DC143C',
                'High': '#FF6347',
                'Medium': '#FFA500',
                'Low': '#90EE90'
            }
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.subheader("📊 Status Distribution")
        status_counts = filtered_df['status'].value_counts()
        fig2 = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            hole=0.4
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    st.divider()
    
    # ==================== INCIDENT TABLE ====================
    st.subheader("📋 All Incidents")
    
    # Display options
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write(f"Showing {len(filtered_df):,} of {len(df):,} incidents")
    with col2:
        rows_to_show = st.selectbox("Rows per page", [10, 25, 50, 100], index=1)
    
    st.dataframe(
        filtered_df.head(rows_to_show),
        use_container_width=True,
        hide_index=True
    )
    
    st.divider()
    
    # ==================== CREATE NEW INCIDENT ====================
    st.subheader("➕ Add New Incident")
    
    with st.form("new_incident_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            incident_type = st.text_input("Incident Type", placeholder="e.g., Phishing, Malware, DDoS")
            incident_severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
            incident_status = st.selectbox("Status", ["Open", "In Progress", "Resolved", "Closed"])
        
        with col2:
            incident_date = st.date_input("Date", value=datetime.now())
            incident_description = st.text_area("Description", placeholder="Detailed description of the incident...")
        
        submitted = st.form_submit_button("🔒 Create Incident", type="primary")
        
        if submitted:
            if incident_type and incident_description:
                new_id = insert_incident(
                    conn,
                    incident_date.strftime("%Y-%m-%d"),
                    incident_type,
                    incident_severity,
                    incident_status,
                    incident_description,
                    st.session_state.username
                )
                st.success(f"✅ Incident #{new_id} created successfully!")
                st.rerun()
            else:
                st.error("⚠️ Please fill in all required fields")
    
    # ==================== UPDATE/DELETE INCIDENTS ====================
    st.divider()
    st.subheader("✏️ Manage Incidents")
    
    if len(df) > 0:
        # Select incident
        incident_options = [f"#{row['id']}: {row['incident_type']} - {row['severity']}" for _, row in df.head(50).iterrows()]
        selected_incident = st.selectbox("Select Incident to Manage", incident_options)
        
        if selected_incident:
            selected_id = int(selected_incident.split(":")[0].replace("#", ""))
            incident_data = df[df['id'] == selected_id].iloc[0]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Update Status**")
                with st.form(f"update_form_{selected_id}"):
                    new_status = st.selectbox(
                        "New Status",
                        ["Open", "In Progress", "Resolved", "Closed"],
                        index=["Open", "In Progress", "Resolved", "Closed"].index(incident_data['status'])
                    )
                    
                    if st.form_submit_button("💾 Update"):
                        if update_incident_status(conn, selected_id, new_status):
                            st.success("✅ Incident updated!")
                            st.rerun()
                        else:
                            st.error("❌ Update failed")
            
            with col2:
                st.write("**Delete Incident**")
                st.warning(f"⚠️ Delete: {incident_data['incident_type']}?")
                if st.button("🗑️ Delete", type="primary", key=f"delete_{selected_id}"):
                    if delete_incident(conn, selected_id):
                        st.success("✅ Incident deleted!")
                        st.rerun()
                    else:
                        st.error("❌ Delete failed")
    else:
        st.info("No incidents to manage")
else:
    st.info("📭 No incidents found. Create your first incident above!")

# Close database connection
conn.close()

# Footer
st.divider()
if st.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.switch_page("Home.py")