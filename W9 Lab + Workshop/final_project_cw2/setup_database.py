"""
Database setup script
Run this FIRST to create the database and load all data.
"""

from app.data.db import connect_database, load_csv_to_table
from app.data.schema import create_all_tables
from app.services.user_service import migrate_users_from_file


def setup_database_complete():
    """
    Complete database setup:
    1. Connect to database
    2. Create all tables
    3. Migrate users from users.txt
    4. Load CSV data for all domains
    5. Verify setup
    """
    print("\n" + "=" * 70)
    print("🚀 MULTI-DOMAIN INTELLIGENCE PLATFORM - DATABASE SETUP")
    print("=" * 70)

    # Step 1: Connect
    print("\n[1/5] 📡 Connecting to database...")
    conn = connect_database()
    print("      ✅ Connected to intelligence_platform.db")

    # Step 2: Create tables
    print("\n[2/5] 📊 Creating database tables...")
    create_all_tables(conn)
    print("      ✅ All tables created successfully")

    # Step 3: Migrate users
    print("\n[3/5] 👥 Migrating users from users.txt...")
    # Passing conn to migrate_users_from_file to ensure it uses the open connection
    user_count = migrate_users_from_file(conn)
    if user_count > 0:
        print(f"      ✅ Migrated {user_count} users")
    else:
        print("      ℹ️  No new users to migrate (or file not found)")

    # Step 4: Load CSV data
    print("\n[4/5] 📁 Loading CSV data...")

    # using load_csv_to_table directly from db.py
    incidents_count = load_csv_to_table(conn, "cyber_incidents.csv", "cyber_incidents")
    datasets_count = load_csv_to_table(
        conn, "datasets_metadata.csv", "datasets_metadata"
    )
    tickets_count = load_csv_to_table(conn, "it_tickets.csv", "it_tickets")

    total_rows = incidents_count + datasets_count + tickets_count
    print(f"\n      ✅ Total new records loaded: {total_rows:,}")

    # Step 5: Verify
    print("\n[5/5] ✔️  Verifying database setup...")
    cursor = conn.cursor()

    tables = ["users", "cyber_incidents", "datasets_metadata", "it_tickets"]
    print("\n      📋 Database Summary:")
    print(f"      {'Table':<30} {'Row Count':<15}")
    print("      " + "-" * 45)

    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"      {table:<30} {count:,}")
        except Exception as e:
            print(f"      {table:<30} Error: {e}")

    conn.close()

    print("\n" + "=" * 70)
    print("🎉 DATABASE SETUP COMPLETE!")
    print("=" * 70)
    print("You can now run 'python main.py' to test logic, or 'streamlit run Home.py'")


if __name__ == "__main__":
    setup_database_complete()
