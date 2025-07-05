#!/usr/bin/env python3
"""
Database initialization script for the Inventory Management System.
Creates tables and populates with sample data.
"""

import sys
import os
from datetime import datetime

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.database import SessionLocal, create_tables
from src.models import User, Role, Item, Storeroom, StoreroomItem, Transfer, TransferLog
from src.auth import get_password_hash

def init_database():
    """Initialize database with tables and sample data"""
    print("Creating database tables...")
    create_tables()
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Create roles
        print("Creating roles...")
        admin_role = Role(
            name="admin",
            description="System administrator with full access",
            permissions='{"all": true}'
        )
        manager_role = Role(
            name="manager",
            description="Storeroom manager with CRUD permissions",
            permissions='{"create": true, "read": true, "update": true, "delete": false}'
        )
        user_role = Role(
            name="user",
            description="Regular user with read and basic operations",
            permissions='{"create": false, "read": true, "update": false, "delete": false}'
        )
        
        db.add_all([admin_role, manager_role, user_role])
        db.commit()
        
        # Create users
        print("Creating users...")
        admin_user = User(
            username="admin",
            email="admin@example.com",
            password_hash=get_password_hash("admin123"),
            first_name="System",
            last_name="Administrator",
            role_id=admin_role.id,
            is_active=True
        )
        
        manager_user = User(
            username="manager",
            email="manager@example.com",
            password_hash=get_password_hash("manager123"),
            first_name="Store",
            last_name="Manager",
            role_id=manager_role.id,
            is_active=True
        )
        
        regular_user = User(
            username="user",
            email="user@example.com",
            password_hash=get_password_hash("user123"),
            first_name="Regular",
            last_name="User",
            role_id=user_role.id,
            is_active=True
        )
        
        db.add_all([admin_user, manager_user, regular_user])
        db.commit()
        
        # Create storerooms
        print("Creating storerooms...")
        warehouse_a = Storeroom(
            name="Warehouse A",
            description="Main warehouse facility",
            location="Building A, Floor 1",
            capacity=10000,
            manager_id=manager_user.id,
            is_active=True
        )
        
        warehouse_b = Storeroom(
            name="Warehouse B",
            description="Secondary warehouse facility",
            location="Building B, Floor 2",
            capacity=5000,
            manager_id=manager_user.id,
            is_active=True
        )
        
        retail_store = Storeroom(
            name="Retail Store",
            description="Front-facing retail location",
            location="Main Street Store",
            capacity=1000,
            manager_id=manager_user.id,
            is_active=True
        )
        
        db.add_all([warehouse_a, warehouse_b, retail_store])
        db.commit()
        
        # Create items
        print("Creating items...")
        laptop = Item(
            name="Laptop Computer",
            description="High-performance laptop for office use",
            sku="LAP-001",
            category="Electronics",
            unit_of_measure="pcs",
            minimum_stock=5,
            maximum_stock=50,
            unit_cost=899.99,
            barcode="123456789012",
            is_active=True
        )
        
        office_chair = Item(
            name="Office Chair",
            description="Ergonomic office chair with lumbar support",
            sku="CHR-001",
            category="Furniture",
            unit_of_measure="pcs",
            minimum_stock=10,
            maximum_stock=100,
            unit_cost=299.99,
            barcode="123456789013",
            is_active=True
        )
        
        printer_paper = Item(
            name="Printer Paper",
            description="A4 size white printer paper",
            sku="PAP-001",
            category="Office Supplies",
            unit_of_measure="reams",
            minimum_stock=50,
            maximum_stock=500,
            unit_cost=4.99,
            barcode="123456789014",
            is_active=True
        )
        
        mouse = Item(
            name="Wireless Mouse",
            description="Ergonomic wireless mouse",
            sku="MOU-001",
            category="Electronics",
            unit_of_measure="pcs",
            minimum_stock=20,
            maximum_stock=200,
            unit_cost=29.99,
            barcode="123456789015",
            is_active=True
        )
        
        db.add_all([laptop, office_chair, printer_paper, mouse])
        db.commit()
        
        # Create storeroom items (inventory)
        print("Creating inventory...")
        inventory_items = [
            StoreroomItem(storeroom_id=warehouse_a.id, item_id=laptop.id, quantity=25),
            StoreroomItem(storeroom_id=warehouse_a.id, item_id=office_chair.id, quantity=50),
            StoreroomItem(storeroom_id=warehouse_a.id, item_id=printer_paper.id, quantity=200),
            StoreroomItem(storeroom_id=warehouse_a.id, item_id=mouse.id, quantity=100),
            
            StoreroomItem(storeroom_id=warehouse_b.id, item_id=laptop.id, quantity=15),
            StoreroomItem(storeroom_id=warehouse_b.id, item_id=office_chair.id, quantity=30),
            StoreroomItem(storeroom_id=warehouse_b.id, item_id=printer_paper.id, quantity=100),
            StoreroomItem(storeroom_id=warehouse_b.id, item_id=mouse.id, quantity=75),
            
            StoreroomItem(storeroom_id=retail_store.id, item_id=laptop.id, quantity=3),
            StoreroomItem(storeroom_id=retail_store.id, item_id=office_chair.id, quantity=8),
            StoreroomItem(storeroom_id=retail_store.id, item_id=printer_paper.id, quantity=25),
            StoreroomItem(storeroom_id=retail_store.id, item_id=mouse.id, quantity=20),
        ]
        
        db.add_all(inventory_items)
        db.commit()
        
        # Create sample transfers
        print("Creating sample transfers...")
        transfer1 = Transfer(
            transfer_number="TRN-20240101-SAMPLE01",
            source_storeroom_id=warehouse_a.id,
            destination_storeroom_id=retail_store.id,
            item_id=laptop.id,
            quantity=2,
            transfer_type="transfer",
            status="completed",
            reason="Restocking retail store",
            requested_by=manager_user.id,
            approved_by=admin_user.id,
            completed_by=admin_user.id,
            requested_at=datetime.utcnow(),
            approved_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            notes="Initial stock transfer"
        )
        
        transfer2 = Transfer(
            transfer_number="TRN-20240101-SAMPLE02",
            source_storeroom_id=warehouse_b.id,
            destination_storeroom_id=retail_store.id,
            item_id=mouse.id,
            quantity=10,
            transfer_type="transfer",
            status="pending",
            reason="Restocking retail store",
            requested_by=regular_user.id,
            requested_at=datetime.utcnow(),
            notes="Pending approval"
        )
        
        db.add_all([transfer1, transfer2])
        db.commit()
        
        # Create transfer logs
        print("Creating transfer logs...")
        log1 = TransferLog(
            transfer_id=transfer1.id,
            action="completed",
            previous_status="pending",
            new_status="completed",
            user_id=admin_user.id,
            timestamp=datetime.utcnow(),
            notes="Transfer completed successfully"
        )
        
        log2 = TransferLog(
            transfer_id=transfer2.id,
            action="created",
            new_status="pending",
            user_id=regular_user.id,
            timestamp=datetime.utcnow(),
            notes="Transfer created and awaiting approval"
        )
        
        db.add_all([log1, log2])
        db.commit()
        
        print("Database initialization completed successfully!")
        print("\nSample login credentials:")
        print("Admin: username=admin, password=admin123")
        print("Manager: username=manager, password=manager123")
        print("User: username=user, password=user123")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
