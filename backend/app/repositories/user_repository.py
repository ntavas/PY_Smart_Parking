from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import User
from typing import List, Optional

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_users(self) -> List[User]:
        result = await self.db.execute(select(User))
        return result.scalars().all()

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        return await self.db.get(User, user_id)

    async def get_user_by_email(self, email: str) -> Optional[User]:
        query = select(User).where(User.email == email)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_user(self, email: str, password_hash: str, full_name: str) -> User:
        new_user = User(email=email, password_hash=password_hash, full_name=full_name)
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def update_user(self, user_id: int, **updates) -> Optional[User]:
        user = await self.db.get(User, user_id)
        if not user:
            return None
        for key, value in updates.items():
            if value is not None:
                setattr(user, key, value)
        await self.db.commit()
        return user

    async def delete_user(self, user_id: int) -> Optional[User]:
        user = await self.db.get(User, user_id)
        if user:
            await self.db.delete(user)
            await self.db.commit()
        return user