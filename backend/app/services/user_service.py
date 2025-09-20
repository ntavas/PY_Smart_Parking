import bcrypt
from app.repositories.user_repository import UserRepository

class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

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