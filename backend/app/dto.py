from pydantic import BaseModel

# Request DTO
class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str

# Response DTO
class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    created_at: str  # Converted to string for JSON