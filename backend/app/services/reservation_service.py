from app.repositories.reservation_repository import ReservationRepository
from datetime import datetime
from typing import Optional

class ReservationService:
    def __init__(self, repo: ReservationRepository):
        self.repo = repo

    async def get_all_reservations(self):
        return await self.repo.get_all_reservations()

    async def get_reservation_by_id(self, reservation_id: int):
        reservation = await self.repo.get_reservation_by_id(reservation_id)
        if not reservation:
            raise ValueError("Reservation not found")
        return reservation

    async def get_reservations_by_user_id(self, user_id: int):
        return await self.repo.get_reservations_by_user_id(user_id)

    async def get_reservations_by_spot_id(self, spot_id: int):
        return await self.repo.get_reservations_by_spot_id(spot_id)

    async def create_reservation(self, user_id: int, spot_id: int, start_time: datetime, end_time: Optional[datetime] = None):
        return await self.repo.create_reservation(user_id, spot_id, start_time, end_time)

    async def update_reservation(self, reservation_id: int, **updates):
        reservation = await self.repo.update_reservation(reservation_id, **updates)
        if not reservation:
            raise ValueError("Reservation not found")
        return reservation

    async def delete_reservation(self, reservation_id: int):
        reservation = await self.repo.delete_reservation(reservation_id)
        if not reservation:
            raise ValueError("Reservation not found")
        return reservation
