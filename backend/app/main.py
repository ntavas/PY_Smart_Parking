from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import init_db
from app import models
from app.routers import router
# from app.mqtt_consumer import start_mqtt_consumer, on_message  # Uncomment later

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    print("Starting MQTT consumer...")
    # await start_mqtt_consumer()  # Uncomment later
    yield
    print("Shutting down...")

app = FastAPI(lifespan=lifespan, title="Smart Parking API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print(f"Frontend connected: {websocket.client}")
    while True:
        try:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
        except:
            break

app.include_router(router, prefix="/api", tags=["Users"])

@app.get("/")
async def root():
    return {"message": "Smart Parking Backend Running!"}