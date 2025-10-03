from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional, Tuple, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import ParkingSpot
from app.database import redis_client

logger = logging.getLogger(__name__)

def _s(x) -> str:
    if isinstance(x, (bytes, bytearray)):
        return x.decode("utf-8", errors="replace")
    return "" if x is None else str(x)

def _get_any(d: dict, *keys, default=None):
    for k in keys:
        if k in d:
            return d[k]
    return default

def _parse_dt(x: Optional[str]) -> Optional[datetime]:
    if not x:
        return None
    try:
        s = x.replace("Z", "+00:00") if x.endswith("Z") else x
        return datetime.fromisoformat(s)
    except Exception:
        return None

def _member_to_id(member: bytes | str) -> Optional[int]:
    v = _s(member)
    if v.startswith("spot_"):
        v = v.split("_", 1)[1]
    try:
        return int(v)
    except Exception:
        return None

class ParkingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_spots(self) -> List[ParkingSpot]:
        res = await self.db.execute(select(ParkingSpot))
        return res.scalars().all()

    async def get_spot_by_id(self, spot_id: int) -> Optional[ParkingSpot]:
        return await self.db.get(ParkingSpot, spot_id)

    async def create_spot(self, location: str, latitude: float, longitude: float, status: str) -> ParkingSpot:
        spot = ParkingSpot(location=location, latitude=latitude, longitude=longitude, status=status)
        self.db.add(spot)
        await self.db.commit()
        await self.db.refresh(spot)
        return spot

    async def update_spot(self, spot_id: int, **updates) -> Optional[ParkingSpot]:
        spot = await self.db.get(ParkingSpot, spot_id)
        if not spot:
            return None
        for k, v in updates.items():
            if v is not None:
                setattr(spot, k, v)
        await self.db.commit()
        return spot

    async def delete_spot(self, spot_id: int) -> Optional[ParkingSpot]:
        spot = await self.db.get(ParkingSpot, spot_id)
        if spot:
            await self.db.delete(spot)
            await self.db.commit()
        return spot

    async def get_spots_in_viewport(
        self,
        sw_lat: float,
        sw_lng: float,
        ne_lat: float,
        ne_lng: float,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> List[ParkingSpot]:
        q = select(ParkingSpot).where(
            ParkingSpot.latitude >= sw_lat,
            ParkingSpot.latitude <= ne_lat,
            ParkingSpot.longitude >= sw_lng,
            ParkingSpot.longitude <= ne_lng,
        )
        if status:
            q = q.where(ParkingSpot.status == status)
        q = q.order_by(ParkingSpot.last_updated.desc()).limit(limit)
        res = await self.db.execute(q)
        return res.scalars().all()

    async def get_spots_in_viewport_cached(
        self,
        sw_lat: float,
        sw_lng: float,
        ne_lat: float,
        ne_lng: float,
        status: Optional[str] = None,
    ) -> Tuple[List[ParkingSpot], bool]:
        geo_key = f"spots:geo:{status}" if status else "spots:geo:Available"
        center_lng = (sw_lng + ne_lng) / 2
        center_lat = (sw_lat + ne_lat) / 2
        radius_km = max(abs(ne_lat - sw_lat), abs(ne_lng - sw_lng)) * 111.32

        try:
            members = await redis_client.geosearch(
                geo_key,
                longitude=center_lng,
                latitude=center_lat,
                radius=radius_km,
                unit="km",
                sort="ASC",
                count=2000,
            )
        except Exception:
            return [], False

        if not members:
            return [], False

        ids = [sid for sid in (_member_to_id(m) for m in members) if sid is not None]
        if not ids:
            return [], False

        spots: List[ParkingSpot] = []
        for sid in ids:
            raw = await redis_client.hgetall(f"spot:{sid}")
            if not raw:
                continue
            m = {_s(k): _s(v) for k, v in raw.items()}
            try:
                pid = int(m.get("id", str(sid)))
                lat = float(m.get("latitude", "nan"))
                lng = float(m.get("longitude", "nan"))
                loc = m.get("location", "")
                st = m.get("status", "")
                lu = _parse_dt(m.get("last_updated"))
                if any(map(lambda x: x != x, [lat, lng])) or not st:
                    continue
                spots.append(ParkingSpot(
                    id=pid, latitude=lat, longitude=lng, location=loc, status=st, last_updated=lu
                ))
            except Exception:
                continue

        if not spots:
            return [], False
        return spots, True

    async def preload_spots_to_cache(self) -> None:
        """Warm Redis cache with ALL spots from DB on startup. Joins existing cache data."""
        logger.info("Preloading all spots into Redis cache...")
        all_spots = await self.get_all_spots()  # Grab full set from DB
        for spot in all_spots:
            try:
                # Upsert base hash (always, even if existing)
                await redis_client.hset(
                    f"spot:{spot.id}",
                    mapping={
                        "id": str(spot.id),
                        "latitude": "" if spot.latitude is None else str(spot.latitude),
                        "longitude": "" if spot.longitude is None else str(spot.longitude),
                        "location": spot.location,
                        "status": spot.status,
                        "last_updated": (
                            spot.last_updated.isoformat()
                            if spot.last_updated else ""
                        ),
                    },
                )
                # Add to status set (idempotent)
                await redis_client.sadd(f"spots:by_status:{spot.status}", spot.id)
                # Add to GEO set (if coords exist)
                if spot.longitude is not None and spot.latitude is not None:
                    await redis_client.execute_command(
                        "GEOADD", f"spots:geo:{spot.status}", spot.longitude, spot.latitude, f"spot_{spot.id}"
                    )
                logger.debug(f"Preloaded spot {spot.id} (status={spot.status}) to cache")
            except Exception as e:
                logger.error(f"Error preloading spot {spot.id}: {e}")

        logger.info(f"Cache preload complete: {len(all_spots)} spots indexed.")