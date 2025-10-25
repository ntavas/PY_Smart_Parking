import bcrypt
from app.repositories.user_repository import UserRepository

class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def login(self, email: str, password: str):
        """Authenticate user with email and password"""
        user = await self.user_repo.get_user_by_email(email)
        if not user:
            raise ValueError("Invalid email or password")
        
        # Verify password
        if not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
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
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        # Create user
        user = await self.user_repo.create_user(email, password_hash, full_name)
        return user

    async def update_user(self, user_id: int, **updates):
        # Hash password if provided
        if 'password' in updates and updates['password']:
            updates['password_hash'] = bcrypt.hashpw(updates['password'].encode(), bcrypt.gensalt()).decode()
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