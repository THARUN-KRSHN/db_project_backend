
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)

def check_inventory():
    with engine.connect() as conn:
        print("Checking products table...")
        result = conn.execute(text("SELECT product_name, image FROM products LIMIT 5"))
        products = result.fetchall()
        print(f"Found {len(products)} products:")
        for p in products:
            print(f"Product: {p.product_name}, Image: {p.image}")

if __name__ == "__main__":
    check_inventory()
