"""
Database setup script
Run this once to create database and load all data
"""

from app.data.db import connect_database
from app.data.schema import create_all_tables
from app.data.users import migrate_users_from_file
from app.data.incidents import load_incidents_from_csv
from app.data.datasets import load_datasets_from_csv
from app.data.tickets import load_tickets_from_csv

def setup_database_complete():
    """
    Complete database setup:
    1. Connect to database
    2. Create all tables
    3. Migrate users from users.txt
    4. Load CSV data for all domains
    5. Verify setup
    """
    print("\n" + "="*70)
    print("🚀 MULTI-DOMAIN INTELLIGENCE PLATFORM - DATABASE SETUP")
    print("="*70)
    
    # Step 1: Connect
    print("\n[1/5] 📡 Connecting to database...")
    conn = connect_database()
    print("      ✅ Connected to intelligence_platform.db")
    
    # Step 2: Create tables
    print("\n[2/5] 📊 Creating database tables...")
    create_all_tables(conn)
    
    # Step 3: Migrate users
    print("\n[3/5] 👥 Migrating users from users.txt...")
    user_count = migrate_users_from_file(conn)
    if user_count > 0:
        print(f"      ✅ Migrated {user_count} users")
    else:
        print("      ℹ️  No new users to migrate")
    
    # Step 4: Load CSV data
    print("\n[4/5] 📁 Loading CSV data...")
    
    incidents_count = load_incidents_from_csv(conn)
    datasets_count = load_datasets_from_csv(conn)
    tickets_count = load_tickets_from_csv(conn)
    
    total_rows = incidents_count + datasets_count + tickets_count
    print(f"\n      ✅ Total new records loaded: {total_rows:,}")
    
    # Step 5: Verify
    print("\n[5/5] ✔️  Verifying database setup...")
    cursor = conn.cursor()
    
    tables = ['users', 'cyber_incidents', 'datasets_metadata', 'it_tickets']
    print("\n      📋 Database Summary:")
    print(f"      {'Table':<30} {'Row Count':<15}")
    print("      " + "-" * 45)
    
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"      {table:<30} {count:,}")
    
    conn.close()
    
    print("\n" + "="*70)
    print("🎉 DATABASE SETUP COMPLETE!")
    print("="*70)
    print("\n✅ Your database is ready!")
    print("📍 Location: DATA/intelligence_platform.db")
    print("\n🚀 Next steps:")
    print("   1. Run: streamlit run Home.py")
    print("   2. Login with your credentials")
    print("   3. Explore the dashboards!")
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    setup_database_complete()
