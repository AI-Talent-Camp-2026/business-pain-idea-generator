"""
Migration script to add selected_direction column to runs table
"""
import sqlite3
from src.config import logger

def migrate():
    """Add selected_direction column to runs table"""
    try:
        # Connect to database
        conn = sqlite3.connect('pain_to_idea.db')
        cursor = conn.cursor()

        # Check if column already exists
        cursor.execute("PRAGMA table_info(runs)")
        columns = [row[1] for row in cursor.fetchall()]

        if 'selected_direction' in columns:
            logger.info("Column 'selected_direction' already exists, skipping migration")
            return

        # Add new column
        logger.info("Adding 'selected_direction' column to runs table...")
        cursor.execute("""
            ALTER TABLE runs
            ADD COLUMN selected_direction VARCHAR(1000)
        """)

        conn.commit()
        conn.close()

        logger.info("Migration completed successfully!")
        print("✓ Migration completed: added 'selected_direction' column to runs table")

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        print(f"✗ Migration failed: {e}")
        raise

if __name__ == "__main__":
    migrate()
