from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import ParkingSpot
from app.database import redis_client
import asyncio
class ParkingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_spots(self):
        result = await self.db.execute(select(ParkingSpot))
        return result.scalars().all()

    async def get_spot_by_id(self, spot_id: int):
        return await self.db.get(ParkingSpot, spot_id)

    async def create_spot(self, location: str, latitude: float, longitude: float, status: str):
        spot = ParkingSpot(location=location, latitude=latitude, longitude=longitude, status=status)
        self.db.add(spot)
        await self.db.commit()
        await self.db.refresh(spot)
        return spot

    async def update_spot(self, spot_id: int, **updates):
        spot = await self.db.get(ParkingSpot, spot_id)
        if not spot:
            return None
        for key, value in updates.items():
            if value is not None:
                setattr(spot, key, value)
        await self.db.commit()
        return spot

    async def get_spots_by_city(self, city: str):
        """Get all parking spots for a specific city"""
        result = await self.db.execute(
            select(ParkingSpot).where(ParkingSpot.location.contains(city))
        )
        return result.scalars().all()

    async def delete_spot(self, spot_id: int):
        spot = await self.db.get(ParkingSpot, spot_id)
        if spot:
            await self.db.delete(spot)
            await self.db.commit()
        return spot

    async def get_spots_in_viewport(self, sw_lat: float, sw_lng: float, ne_lat: float, ne_lng: float,
                                    status: str = None, limit: int = 100):

        # Build query: bbox + optional status filter
        query = select(ParkingSpot).where(
            ParkingSpot.latitude >= sw_lat,
            ParkingSpot.latitude <= ne_lat,
            ParkingSpot.longitude >= sw_lng,
            ParkingSpot.longitude <= ne_lng
        )
        if status:
            query = query.where(ParkingSpot.status == status)

        # Order by last_updated DESC, apply limit
        query = query.order_by(ParkingSpot.last_updated.desc()).limit(limit)

        spots = await self.db.execute(query)
        return spots.scalars().all()

    async def get_spots_in_viewport_cached(self, sw_lat, sw_lng, ne_lat, ne_lng, status=None):
        geo_key = f"spots:geo:{status}" if status else "spots:geo:Available"
        center_lng = (sw_lng + ne_lng) / 2
        center_lat = (sw_lat + ne_lat) / 2
        # Rough approximation for radius
        radius_km = max(abs(ne_lat - sw_lat), abs(ne_lng - sw_lng)) * 111.32
        # Await the async geosearch call directly
        results = await redis_client.geosearch(
             geo_key,
             longitude = center_lng,
             latitude = center_lat,
             radius = radius_km,
             unit = "km",
             sort = "ASC",
             count = 2000)

        spot_ids = [int(r) for r in results]
        spots = []
        for sid in spot_ids:
            data = await redis_client.hgetall(f"spot:{sid}")
            if data:
                spots.append(ParkingSpot(
                    id=int(data[b"id"]),
                    latitude=float(data[b"latitude"]),
                    longitude=float(data[b"longitude"]),
                    location=data[b"location"].decode('utf-8'),
                    status=data[b"status"].decode('utf-8'),
                    last_updated=data[b"last_updated"].decode('utf-8') or None
                ))
        return spots, True  # Cache hit