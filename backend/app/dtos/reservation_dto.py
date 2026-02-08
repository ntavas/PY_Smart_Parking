"""
reservation_dto.py - Reservation Data Transfer Objects

Pydantic schemas for reservation-related API requests and responses.
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ReservationBase(BaseModel):
    user_id: int
    spot_id: int
    start_time: datetime
    end_time: Optional[datetime] = None

class ReservationCreate(BaseModel):
    user_id: int
    spot_id: int

class ReservationUpdate(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

from app.dtos.parking_dto import ParkingSpotResponse

class ReservationResponse(ReservationBase):
    id: int
    spot: ParkingSpotResponse

    class Config:
        from_attributes = True
