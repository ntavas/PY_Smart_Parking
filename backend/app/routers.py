from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dto import UserCreate, UserResponse
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService

router = APIRouter()


@router.post("/users", response_model=UserResponse)
async def create_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    repo = UserRepository(db)
    service = UserService(repo)

    try:
        user = await service.create_user(user_data.email, user_data.password, user_data.full_name)
        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            created_at=user.created_at.isoformat()  # Convert to string
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))