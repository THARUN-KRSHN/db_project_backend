
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)

def get_test_user():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT email, role FROM users LIMIT 5"))
        users = result.fetchall()
        for user in users:
            print(f"User: {user.email}, Role: {user.role}")

if __name__ == "__main__":
    get_test_user()
