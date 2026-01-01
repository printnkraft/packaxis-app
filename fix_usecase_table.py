import sqlite3
import os

# Get database path
db_path = os.path.join(os.path.dirname(__file__), 'db.sqlite3')

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Drop the old ProductUseCase table if it exists
    cursor.execute("DROP TABLE IF EXISTS core_productusecase")
    print("✓ Dropped old core_productusecase table")
    
    # Commit changes
    conn.commit()
    print("✓ Database updated successfully!")
    
except Exception as e:
    print(f"✗ Error: {e}")
    conn.rollback()
    
finally:
    conn.close()
