"""
main.py - FastAPI Application Entry Point

This is the main file that bootstraps the Smart Parking backend.
It handles:
- Application startup (database init, Redis cache, MQTT consumer)
- CORS configuration for frontend communication
- WebSocket endpoint for real-time updates
- Router registration for all API endpoints
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import init_db
from app import models
from app.routers.user_router import router as user_router
from app.routers.parking_router import router as parking_router
from app.routers.spot_status_log_router import router as spot_status_log_router
from app.routers.reservation_router import router as reservation_router
from app.mqtt_consumer import start_mqtt_consumer, add_websocket_client, remove_websocket_client
from app.database import get_session, redis_client
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# Application Lifespan
# =============================================================================
# This runs once when the app starts and once when it shuts down.
# Startup: Initialize DB tables, preload cache, start MQTT listener
# Shutdown: Clean up resources

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Step 1: Create database tables if they don't exist
    await init_db()
    logger.info("Database initialized")

    # Step 2: Preload all parking spots into Redis cache for fast reads
    session = await get_session()
    try:
        from app.repositories.parking_repository import ParkingRepository
        repo = ParkingRepository(session)
        await repo.preload_spots_to_cache()
        logger.info("Redis cache preload successful")
    except Exception as e:
        logger.error(f"Failed to preload Redis cache: {e}")
    finally:
        await session.close()

    # Step 3: Start listening for MQTT messages from parking sensors
    try:
        await start_mqtt_consumer()
        logger.info("MQTT consumer started successfully")
    except Exception as e:
        logger.error(f"Failed to start MQTT consumer: {e}")

    yield  # App is running

    logger.info("Shutting down...")


# =============================================================================
# FastAPI App Instance
# =============================================================================

app = FastAPI(lifespan=lifespan, title="Smart Parking API")


# =============================================================================
# CORS Middleware
# =============================================================================
# Allows the React frontend (running on port 5173) to make requests to this API

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# WebSocket Endpoint
# =============================================================================
# Real-time connection for pushing parking spot updates to connected clients

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    add_websocket_client(websocket)
    logger.info(f"WebSocket client connected: {websocket.client}")

    try:
        while True:
            # Keep connection alive and handle any client messages
            data = await websocket.receive_text()
            await websocket.send_json({"type": "echo", "message": data})
    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected: {websocket.client}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        remove_websocket_client(websocket)


# =============================================================================
# API Routers
# =============================================================================
# All routes are prefixed with /api (e.g., /api/users, /api/spots)

app.include_router(user_router, prefix="/api")
app.include_router(parking_router, prefix="/api")
app.include_router(spot_status_log_router, prefix="/api")
app.include_router(reservation_router, prefix="/api")


# Health check endpoint
@app.get("/")
async def root():
    return {"message": "Smart Parking Backend Running!"}

