import sqlite3
import os

# Get database path
db_path = os.path.join(os.path.dirname(__file__), 'db.sqlite3')

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Create UseCase table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS core_usecase (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(100) NOT NULL UNIQUE,
            description TEXT NOT NULL,
            icon_name VARCHAR(50) NOT NULL DEFAULT 'users',
            "order" INTEGER NOT NULL DEFAULT 0,
            is_active BOOLEAN NOT NULL DEFAULT 1,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL
        )
    """)
    print("✓ Created core_usecase table")
    
    # Create ProductUseCase table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS core_productusecase (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            use_case_id INTEGER NOT NULL,
            is_enabled BOOLEAN NOT NULL DEFAULT 1,
            "order" INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (product_id) REFERENCES core_product(id),
            FOREIGN KEY (use_case_id) REFERENCES core_usecase(id),
            UNIQUE (product_id, use_case_id)
        )
    """)
    print("✓ Created core_productusecase table")
    
    # Commit changes
    conn.commit()
    print("✓ Database updated successfully!")
    
except Exception as e:
    print(f"✗ Error: {e}")
    conn.rollback()
    
finally:
    conn.close()
