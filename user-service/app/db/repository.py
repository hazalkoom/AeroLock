from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.db.models import User
from app.core.security import get_password_hash
import logging

logger = logging.getLogger(__name__)

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    async def get_user_by_id(self, user_id: str) -> User | None:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    async def create_user(self, email: str, password: str, first_name: str, last_name: str) -> tuple[bool, str | User]:
        """Hashes the password and saves the new user to the database."""
        try:
            hashed_pwd = await get_password_hash(password)
            new_user = User(
                email=email,
                password_hash=hashed_pwd,
                first_name=first_name,
                last_name=last_name
            )
            self.session.add(new_user)
            await self.session.commit()
            await self.session.refresh(new_user)
            
            return True, new_user
            
        except IntegrityError:
            await self.session.rollback()
            return False, "Email already registered."
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Database error during user creation: {e}")
            return False, "Internal database error."