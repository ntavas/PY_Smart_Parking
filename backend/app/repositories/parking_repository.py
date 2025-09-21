from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import ParkingSpot

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