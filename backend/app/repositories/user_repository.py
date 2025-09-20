from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import User

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, email: str, password_hash: str, full_name: str):
        new_user = User(email=email, password_hash=password_hash, full_name=full_name)
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def get_user_by_email(self, email: str):
        query = select(User).where(User.email == email)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()