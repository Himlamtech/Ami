"""
Script to create the first admin user in MongoDB.
Run this once to bootstrap the system with an admin account.
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.application.factory import ProviderFactory
from app.core.auth import get_password_hash
from app.core.mongodb_models import UserRole


async def create_admin():
    """Create first admin user."""
    try:
        # Get MongoDB client
        mongodb = await ProviderFactory.get_mongodb_client()
        
        # Check if admin already exists
        existing_admin = await mongodb.get_user_by_username("admin")
        if existing_admin:
            print("❌ Admin user already exists!")
            print(f"   Username: {existing_admin['username']}")
            print(f"   Email: {existing_admin['email']}")
            return
        
        # Create admin user
        admin_password = "admin"  # Change this after first login!
        admin_user = {
            "username": "admin",
            "email": "admin@ptit.edu.vn",
            "full_name": "System Administrator",
            "hashed_password": get_password_hash(admin_password),
            "role": UserRole.ADMIN,
            "is_active": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        
        user_id = await mongodb.create_user(admin_user)
        
        print("✅ Admin user created successfully!")
        print(f"   User ID: {user_id}")
        print(f"   Username: admin")
        print(f"   Password: {admin_password}")
        print(f"   Email: admin@ptit.edu.vn")
        print("\n⚠️  IMPORTANT: Change the password after first login!")
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
    finally:
        await ProviderFactory.cleanup()


if __name__ == "__main__":
    asyncio.run(create_admin())

