from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.reservation_service import ReservationService
from app.repositories.reservation_repository import ReservationRepository
from app.dtos.reservation_dto import ReservationCreate, ReservationUpdate, ReservationResponse

router = APIRouter(prefix="/reservations", tags=["reservations"])

def get_reservation_service(db: AsyncSession = Depends(get_db)) -> ReservationService:
    repo = ReservationRepository(db)
    return ReservationService(repo)

@router.get("/", response_model=list[ReservationResponse])
async def get_all_reservations(service: ReservationService = Depends(get_reservation_service)):
    return await service.get_all_reservations()

@router.get("/{reservation_id}", response_model=ReservationResponse)
async def get_reservation(reservation_id: int, service: ReservationService = Depends(get_reservation_service)):
    try:
        return await service.get_reservation_by_id(reservation_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/user/{user_id}", response_model=list[ReservationResponse])
async def get_reservations_by_user(user_id: int, service: ReservationService = Depends(get_reservation_service)):
    return await service.get_reservations_by_user_id(user_id)

@router.get("/spot/{spot_id}", response_model=list[ReservationResponse])
async def get_reservations_by_spot(spot_id: int, service: ReservationService = Depends(get_reservation_service)):
    return await service.get_reservations_by_spot_id(spot_id)

@router.post("/", response_model=ReservationResponse)
async def create_reservation(reservation: ReservationCreate, service: ReservationService = Depends(get_reservation_service)):
    return await service.create_reservation(
        reservation.user_id, 
        reservation.spot_id, 
        reservation.start_time, 
        reservation.end_time
    )

@router.put("/{reservation_id}", response_model=ReservationResponse)
async def update_reservation(reservation_id: int, updates: ReservationUpdate, service: ReservationService = Depends(get_reservation_service)):
    try:
        return await service.update_reservation(reservation_id, **updates.dict(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{reservation_id}", response_model=ReservationResponse)
async def delete_reservation(reservation_id: int, service: ReservationService = Depends(get_reservation_service)):
    try:
        return await service.delete_reservation(reservation_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
