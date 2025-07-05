#!/usr/bin/env python3
"""
Database migration script to add authentication fields to existing database.
"""

import sqlite3

def migrate_database():
    """Add authentication fields to existing database"""
    db_path = "/home/kavia/workspace/code-generation/inventoryhub-120942-120952/ims_database/myapp.db"
    
    print(f"Migrating database at: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Add missing columns to users table
        print("Adding authentication fields to users table...")
        
        # Add password_hash column
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")
            print("Added password_hash column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("password_hash column already exists")
            else:
                raise
        
        # Add role_id column  
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN role_id INTEGER")
            print("Added role_id column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("role_id column already exists")
            else:
                raise
        
        # Add first_name column
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN first_name TEXT")
            print("Added first_name column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("first_name column already exists")
            else:
                raise
        
        # Add last_name column
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN last_name TEXT")
            print("Added last_name column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("last_name column already exists")
            else:
                raise
        
        # Add is_active column
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1")
            print("Added is_active column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("is_active column already exists")
            else:
                raise
        
        # Add last_login column
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN last_login TIMESTAMP")
            print("Added last_login column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("last_login column already exists")
            else:
                raise
        
        # Add updated_at column
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            print("Added updated_at column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("updated_at column already exists")
            else:
                raise
        
        # Create default admin user if no users exist with password_hash
        cursor.execute("SELECT COUNT(*) FROM users WHERE password_hash IS NOT NULL")
        auth_users_count = cursor.fetchone()[0]
        
        if auth_users_count == 0:
            print("Creating default admin user...")
            
            # First, ensure we have an admin role
            cursor.execute("SELECT id FROM roles WHERE name = 'admin'")
            admin_role = cursor.fetchone()
            
            if not admin_role:
                print("Creating admin role...")
                cursor.execute("""
                    INSERT INTO roles (name, description, permissions)
                    VALUES ('admin', 'System Administrator', '{"all": true}')
                """)
                cursor.execute("SELECT id FROM roles WHERE name = 'admin'")
                admin_role = cursor.fetchone()
            
            admin_role_id = admin_role[0]
            
            # Create admin user with hashed password
            # Using a simple hash for demo - in production use proper bcrypt
            import hashlib
            password_hash = hashlib.sha256("admin123".encode()).hexdigest()
            
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, first_name, last_name, role_id, is_active)
                VALUES ('admin', 'admin@example.com', ?, 'System', 'Administrator', ?, 1)
            """, (password_hash, admin_role_id))
            
            print("Created admin user (username: admin, password: admin123)")
        
        conn.commit()
        print("Database migration completed successfully!")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    migrate_database()
