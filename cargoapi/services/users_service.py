import collections
import uuid
from typing import Any, Optional

from fastapi import Depends, HTTPException, status
from sqlalchemy import Row
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from cargoapi.models.api.v1.users import User
from cargoapi.schemas.users import UserCreate
from cargoapi.utils.auth import JWTBearer, decodeJWT
from cargoapi.utils.password_hash import hash_password


class UserService:
    async def get_all_users(self, session: AsyncSession) -> collections.abc.Sequence[Row[tuple[User, Any]]]:
        statement = select(User)
        result = await session.execute(statement)
        return result.all()

    async def get_user_by_uid(self, user_uid: uuid.UUID, session: AsyncSession) -> Row[tuple[User, ...]]:
        statement = select(User).where(User.uid == user_uid)
        result = await session.execute(statement)
        user = result.scalar_one()
        return user if user is not None else None

    async def get_user(self, username: str, session: AsyncSession) -> Optional[Row[tuple[User]]]:
        statement = select(User).where(User.username == username)
        result = await session.execute(statement)
        user = result.first()
        return user if user is not None else None

    async def username_exists(self, username: str, session: AsyncSession) -> Optional[bool]:
        statement = select(User).where(User.username == username)
        result = await session.execute(statement)
        user = result.first()
        return True if user else None

    async def create_user(self, user_data: UserCreate, session: AsyncSession) -> Any:
        hashed_password = hash_password(user_data.password)
        user_data.password = hashed_password
        user_data_dict = user_data.model_dump()

        new_user = User(**user_data_dict)
        session.add(new_user)
        await session.commit()
        return new_user

    async def get_current_user_uid(self, token: str = Depends(JWTBearer())) -> User:
        """
        Get current user from JWT token
        """
        payload = decodeJWT(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid token or expired token',
            )
        user_uid = payload.get('sub')

        if not user_uid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid token or expired token',
            )
        return user_uid
