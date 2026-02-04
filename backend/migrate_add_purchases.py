"""
Migration script to create purchases table
"""
import sqlite3
from src.config import logger

def migrate():
    """Create purchases table"""
    try:
        # Connect to database
        conn = sqlite3.connect('pain_to_idea.db')
        cursor = conn.cursor()

        # Check if table already exists
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='purchases'
        """)

        if cursor.fetchone():
            logger.info("Table 'purchases' already exists, skipping migration")
            print("Table 'purchases' already exists, skipping migration")
            return

        # Create purchases table
        logger.info("Creating 'purchases' table...")
        cursor.execute("""
            CREATE TABLE purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                idea_id INTEGER NOT NULL,
                run_id VARCHAR,
                created_at DATETIME NOT NULL,
                user_ip VARCHAR(50),
                user_agent VARCHAR(500),
                FOREIGN KEY (idea_id) REFERENCES ideas(id),
                FOREIGN KEY (run_id) REFERENCES runs(id)
            )
        """)

        # Create indexes for better query performance
        cursor.execute("""
            CREATE INDEX idx_purchases_idea_id ON purchases(idea_id)
        """)
        cursor.execute("""
            CREATE INDEX idx_purchases_created_at ON purchases(created_at)
        """)

        conn.commit()
        conn.close()

        logger.info("Migration completed successfully!")
        print("Migration completed: 'purchases' table created successfully")

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        print(f"Migration failed: {e}")
        raise

if __name__ == "__main__":
    migrate()
