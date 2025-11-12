"""
Initialize PrizePicks User Dashboard Database
Reads create_schema.sql and creates the SQLite database with all tables, indexes, and views
"""

import sqlite3
import os

# File paths - relative to project root
# This script is in backend/data_storage/
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))  # Go up 2 levels to project root
DATA_STORAGE_DIR = os.path.join(PROJECT_ROOT, 'backend', 'data_storage')

SCHEMA_FILE = os.path.join(DATA_STORAGE_DIR, 'create_schema.sql')
DATABASE_FILE = os.path.join(DATA_STORAGE_DIR, 'user_data.db')

def init_database():
    """
    Initialize the database by:
    1. Creating/connecting to user_data.db
    2. Reading the schema from create_schema.sql
    3. Executing all SQL statements to create tables, indexes, and views
    """
    
    print("=" * 60)
    print("🗄️  INITIALIZING PRIZEPICKS USER DATABASE")
    print("=" * 60)
    
    # Check if schema file exists
    if not os.path.exists(SCHEMA_FILE):
        print(f"❌ ERROR: Schema file not found at {SCHEMA_FILE}")
        print("Make sure create_schema.sql is in the same directory as this script")
        return False
    
    # Check if database already exists
    db_exists = os.path.exists(DATABASE_FILE)
    if db_exists:
        print(f"⚠️  WARNING: Database already exists at {DATABASE_FILE}")
        response = input("Do you want to DELETE and recreate it? (yes/no): ").strip().lower()
        if response == 'yes':
            os.remove(DATABASE_FILE)
            print("🗑️  Old database deleted")
        else:
            print("❌ Initialization cancelled")
            return False
    
    try:
        # Connect to database (creates file if it doesn't exist)
        print(f"\n📁 Creating database at: {DATABASE_FILE}")
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        # Read the schema file
        print(f"📖 Reading schema from: {SCHEMA_FILE}")
        with open(SCHEMA_FILE, 'r') as f:
            schema_sql = f.read()
        
        # Execute the schema
        print("🔨 Creating tables, indexes, and views...")
        cursor.executescript(schema_sql)
        
        # Commit changes
        conn.commit()
        
        # Verify tables were created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        
        print("\n✅ DATABASE INITIALIZED SUCCESSFULLY!")
        print("\n📊 Tables created:")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"   - {table[0]}: {count} rows")
        
        # Verify views were created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='view' ORDER BY name")
        views = cursor.fetchall()
        
        if views:
            print("\n👁️  Views created:")
            for view in views:
                print(f"   - {view[0]}")
        
        # Verify indexes were created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' ORDER BY name")
        indexes = cursor.fetchall()
        
        if indexes:
            print(f"\n🔍 Indexes created: {len(indexes)} total")
        
        print("\n" + "=" * 60)
        print("🎉 DATABASE READY FOR DATA!")
        print("=" * 60)
        print(f"\nNext step: Run seed_database.py to populate with mock data")
        
        # Close connection
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"\n❌ DATABASE ERROR: {e}")
        return False
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        return False

def get_database_info():
    """
    Display information about the existing database
    """
    if not os.path.exists(DATABASE_FILE):
        print(f"❌ Database not found at {DATABASE_FILE}")
        print("Run init_database() first to create the database")
        return
    
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    print("\n" + "=" * 60)
    print("📊 DATABASE INFORMATION")
    print("=" * 60)
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    
    print(f"\n📋 Tables ({len(tables)} total):")
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cursor.fetchone()[0]
        print(f"   {table[0]}: {count} rows")
    
    # Get all views
    cursor.execute("SELECT name FROM sqlite_master WHERE type='view' ORDER BY name")
    views = cursor.fetchall()
    
    if views:
        print(f"\n👁️  Views ({len(views)} total):")
        for view in views:
            print(f"   - {view[0]}")
    
    # Get database file size
    db_size = os.path.getsize(DATABASE_FILE)
    print(f"\n💾 Database size: {db_size:,} bytes ({db_size / 1024:.2f} KB)")
    
    conn.close()

if __name__ == "__main__":
    # Run the initialization
    success = init_database()
    
    if success:
        print("\n✨ You can now run seed_database.py to add mock data!")
    else:
        print("\n⚠️  Initialization failed. Please check the errors above.")