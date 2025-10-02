from app.database import get_db
from app.repositories.parking_repository import ParkingRepository
from app.services.parking_service import ParkingService
from app.dtos.parking_dto import ParkingSpotCreate, ParkingSpotResponse
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.parking_service import ParkingService
from app.repositories.parking_repository import ParkingRepository
from app.dtos.parking_dto import ParkingSpotCreate, ParkingSpotUpdate, ParkingSpotResponse
from app.dtos.parking_dto import ViewportResponse


router = APIRouter(prefix="/parking", tags=["parking"])

def get_parking_service(db: AsyncSession = Depends(get_db)) -> ParkingService:
    repo = ParkingRepository(db)
    return ParkingService(repo)

@router.get("/spots", response_model=list[ParkingSpotResponse])
async def get_all_spots(service: ParkingService = Depends(get_parking_service)):
    return await service.get_all_spots()

@router.get("/spots/{spot_id}", response_model=ParkingSpotResponse)
async def get_spot(spot_id: int, service: ParkingService = Depends(get_parking_service)):
    try:
        return await service.get_spot_by_id(spot_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/spots", response_model=ParkingSpotResponse)
async def create_spot(spot: ParkingSpotCreate, service: ParkingService = Depends(get_parking_service)):
    return await service.create_spot(spot.location, spot.latitude, spot.longitude, spot.status)

@router.put("/spots/{spot_id}", response_model=ParkingSpotResponse)
async def update_spot(spot_id: int, updates: ParkingSpotUpdate, service: ParkingService = Depends(get_parking_service)):
    try:
        return await service.update_spot(spot_id, **updates.dict(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/spots/{spot_id}", response_model=ParkingSpotResponse)
async def delete_spot(spot_id: int, service: ParkingService = Depends(get_parking_service)):
    try:
        return await service.delete_spot(spot_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
router = APIRouter()

@router.get("/spots", response_model=list[ParkingSpotResponse])
async def get_spots(db: AsyncSession = Depends(get_db)):
    repo = ParkingRepository(db)
    service = ParkingService(repo)
    spots = await service.get_all_spots()
    return [
        ParkingSpotResponse(
            id=spot.id,
            latitude=spot.latitude,
            longitude=spot.longitude,
            location=spot.location,
            status=spot.status,
            last_updated=spot.last_updated.isoformat() if spot.last_updated else None
        ) for spot in spots
    ]


@router.get("/spots/viewport", response_model=ViewportResponse)
async def get_spots_viewport(
        sw_lat: float = Query(..., alias="swLat", description="Southwest latitude"),
        sw_lng: float = Query(..., alias="swLng", description="Southwest longitude"),
        ne_lat: float = Query(..., alias="neLat", description="Northeast latitude"),
        ne_lng: float = Query(..., alias="neLng", description="Northeast longitude"),
        zoom: int = Query(None, description="Map zoom level"),
        status: str = Query(None, description="Optional status filter"),
        limit: int = Query(100, gt=0, le=500),
        db: AsyncSession = Depends(get_db)
):
    repo = ParkingRepository(db)
    service = ParkingService(repo)

    spots = await service.get_spots_in_viewport(sw_lat, sw_lng, ne_lat, ne_lng, status, limit)

    # Map to DTOs
    spot_dtos = [
        ParkingSpotResponse(
            id=spot.id,
            latitude=spot.latitude,
            longitude=spot.longitude,
            location=spot.location,
            status=spot.status,
            last_updated=spot.last_updated.isoformat() if spot.last_updated else None
        ) for spot in spots
    ]

    return ViewportResponse(spots=spot_dtos,
                            total=len(spot_dtos))  # For now, total is len(spots); could add COUNT query later