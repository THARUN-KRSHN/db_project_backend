
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_migrations():
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("Warning: DATABASE_URL not set, skipping DB migration.")
        return

    # Fix for postgres:// vs postgresql://
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    try:
        from sqlalchemy import create_engine, text
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            print("Checking for 'image' column in 'products' table...")
            conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS image TEXT"))
            print("Successfully ensured 'image' column exists.")
            
            print("Checking for 'cover_image' column in 'shops' table...")
            conn.execute(text("ALTER TABLE shops ADD COLUMN IF NOT EXISTS cover_image TEXT"))
            conn.commit()
            print("Successfully ensured 'cover_image' column exists.")
    except Exception as e:
        print(f"DB migration warning (non-fatal): {e}")

if __name__ == "__main__":
    run_migrations()
