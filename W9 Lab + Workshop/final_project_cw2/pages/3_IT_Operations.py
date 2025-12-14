import streamlit as st
import plotly.express as px
from datetime import datetime

from app.data.tickets import (
    get_all_tickets,
    insert_ticket,
    update_ticket_status,
    delete_ticket,
    get_ticket_statistics,
)

st.set_page_config(page_title="IT Operations Dashboard", page_icon="⚙️", layout="wide")

# ==================== AUTHENTICATION GUARD ====================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.error("🔒 You must be logged in to view this page")
    if st.button("Go to Login"):
        st.switch_page("Home.py")
    st.stop()

# ==================== DASHBOARD CONTENT ====================
st.title("⚙️ IT Operations Dashboard")
st.markdown(
    f"**Welcome, {st.session_state.username}** | Role: *{st.session_state.role}*"
)
st.divider()

with st.sidebar:
    st.header("Controls")

    priority_filter = st.multiselect(
        "Filter by Priority",
        ["Low", "Medium", "High", "Critical"],
        default=["Low", "Medium", "High", "Critical"],
    )

    status_filter = st.multiselect(
        "Filter by Status",
        ["Open", "In Progress", "Resolved", "Closed", "On Hold"],
        default=["Open", "In Progress", "Resolved", "Closed", "On Hold"],
    )

    st.divider()
    st.subheader("📍 Navigate")
    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("Home.py")
    if st.button("🛡️ Cyber Incidents", use_container_width=True):
        st.switch_page("pages/1_Cyber_Incidents.py")
    if st.button("📊 Data Science", use_container_width=True):
        st.switch_page("pages/2_Data_Science.py")

# ==================== SYSTEM HEALTH METRICS ====================
st.subheader("🖥️ System Health")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("CPU Usage", "67%", delta="+5%")
with col2:
    st.metric("Memory", "8.2 GB", delta="+0.3 GB")
with col3:
    st.metric("Disk Usage", "72%", delta="+2%")
with col4:
    st.metric("Uptime", "99.8%", delta="+0.1%")

st.divider()

# ==================== TICKET METRICS ====================

st.subheader("Ticket Metrics")

try:
    stats = get_ticket_statistics()

    priority_lookup_map = {
        item["priority"]: item["count"] for item in stats["by_priority"]
    }
    status_lookup_map = {item["status"]: item["count"] for item in stats["by_status"]}

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Tickets", f"{stats['total']:,}")

    with col2:
        critical_count = priority_lookup_map.get("Critical", 0)
        st.metric(
            "Critical",
            critical_count,
            delta=f"+{critical_count}" if critical_count > 0 else "0",
        )

    with col3:
        open_count = status_lookup_map.get("Open", 0)
        st.metric("Open", open_count)

    with col4:
        resolved_count = status_lookup_map.get("Resolved", 0)
        st.metric("Resolved", resolved_count)

except Exception as e:
    st.error(f"Error loading statistics: {e}")

st.divider()

# ==================== VISUALIZATIONS ====================
try:
    df = get_all_tickets()

    if len(df) > 0:
        # Apply filters
        filtered_df = df[
            (df["priority"].isin(priority_filter)) & (df["status"].isin(status_filter))
        ]

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📊 Tickets by Priority")
            priority_counts = filtered_df["priority"].value_counts()
            fig1 = px.bar(
                x=priority_counts.index,
                y=priority_counts.values,
                labels={"x": "Priority", "y": "Count"},
                color=priority_counts.index,
                color_discrete_map={
                    "Critical": "#DC143C",
                    "High": "#FF6347",
                    "Medium": "#FFA500",
                    "Low": "#90EE90",
                },
            )
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            st.subheader("Status Distribution")
            status_counts = filtered_df["status"].value_counts()
            fig2 = px.pie(
                values=status_counts.values, names=status_counts.index, hole=0.4
            )
            st.plotly_chart(fig2, use_container_width=True)

        # Tickets by category
        st.subheader("📈 Top Categories")
        category_counts = filtered_df["category"].value_counts().head(10)
        fig3 = px.bar(
            x=category_counts.values,
            y=category_counts.index,
            orientation="h",
            labels={"x": "Count", "y": "Category"},
            color=category_counts.values,
            color_continuous_scale="Teal",
        )
        st.plotly_chart(fig3, use_container_width=True)

        st.divider()

        # ==================== TICKET TABLE ====================
        st.subheader("All Tickets")

        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"Showing {len(filtered_df):,} of {len(df):,} tickets")
        with col2:
            rows_to_show = st.selectbox("Rows per page", [10, 25, 50, 100], index=1)

        st.dataframe(
            filtered_df.head(rows_to_show), use_container_width=True, hide_index=True
        )

        st.divider()

        # ==================== CREATE NEW TICKET ====================
        st.subheader("➕ Create New Ticket")

        with st.form("new_ticket_form"):
            col1, col2 = st.columns(2)

            with col1:
                # Generate ticket ID
                max_id_str = df["ticket_id"].str.extract(r"TKT-(\d+)")[0].max()
                max_id = (
                    int(max_id_str) if max_id_str and str(max_id_str) != "nan" else 0
                )
                new_ticket_id = f"TKT-{str(max_id + 1).zfill(6)}"
                st.text_input("Ticket ID", value=new_ticket_id, disabled=True)

                ticket_category = st.selectbox(
                    "Category",
                    [
                        "Hardware",
                        "Software",
                        "Network",
                        "Access",
                        "Email",
                        "Printer",
                        "Database",
                        "Server",
                        "Security",
                        "Other",
                    ],
                )
                ticket_priority = st.selectbox(
                    "Priority", ["Low", "Medium", "High", "Critical"]
                )

            with col2:
                ticket_status = st.selectbox(
                    "Status", ["Open", "In Progress", "Resolved", "Closed", "On Hold"]
                )
                ticket_assigned = st.text_input("Assigned To", value="Support Team")
                ticket_date = st.date_input("Created Date", value=datetime.now())

            ticket_subject = st.text_input(
                "Subject", placeholder="Brief description of the issue"
            )
            ticket_description = st.text_area(
                "Description", placeholder="Detailed description..."
            )

            submitted = st.form_submit_button("🎫 Create Ticket", type="primary")

            if submitted:
                if ticket_subject and ticket_description:
                    try:
                        new_id = insert_ticket(
                            new_ticket_id,
                            ticket_priority,
                            ticket_status,
                            ticket_category,
                            ticket_subject,
                            ticket_description,
                            ticket_date.strftime("%Y-%m-%d"),
                            None,
                            ticket_assigned,
                        )
                        st.success(f"✅ Ticket {new_ticket_id} created successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
                else:
                    st.error("⚠️ Please fill in all required fields")

        # ==================== MANAGE TICKETS ====================
        st.divider()
        st.subheader("Manage Tickets")

        if len(df) > 0:
            ticket_options = [
                f"{row['ticket_id']}: {row['subject']}"
                for _, row in df.head(50).iterrows()
            ]
            selected_ticket = st.selectbox("Select Ticket", ticket_options)

            if selected_ticket:
                selected_ticket_id = selected_ticket.split(":")[0]
                ticket_data = df[df["ticket_id"] == selected_ticket_id].iloc[0]

                col1, col2 = st.columns(2)

                with col1:
                    st.write("**Update Ticket**")
                    with st.form(f"update_form_{selected_ticket_id}"):
                        new_status = st.selectbox(
                            "New Status",
                            ["Open", "In Progress", "Resolved", "Closed", "On Hold"],
                            index=[
                                "Open",
                                "In Progress",
                                "Resolved",
                                "Closed",
                                "On Hold",
                            ].index(ticket_data["status"]),
                        )

                        resolved_date = None
                        if new_status in ["Resolved", "Closed"]:
                            resolved_date = st.date_input(
                                "Resolved Date", value=datetime.now()
                            ).strftime("%Y-%m-%d")

                        if st.form_submit_button("💾 Update"):
                            try:
                                if update_ticket_status(
                                    selected_ticket_id, new_status, resolved_date
                                ):
                                    st.success("✅ Ticket updated!")
                                    st.rerun()
                                else:
                                    st.error("❌ Update failed")
                            except Exception as e:
                                st.error(f"❌ Error: {e}")

                with col2:
                    st.write("**Delete Ticket**")
                    st.warning(f"⚠️ Delete: {ticket_data['subject']}?")
                    if st.button(
                        "🗑️ Delete Ticket",
                        type="primary",
                        key=f"delete_{selected_ticket_id}",
                    ):
                        try:
                            if delete_ticket(selected_ticket_id):
                                st.success("✅ Ticket deleted!")
                                st.rerun()
                            else:
                                st.error("❌ Delete failed")
                        except Exception as e:
                            st.error(f"❌ Error: {e}")
        else:
            st.info("No tickets to manage")
    else:
        st.info("📭 No tickets found. Create your first ticket above!")

except Exception as e:
    st.error(f"❌ Error loading tickets: {e}")
    st.info("💡 Make sure you've run main.py to initialize the database")

st.divider()
if st.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.switch_page("Home.py")
