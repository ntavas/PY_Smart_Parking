from __future__ import annotations

import logging
from decimal import Decimal
from datetime import datetime
from typing import Optional, Tuple, List, Dict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete
from app.models import ParkingSpot, PaidParking
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

    # --- NEW: fetch all paid prices into a dict[spot_id] = Decimal(price) ---
    async def _get_paid_prices_map(self) -> Dict[int, Decimal]:
        res = await self.db.execute(select(PaidParking.spot_id, PaidParking.price_per_hour))
        rows = res.all()
        return {int(spot_id): (price if isinstance(price, Decimal) else Decimal(str(price)))
                for (spot_id, price) in rows}

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
        spots = list(res.scalars().all())

        # Get paid prices for these spots
        paid_map = await self._get_paid_prices_map()

        # Set price_per_hour for each spot
        for spot in spots:
            if spot.id in paid_map:
                spot.price_per_hour = paid_map[spot.id]
            else:
                spot.price_per_hour = None

        return spots

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
        logger.debug(f"Searching for spots in radius {radius_km}km around {center_lat}, {center_lng} ({geo_key})")
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
                price_per_hour = m.get("price_per_hour")

                if any(map(lambda x: x != x, [lat, lng])) or not st:
                    continue

                price = None
                if price_per_hour:
                    try:
                        price = Decimal(price_per_hour)
                    except:
                        price = None

                p = ParkingSpot(
                    id=pid,
                    latitude=lat,
                    longitude=lng,
                    location=loc,
                    status=st,
                    last_updated=lu,
                    price_per_hour=price
                )

                spots.append(p)
            except Exception:
                continue

        if not spots:
            return [], False
        return spots, True

    async def preload_spots_to_cache(self) -> None:
        """Warm Redis cache with ALL spots from DB on startup. Joins existing cache data."""
        logger.info("Preloading all spots into Redis cache...")
        all_spots = await self.get_all_spots()
        paid_map = await self._get_paid_prices_map()  # spot_id -> Decimal price

        # Optional: maintain a set of paid spot ids for quick filters
        # We'll rebuild it from scratch to stay consistent.
        try:
            await redis_client.delete("spots:paid")
        except Exception:
            pass

        for spot in all_spots:
            try:
                mapping = {
                    "id": str(spot.id),
                    "latitude": "" if spot.latitude is None else str(spot.latitude),
                    "longitude": "" if spot.longitude is None else str(spot.longitude),
                    "location": spot.location,
                    "status": spot.status,
                    "last_updated": (spot.last_updated.isoformat() if spot.last_updated else ""),
                }

                # NEW: if spot is paid, include the price in the hash and set membership
                if spot.id in paid_map:
                    price = paid_map[spot.id]
                    mapping["price_per_hour"] = str(price)
                    await redis_client.sadd("spots:paid", spot.id)

                await redis_client.hset(f"spot:{spot.id}", mapping=mapping)

                # Status set (idempotent)
                await redis_client.sadd(f"spots:by_status:{spot.status}", spot.id)

                # GEO (if coords exist)
                if spot.longitude is not None and spot.latitude is not None:
                    await redis_client.execute_command(
                        "GEOADD", f"spots:geo:{spot.status}", float(spot.longitude), float(spot.latitude), f"spot_{spot.id}"
                    )

                logger.debug(f"Preloaded spot {spot.id} (status={spot.status}, paid={'yes' if spot.id in paid_map else 'no'})")
            except Exception as e:
                logger.error(f"Error preloading spot {spot.id}: {e}")

        logger.info(f"Cache preload complete: {len(all_spots)} spots indexed.")

    # --- OPTIONAL: small helpers to upsert/remove price and keep Redis in sync ---

    async def upsert_paid_price(self, spot_id: int, price_per_hour: float) -> None:
        """Create or update the paid price for a spot and update Redis hash/set."""
        # Upsert DB
        exists = await self.db.get(PaidParking, spot_id)
        if exists:
            exists.price_per_hour = Decimal(str(price_per_hour))
        else:
            self.db.add(PaidParking(spot_id=spot_id, price_per_hour=Decimal(str(price_per_hour))))
        await self.db.commit()

        # Update Redis
        await redis_client.hset(f"spot:{spot_id}", mapping={"price_per_hour": str(price_per_hour)})
        await redis_client.sadd("spots:paid", spot_id)

    async def remove_paid_price(self, spot_id: int) -> None:
        """Remove paid price for a spot (free spot now) and update Redis hash/set."""
        # DB delete
        await self.db.execute(delete(PaidParking).where(PaidParking.spot_id == spot_id))
        await self.db.commit()

        # Redis cleanup
        await redis_client.hdel(f"spot:{spot_id}", "price_per_hour")
        await redis_client.srem("spots:paid", spot_id)

    async def get_distinct_locations(self) -> Tuple[List[str], Dict[str, List[str]]]:
        """ Fetches distinct cities and areas for search filters. """
        # Get all distinct non-null city/area pairs
        query = select(ParkingSpot.city, ParkingSpot.area).distinct().where(ParkingSpot.city != None, ParkingSpot.area != None)
        res = await self.db.execute(query)
        rows = res.all()

        cities = sorted(list(set(r[0] for r in rows)))
        areas: Dict[str, List[str]] = {city: [] for city in cities}
        for city, area in rows:
            if area not in areas[city]:
                areas[city].append(area)
        
        for city in areas:
            areas[city].sort()
            
        return cities, areas

    async def search_spots(
        self,
        city: str,
        area: str,
        is_free: Optional[bool] = None
    ) -> Optional[Tuple[int, float, float]]:
        """ Finds the first available spot matching criteria and returns its id and coordinates. """
        query = select(ParkingSpot.id, ParkingSpot.latitude, ParkingSpot.longitude).where(
            ParkingSpot.city == city,
            ParkingSpot.area == area,
            ParkingSpot.status == "Available"
        )

        if is_free is not None:
            if is_free:
                # It's free if it's NOT in the paid_parking table
                query = query.outerjoin(PaidParking).where(PaidParking.spot_id == None)
            else:
                # It's paid if it's IN the paid_parking table
                query = query.join(PaidParking)

        query = query.limit(1)
        res = await self.db.execute(query)
        result = res.first()

        return result if result else None
