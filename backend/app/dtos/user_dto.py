from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Request DTO
class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str

# Update DTO
class UserUpdate(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None
    full_name: Optional[str] = None

# Response DTO
class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    created_at: datetime

    class Config:
        from_attributes = True