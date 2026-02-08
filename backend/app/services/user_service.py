"""
user_service.py - User Business Logic

Handles user authentication, registration, and profile management.
Passwords are hashed using bcrypt before storage.
"""

from app.repositories.user_repository import UserRepository
from app.core.security import get_password_hash, verify_password

class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def login(self, email: str, password: str):
        """Authenticate user with email and password"""
        user = await self.user_repo.get_user_by_email(email)
        if not user:
            raise ValueError("Invalid email or password")
        
        # Verify password
        if not verify_password(password, user.password_hash):
            raise ValueError("Invalid email or password")
        
        return user

    async def get_all_users(self):
        return await self.user_repo.get_all_users()

    async def get_user_by_id(self, user_id: int):
        user = await self.user_repo.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        return user

    async def create_user(self, email: str, password: str, full_name: str):
        # Check if email exists
        existing = await self.user_repo.get_user_by_email(email)
        if existing:
            raise ValueError("Email already in use")

        # Hash password
        password_hash = get_password_hash(password)

        # Create user
        user = await self.user_repo.create_user(email, password_hash, full_name)
        return user

    async def update_user(self, user_id: int, **updates):
        # Hash password if provided
        if 'password' in updates and updates['password']:
            updates['password_hash'] = get_password_hash(updates['password'])
            del updates['password']

        # Check if email is being updated and if it already exists
        if 'email' in updates:
            existing = await self.user_repo.get_user_by_email(updates['email'])
            if existing and existing.id != user_id:
                raise ValueError("Email already in use")

        user = await self.user_repo.update_user(user_id, **updates)
        if not user:
            raise ValueError("User not found")
        return user

    async def delete_user(self, user_id: int):
        user = await self.user_repo.delete_user(user_id)
        if not user:
            raise ValueError("User not found")
        return user

    async def add_favorite(self, user_id: int, spot_id: int):
        await self.user_repo.add_favorite(user_id, spot_id)

    async def remove_favorite(self, user_id: int, spot_id: int):
        await self.user_repo.remove_favorite(user_id, spot_id)

    async def get_favorites(self, user_id: int):
        return await self.user_repo.get_favorites(user_id)