from typing import Optional

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from cargoapi.models.api.v1.users import User
from cargoapi.schemas.auth import Login
from cargoapi.utils.password_hash import hash_password, verify_password


class AuthService:
    async def get_user_by_credentials(self, login_data: Login, session: AsyncSession) -> Optional[User]:
        user = None
        hashed_password = hash_password(login_data.password)
        if verify_password(login_data.password, hashed_password):
            statement = select(User).where(
                User.username == login_data.username,
            )
            result = await session.execute(statement)
            user = result.scalars().first()
        return user if user else None
