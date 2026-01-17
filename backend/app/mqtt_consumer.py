"""
mqtt_consumer.py - Real-time Parking Sensor Handler

This module handles real-time updates from parking sensors via MQTT.

Flow:
1. Sensors publish status changes to MQTT broker (Mosquitto)
2. This consumer subscribes and receives those messages
3. Updates are batched (every 5s) and persisted to DB + Redis
4. Connected WebSocket clients receive instant notifications

Topic format: parking/<city>/<spot_id>/status
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

from paho.mqtt.client import Client as MqttClient

from app.database import get_session, redis_client
from app.repositories.parking_repository import ParkingRepository
from app.repositories.spot_status_log_repository import SpotStatusLogRepository
from app.constants import VALID_SPOT_STATUSES, VALID_CITIES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app.mqtt_consumer")


# Global variables for batching
pending_updates: Dict[int, Dict] = {}
batch_lock = asyncio.Lock()
websocket_clients: List = []


class MQTTConsumer:
    def __init__(self):
        self.client = MqttClient()
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.loop: Optional[asyncio.AbstractEventLoop] = None  # set in start()

    async def start(self):
        """Start MQTT consumer: connect, subscribe, and spawn workers."""
        self.loop = asyncio.get_running_loop()

        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                logger.info("Connected to MQTT broker")
                for city in VALID_CITIES:
                    topic = f"parking/{city}/+/status"
                    client.subscribe(topic)
                    logger.info(f"Subscribed to {topic}")
            else:
                logger.error(f"Failed to connect, return code {rc}")

        def on_message(client, userdata, msg):
            """Runs in Paho's network thread; enqueue into the asyncio loop."""
            try:
                loop = self.loop
                if loop and loop.is_running():
                    loop.call_soon_threadsafe(self.message_queue.put_nowait, msg)
                else:
                    logger.error("Asyncio loop not set/running yet; dropping MQTT message")
            except Exception as e:
                logger.error(f"Failed to enqueue MQTT message: {e}")

        self.client.on_connect = on_connect
        self.client.on_message = on_message

        try:
            # Hostname matches docker-compose service name
            self.client.connect("mosquitto", 1883, 60)
            self.client.loop_start()
            logger.info("MQTT consumer started")

            asyncio.create_task(self.process_queue())
            asyncio.create_task(self.batch_update_task())
        except Exception as e:
            logger.error(f"Failed to start MQTT consumer: {e}")

    async def process_queue(self):
        """Process messages from queue asynchronously."""
        while True:
            msg = await self.message_queue.get()
            try:
                await self.process_mqtt_message(msg)
            finally:
                self.message_queue.task_done()

    async def process_mqtt_message(self, msg):
        """Process incoming MQTT messages."""
        try:
            topic = msg.topic
            payload_raw = msg.payload.decode("utf-8", errors="replace")
            logger.info(f"Received: {topic} -> {payload_raw}")

            # Expected: parking/<City>/<SpotId>/status
            parts = topic.split("/")
            if len(parts) == 4 and parts[0] == "parking" and parts[3] == "status":
                city = parts[1]
                try:
                    spot_id = int(parts[2])
                except ValueError:
                    logger.warning(f"Invalid spot id in topic: {parts[2]}")
                    return

                status = payload_raw.strip()
                if status.startswith("{"):
                    try:
                        parsed = json.loads(status)
                        status = (parsed.get("status") or "").strip() or status
                    except Exception:
                        pass

                if city not in VALID_CITIES:
                    logger.warning(f"Unsupported city: {city}")
                    return

                if status not in VALID_SPOT_STATUSES:
                    logger.warning(f"Invalid status: {status}")
                    return

                # Log status change immediately
                session = await get_session()
                try:
                    log_repo = SpotStatusLogRepository(session)
                    await log_repo.create_log(spot_id, status)
                except Exception as e:
                    logger.error(f"Error logging status change: {e}")
                finally:
                    await session.close()

                # Queue for batch processing
                async with batch_lock:
                    pending_updates[spot_id] = {
                        "status": status,
                        "city": city,
                        "timestamp": datetime.now(),
                    }

                await self.broadcast_to_websockets(spot_id, status, city)

        except Exception as e:
            logger.error(f"Error processing message: {e}")

    async def batch_update_task(self):
        """
        Every 5s persist pending updates to DB and Redis.

        Important: redis_client is ASYNC → all Redis calls MUST be awaited.
        We always upsert the base hash and ensure current-status set/GEO membership.
        We only remove from old status buckets when the status actually changed.
        """
        while True:
            try:
                await asyncio.sleep(5)

                async with batch_lock:
                    if not pending_updates:
                        continue
                    updates_to_process = pending_updates.copy()
                    pending_updates.clear()

                session = await get_session()
                try:
                    parking_repo = ParkingRepository(session)

                    for spot_id, update_data in updates_to_process.items():
                        try:
                            current_spot = await parking_repo.get_spot_by_id(spot_id)
                            old_status = current_spot.status if current_spot else None

                            updated_spot = await parking_repo.update_spot(
                                spot_id, status=update_data["status"]
                            )
                            if not updated_spot:
                                logger.warning(f"Spot {spot_id} not found")
                                continue

                            new_status = update_data["status"]
                            status_changed = (
                                old_status is not None and new_status != old_status
                            )

                            # --- Redis: ALWAYS upsert the base hash ---
                            await redis_client.hset(
                                f"spot:{spot_id}",
                                mapping={
                                    "id": str(spot_id),
                                    "latitude": "" if updated_spot.latitude is None else str(updated_spot.latitude),
                                    "longitude": "" if updated_spot.longitude is None else str(updated_spot.longitude),
                                    "location": updated_spot.location,
                                    "status": new_status,
                                    "last_updated": (
                                        updated_spot.last_updated.isoformat()
                                        if updated_spot.last_updated else ""
                                    ),
                                },
                            )

                            # --- Ensure membership in the current-status set (idempotent) ---
                            await redis_client.sadd(f"spots:by_status:{new_status}", spot_id)
                            if status_changed:
                                await redis_client.srem(f"spots:by_status:{old_status}", spot_id)

                            # --- GEO upsert for current status (if coords exist) ---
                            if updated_spot.longitude is not None and updated_spot.latitude is not None:
                                lon = float(updated_spot.longitude)
                                lat = float(updated_spot.latitude)

                                # Upsert current
                                await redis_client.execute_command(
                                    "GEOADD", f"spots:geo:{new_status}", lon, lat, f"spot_{spot_id}"
                                )

                                # Remove from old only if status changed
                                if status_changed:
                                    await redis_client.execute_command(
                                        "ZREM", f"spots:geo:{old_status}", f"spot_{spot_id}"
                                    )
                            else:
                                logger.warning(f"Spot {spot_id} missing coordinates; skipping GEO")

                            logger.info(
                                f"Updated spot {spot_id} in DB; cache upserted "
                                f"(status_changed={status_changed}, status={new_status})"
                            )

                        except Exception as e:
                            logger.error(f"Error updating spot {spot_id}: {e}")
                finally:
                    await session.close()

            except Exception as e:
                logger.error(f"Error in batch update task: {e}")

    async def broadcast_to_websockets(self, spot_id: int, status: str, city: str):
        """Broadcast updates to connected WebSocket clients."""
        if not websocket_clients:
            return

        message = {
            "type": "spot_update",
            "spot_id": spot_id,
            "status": status,
            "city": city,
            "timestamp": datetime.now().isoformat(),
        }

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
    """Start the MQTT consumer."""
    await mqtt_consumer.start()

def add_websocket_client(websocket):
    """Add a WebSocket client for broadcasting."""
    websocket_clients.append(websocket)

def remove_websocket_client(websocket):
    """Remove a WebSocket client."""
    if websocket in websocket_clients:
        websocket_clients.remove(websocket)
