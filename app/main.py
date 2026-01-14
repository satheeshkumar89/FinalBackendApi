from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create uploads directory if it doesn't exist
if not os.path.exists("uploads"):
    os.makedirs("uploads")

from app.routers import auth, owner, restaurant, dashboard, menu, orders, admin, customer_auth, customer, notifications, delivery_partner
# from app.socket_manager import sio_app
from app.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

# Auto-patch missing columns on startup
try:
    from migrate import patch_existing_tables
    patch_existing_tables()
except ImportError:
    logger.warning("Migration script not found, skipping auto-patch.")
except Exception as e:
    logger.error(f"Failed to auto-patch database: {e}")

app = FastAPI(
    title="FastFoodie API",
    description="Backend API for FastFoodie (Restaurant Partner, Customer & Delivery Partner)",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Mount Socket.IO app
# app.mount("/socket.io", sio_app)

# Include routers
app.include_router(auth.router)
app.include_router(owner.router)
app.include_router(restaurant.router)
app.include_router(dashboard.router)
app.include_router(menu.router)
app.include_router(orders.router)
app.include_router(admin.router)
app.include_router(customer_auth.router)
app.include_router(customer.router)
app.include_router(notifications.router)
app.include_router(delivery_partner.router)

@app.get("/")
def read_root():
    return {
        "message": "FastFoodie Restaurant Partner API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.put("/mock-upload/{file_path:path}")
async def mock_upload(file_path: str, request: Request):
    """Bypass S3 upload and save file locally for testing purposes"""
    try:
        content = await request.body()
        full_path = os.path.join("uploads", file_path)
        # Ensure subdirectory exists
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "wb") as f:
            f.write(content)
        return {
            "message": f"Successfully mock-uploaded {file_path}", 
            "status": "success", 
            "url": f"https://dharaifooddelivery.in/uploads/{file_path}"
        }
    except Exception as e:
        return {"message": f"Failed to mock-upload: {str(e)}", "status": "error"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
