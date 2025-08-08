from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.routes import users, payments, auth
from app.database import connect_to_mongo, close_mongo_connection, get_database

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Backend API",
    description="A FastAPI backend application",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(payments.router, prefix="/api/v1/payments", tags=["payments"])

@app.on_event("startup")
async def startup_db_client():
    """Connect to MongoDB on startup."""
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    """Close MongoDB connection on shutdown."""
    await close_mongo_connection()

@app.get("/")
async def root():
    return {"message": "Welcome to Backend API"}

@app.get("/health")
async def health_check():
    """Health check endpoint that also checks MongoDB connection."""
    try:
        db = get_database()
        if db is not None:
            # Test MongoDB connection
            await db.command('ping')
            return {
                "status": "healthy",
                "database": "connected",
                "message": "API and database are running"
            }
        else:
            return {
                "status": "unhealthy",
                "database": "disconnected",
                "message": "Database not initialized"
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        } 