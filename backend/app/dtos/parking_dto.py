from pydantic import BaseModel
from typing import Optional

class ParkingSpotCreate(BaseModel):
    location: str
    latitude: float
    longitude: float
    status: Optional[str] = "Available"

class ParkingSpotUpdate(BaseModel):
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    status: Optional[str] = None

class ParkingSpotResponse(BaseModel):
    id: int
    latitude: float
    longitude: float
    location: str
    status: str
    last_updated: str | None

class SpotStatusLogCreate(BaseModel):
    spot_id: int
    status: str

class SpotStatusLogResponse(BaseModel):
    id: int
    spot_id: int
    status: str
    timestamp: str

    class Config:
        from_attributes = True