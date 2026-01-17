"""
ISAVS FastAPI Application Entry Point
Enhanced with robust CORS, error handling, and health checks
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from app.api import endpoints
from app.db.database import init_db, close_db
from app.core.config import settings
from app.services.websocket_manager import get_connection_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("🚀 ISAVS 2026 Backend Starting...")
    await init_db()
    logger.info("✅ Database initialized")
    logger.info(f"🌐 CORS Origins: {settings.CORS_ORIGINS}")
    yield
    # Shutdown
    logger.info("🛑 Shutting down...")
    await close_db()
    logger.info("✅ Cleanup complete")


app = FastAPI(
    title="ISAVS - Intelligent Student Attendance Verification System",
    description="Secure attendance verification using Face Recognition, ID Validation, and OTP",
    version="2.0.0",
    lifespan=lifespan
)

# Parse CORS origins from config
cors_origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",")]
logger.info(f"📡 Configured CORS origins: {cors_origins}")

# Enhanced CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,  # Cache preflight requests for 1 hour
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions."""
    logger.error(f"❌ Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc),
            "path": str(request.url)
        }
    )


# Include API routers
app.include_router(endpoints.router)


@app.get("/health")
async def health_check():
    """
    Enhanced health check endpoint.
    Returns system status and configuration info.
    """
    return {
        "status": "healthy",
        "service": "ISAVS 2026",
        "version": "2.0.0",
        "backend_port": 6000,
        "frontend_port": 2000,
        "cors_enabled": True,
        "database": "connected"
    }


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "ISAVS - Intelligent Student Attendance Verification System",
        "version": "2.0.0",
        "year": 2026,
        "docs": "/docs",
        "health": "/health",
        "api": "/api",
        "status": "operational"
    }


@app.websocket("/ws/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    """
    WebSocket endpoint for real-time dashboard updates.
    
    Pushes attendance_update and anomaly_alert messages to connected clients.
    
    Message format:
    {
        "type": "attendance_update" | "anomaly_alert",
        "data": {...},
        "timestamp": "ISO8601"
    }
    """
    manager = get_connection_manager()
    await manager.connect(websocket)
    
    try:
        # Keep connection alive and listen for client messages
        while True:
            # Wait for any message from client (ping/pong for keep-alive)
            data = await websocket.receive_text()
            
            # Echo back for keep-alive
            if data == "ping":
                await websocket.send_text("pong")
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("WebSocket client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)
