
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Try to construct from components if direct URL is missing
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    # For this project, let's assume DATABASE_URL is in the .env as it's common for SQLAlchemy
    print("Error: DATABASE_URL not found in .env")
    exit(1)

# Fix for postgres:// vs postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)

def add_image_column():
    with engine.connect() as conn:
        print("Checking for 'image' column in 'products' table...")
        try:
            # PostgreSQL syntax to add column if not exists
            conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS image TEXT"))
            conn.commit()
            print("Successfully added 'image' column (or it already existed).")
        except Exception as e:
            print(f"Error adding column: {e}")

if __name__ == "__main__":
    add_image_column()
