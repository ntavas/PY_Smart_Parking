import asyncio
import json
from datetime import datetime
from typing import Dict, Set, List
from paho.mqtt.client import Client as MqttClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.models import ParkingSpot, SpotStatusLog
from app.repositories.parking_repository import ParkingRepository
from app.repositories.spot_status_log_repository import SpotStatusLogRepository
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for batching
pending_updates: Dict[int, Dict] = {}
batch_lock = asyncio.Lock()
websocket_clients: List = []

class MQTTConsumer:
    def __init__(self):
        self.client = MqttClient()
        self.supported_cities = ["Athens", "Larissa"]

    async def start(self):
        """Start the MQTT consumer with batching"""
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                logger.info("Connected to MQTT broker")
                # Subscribe to topics for supported cities
                for city in self.supported_cities:
                    client.subscribe(f"parking/{city}/+/status")
                    logger.info(f"Subscribed to parking/{city}/+/status")
            else:
                logger.error(f"Failed to connect, return code {rc}")

        def on_message(client, userdata, msg):
            asyncio.create_task(self.process_mqtt_message(msg))

        self.client.on_connect = on_connect
        self.client.on_message = on_message

        # Connect to MQTT broker
        try:
            self.client.connect("mosquitto", 1883, 60)
            self.client.loop_start()
            logger.info("MQTT consumer started")

            # Start the batch update task
            asyncio.create_task(self.batch_update_task())

        except Exception as e:
            logger.error(f"Failed to start MQTT consumer: {e}")

    async def process_mqtt_message(self, msg):
        """Process incoming MQTT messages"""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            logger.info(f"Received: {topic} -> {payload}")

            # Parse topic (e.g., parking/Athens/1/status or parking/Larissa/5/status)
            parts = topic.split('/')
            if len(parts) == 4 and parts[0] == "parking" and parts[3] == "status":
                city = parts[1]
                spot_id = int(parts[2])
                status = payload.strip()

                # Validate city
                if city not in self.supported_cities:
                    logger.warning(f"Unsupported city: {city}")
                    return

                # Validate status
                valid_statuses = ["Available", "Occupied", "Reserved", "Maintenance"]
                if status not in valid_statuses:
                    logger.warning(f"Invalid status: {status}")
                    return

                # Log the status change immediately
                await self.log_status_change(spot_id, status)

                # Add to pending updates for batch processing
                async with batch_lock:
                    pending_updates[spot_id] = {
                        'status': status,
                        'city': city,
                        'timestamp': datetime.now()
                    }

                # Broadcast to WebSocket clients
                await self.broadcast_to_websockets(spot_id, status, city)

        except Exception as e:
            logger.error(f"Error processing message: {e}")

    async def log_status_change(self, spot_id: int, status: str):
        """Log status change to spot_status_log table immediately"""
        try:
            async with get_session() as session:
                log_repo = SpotStatusLogRepository(session)
                await log_repo.create_log(spot_id, status)
                logger.debug(f"Logged status change for spot {spot_id}: {status}")
        except Exception as e:
            logger.error(f"Error logging status change: {e}")

    async def batch_update_task(self):
        """Update parking spots every 5 seconds"""
        while True:
            try:
                await asyncio.sleep(5)  # Wait 5 seconds

                async with batch_lock:
                    if not pending_updates:
                        continue

                    # Copy and clear pending updates
                    updates_to_process = pending_updates.copy()
                    pending_updates.clear()

                # Process the batch updates
                async with get_session() as session:
                    parking_repo = ParkingRepository(session)

                    for spot_id, update_data in updates_to_process.items():
                        try:
                            # Update the parking spot
                            updated_spot = await parking_repo.update_spot(
                                spot_id, 
                                status=update_data['status']
                            )

                            if updated_spot:
                                logger.info(f"Batch updated spot {spot_id} to {update_data['status']} in {update_data['city']}")
                            else:
                                logger.warning(f"Spot {spot_id} not found for update")

                        except Exception as e:
                            logger.error(f"Error updating spot {spot_id}: {e}")

            except Exception as e:
                logger.error(f"Error in batch update task: {e}")

    async def broadcast_to_websockets(self, spot_id: int, status: str, city: str):
        """Broadcast updates to connected WebSocket clients"""
        if not websocket_clients:
            return

        message = {
            "type": "spot_update",
            "spot_id": spot_id,
            "status": status,
            "city": city,
            "timestamp": datetime.now().isoformat()
        }

        # Remove disconnected clients
        connected_clients = []
        for client in websocket_clients:
            try:
                await client.send_json(message)
                connected_clients.append(client)
            except Exception as e:
                logger.debug(f"Removed disconnected WebSocket client: {e}")

        websocket_clients.clear()
        websocket_clients.extend(connected_clients)

# Global instance
mqtt_consumer = MQTTConsumer()

async def start_mqtt_consumer():
    """Start the MQTT consumer"""
    await mqtt_consumer.start()

def add_websocket_client(websocket):
    """Add a WebSocket client for broadcasting"""
    websocket_clients.append(websocket)

def remove_websocket_client(websocket):
    """Remove a WebSocket client"""
    if websocket in websocket_clients:
        websocket_clients.remove(websocket)