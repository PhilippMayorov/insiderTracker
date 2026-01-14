"""
Database migration script to add new market_info fields to trades table
Run this after updating the models to ensure database schema is up to date
"""
import sqlite3
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

DATABASE_PATH = "src/data/tracker.db"


def migrate_database():
    """Add new market_info columns to trades table"""
    print(f"Migrating database: {DATABASE_PATH}")
    
    # Connect to database
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Check if columns already exist
    cursor.execute("PRAGMA table_info(trades)")
    columns = [row[1] for row in cursor.fetchall()]
    
    new_columns = [
        ("market_question", "TEXT"),
        ("market_outcome", "TEXT"),
        ("market_tags", "TEXT"),
        ("market_target_price", "REAL"),
        ("market_resolved", "INTEGER"),
        ("market_is_winner", "INTEGER"),
        ("market_resolved_price", "REAL"),
    ]
    
    # Add missing columns
    added = 0
    for col_name, col_type in new_columns:
        if col_name not in columns:
            try:
                cursor.execute(f"ALTER TABLE trades ADD COLUMN {col_name} {col_type}")
                print(f"✅ Added column: {col_name}")
                added += 1
            except sqlite3.OperationalError as e:
                print(f"⚠️  Column {col_name} might already exist: {e}")
        else:
            print(f"✓ Column {col_name} already exists")
    
    # Commit changes
    conn.commit()
    conn.close()
    
    if added > 0:
        print(f"\n✅ Migration complete! Added {added} new columns.")
    else:
        print("\n✓ Database schema is already up to date.")


if __name__ == "__main__":
    migrate_database()
