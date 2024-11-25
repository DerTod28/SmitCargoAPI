from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from cargoapi.database import get_session
from cargoapi.schemas.auth import Login
from cargoapi.services.auth_service import AuthService
from cargoapi.utils.auth import create_access_token, create_refresh_token
from cargoapi.utils.exceptions import ApiExceptionsError

router = APIRouter(
    prefix='/auth',
    tags=['auth'],
)

auth_service = AuthService()


# /api/v1/auth/login/ - Обмен логина/пароля на токены
@router.post('/login')
async def login(login_data: Login, session: AsyncSession = Depends(get_session)) -> dict[str, str]:
    user_verified = await auth_service.get_user_by_credentials(login_data, session)  # type: ignore[arg-type]
    if not user_verified:
        raise ApiExceptionsError.bad_request_400(detail='Bad username or password')
    token = create_access_token(str(user_verified.uid))
    refresh = create_refresh_token(str(user_verified.uid))
    return {'access_token': token, 'token_type': 'bearer', 'refresh_token': refresh, 'user_uid': str(user_verified.uid)}
