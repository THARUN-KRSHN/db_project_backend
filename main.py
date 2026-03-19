import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from routers import auth_router, shop_router, inventory_router, billing_router, dashboard_router, public_router

load_dotenv()

app = FastAPI(
    title="Smart Multi-Tenant Inventory & Billing System",
    description="A multi-tenant platform for managing retail shop inventory, billing, and analytics.",
    version="1.0.0",
)

# CORS — allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        os.getenv("FRONTEND_URL", ""),
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(auth_router.router)
app.include_router(shop_router.router)
app.include_router(inventory_router.router)
app.include_router(billing_router.router)
app.include_router(dashboard_router.router)
app.include_router(public_router.router)

# Mount static directory for uploads
os.makedirs("static/logos", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "message": "Smart Inventory & Billing System API is running",
    }
