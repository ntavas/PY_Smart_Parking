"""
user_router.py - User API Endpoints

Provides REST endpoints for:
- User registration and login
- User CRUD operations
- Managing user's favorite parking spots
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository
from app.dtos.user_dto import UserCreate, UserUpdate, UserResponse, UserLogin

router = APIRouter(prefix="/users", tags=["users"])

def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    repo = UserRepository(db)
    return UserService(repo)

@router.post("/login", response_model=UserResponse)
async def login(credentials: UserLogin, service: UserService = Depends(get_user_service)):
    try:
        return await service.login(credentials.email, credentials.password)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.get("/", response_model=list[UserResponse])
async def get_all_users(service: UserService = Depends(get_user_service)):
    return await service.get_all_users()

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, service: UserService = Depends(get_user_service)):
    try:
        return await service.get_user_by_id(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate, service: UserService = Depends(get_user_service)):
    return await service.create_user(user.email, user.password, user.full_name)

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, updates: UserUpdate, service: UserService = Depends(get_user_service)):
    try:
        return await service.update_user(user_id, **updates.dict(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{user_id}", response_model=UserResponse)
async def delete_user(user_id: int, service: UserService = Depends(get_user_service)):
    try:
        return await service.delete_user(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{user_id}/favorites/{spot_id}")
async def add_favorite(user_id: int, spot_id: int, service: UserService = Depends(get_user_service)):
    try:
        await service.add_favorite(user_id, spot_id)
        return {"message": "Favorite added"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{user_id}/favorites/{spot_id}")
async def remove_favorite(user_id: int, spot_id: int, service: UserService = Depends(get_user_service)):
    try:
        await service.remove_favorite(user_id, spot_id)
        return {"message": "Favorite removed"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{user_id}/favorites", response_model=list[int])
async def get_favorites(user_id: int, service: UserService = Depends(get_user_service)):
    return await service.get_favorites(user_id)
