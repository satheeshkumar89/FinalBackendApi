from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create uploads directory if it doesn't exist
os.makedirs("uploads", mode=0o777, exist_ok=True)
try:
    os.chmod("uploads", 0o777)
except Exception:
    pass

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

@app.on_event("startup")
def startup_event():
    try:
        from app.services.firebase_service import FirebaseService
        initialized = FirebaseService.initialize()
        if initialized:
            logger.info("✅ Firebase Service initialized successfully on startup.")
        else:
            logger.warning("⚠️ Firebase Service running in simulated development mode.")
    except Exception as e:
        logger.error(f"❌ Error initializing Firebase Service: {e}")

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

# Include routers (both root and versioned for backward compatibility)
routers = [
    auth.router, owner.router, restaurant.router, dashboard.router,
    menu.router, orders.router, admin.router, customer_auth.router,
    customer.router, notifications.router, delivery_partner.router
]

for router in routers:
    app.include_router(router)
    app.include_router(router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {
        "message": "FastFoodie Restaurant Partner API",
        "version": "1.0.0",
        "status": "running",
        "docs_url": "https://dharaidelivery.online/docs",
        "admin_docs_url": "https://dharaidelivery.online/admin/docs"
    }

# ============= Dedicated Admin Swagger UI =============
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

@app.get("/admin/openapi.json", include_in_schema=False)
def get_admin_openapi():
    """Generate OpenAPI schema containing strictly Admin endpoints"""
    admin_routes = []
    for route in app.routes:
        path = getattr(route, "path", "")
        tags = getattr(route, "tags", [])
        if path.startswith("/admin") or "Admin" in tags:
            # Exclude duplicate /api/v1 routes to keep schema clean
            if not path.startswith("/api/v1"):
                admin_routes.append(route)

    return get_openapi(
        title="FastFoodie Admin Management API",
        version="1.0.0",
        description="Dedicated Admin Portal API documentation for platform operations, approvals, and metrics.",
        routes=admin_routes
    )

@app.get("/admin/docs", include_in_schema=False)
def get_admin_swagger_ui():
    """Separate Swagger UI for Admin Portal"""
    return get_swagger_ui_html(
        openapi_url="/admin/openapi.json",
        title="FastFoodie Admin Portal API Docs",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png"
    )

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.put("/mock-upload/{file_path:path}")
@app.put("/api/v1/mock-upload/{file_path:path}")
async def mock_upload(file_path: str, request: Request):
    """Bypass S3 upload and save file locally for testing purposes"""
    try:
        content = await request.body()
        full_path = os.path.join("uploads", file_path)
        dir_path = os.path.dirname(full_path)
        os.makedirs(dir_path, mode=0o777, exist_ok=True)
        try:
            os.chmod(dir_path, 0o777)
        except Exception:
            pass
            
        with open(full_path, "wb") as f:
            f.write(content)
        try:
            os.chmod(full_path, 0o666)
        except Exception:
            pass
        return {
            "message": f"Successfully mock-uploaded {file_path}", 
            "status": "success", 
            "url": f"https://dharaidelivery.online/uploads/{file_path}"
        }
    except Exception as e:
        return {"message": f"Failed to mock-upload: {str(e)}", "status": "error"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
