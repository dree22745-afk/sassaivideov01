"""Optional: Seed test data"""
from database import SessionLocal
from models import User
from auth import hash_password

def seed():
    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            admin = User(
                email="admin@omni.ai",
                username="admin",
                password=hash_password("admin123"),
                full_name="Admin User",
                role="admin"
            )
            user = User(
                email="user@omni.ai",
                username="user",
                password=hash_password("user123"),
                full_name="Demo User",
                role="user"
            )
            db.add_all([admin, user])
            db.commit()
            print("✅ Test users created: admin/admin123, user/user123")
    finally:
        db.close()

if __name__ == "__main__":
    seed()