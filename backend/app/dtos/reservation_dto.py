from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ReservationBase(BaseModel):
    user_id: int
    spot_id: int
    start_time: datetime
    end_time: Optional[datetime] = None

class ReservationCreate(ReservationBase):
    pass

class ReservationUpdate(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

class ReservationResponse(ReservationBase):
    id: int

    class Config:
        from_attributes = True
