from app.repositories.parking_repository import ParkingRepository
from app.models import ParkingSpot
import logging

logger = logging.getLogger(__name__)

class ParkingService:
    def __init__(self, repo: ParkingRepository):
        self.repo = repo

    async def get_all_spots(self):
        return await self.repo.get_all_spots()

    async def get_spot_by_id(self, spot_id: int):
        spot = await self.repo.get_spot_by_id(spot_id)
        if not spot:
            raise ValueError("Spot not found")
        return spot

    async def create_spot(self, location: str, latitude: float, longitude: float, status: str):
        return await self.repo.create_spot(location, latitude, longitude, status)

    async def update_spot(self, spot_id: int, **updates):
        spot = await self.repo.update_spot(spot_id, **updates)
        if not spot:
            raise ValueError("Spot not found")
        return spot

    async def delete_spot(self, spot_id: int):
        spot = await self.repo.delete_spot(spot_id)
        if not spot:
            raise ValueError("Spot not found")

    async def get_spots_in_viewport(self, sw_lat, sw_lng, ne_lat, ne_lng, status, limit):
        spots, hit = await self.repo.get_spots_in_viewport_cached(sw_lat, sw_lng, ne_lat, ne_lng, status)
        if hit and spots:
            logger.info("Fetched from cache")
            return spots
        spots = await self.repo.get_spots_in_viewport(sw_lat, sw_lng, ne_lat, ne_lng, status, limit)
        logger.info("Fetched from DB")
        return spots