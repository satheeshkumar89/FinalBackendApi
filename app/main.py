from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, owner, restaurant, dashboard, menu, orders, admin, customer_auth, customer, notifications, delivery_partner
from app.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FastFoodie API",
    description="Backend API for FastFoodie (Restaurant Partner, Customer & Delivery Partner)",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
async def mock_upload(file_path: str):
    """Bypass S3 upload for testing purposes"""
    return {"message": f"Successfully mock-uploaded {file_path}", "status": "success"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
