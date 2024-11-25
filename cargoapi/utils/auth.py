import collections
from datetime import datetime, timedelta
from typing import Any, Optional, Union

from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt as jost_jwt
from jwt import InvalidTokenError

from cargoapi.core.config import settings


def create_access_token(subject: Union[str, Any], expires_delta: Optional[int] = None) -> str:
    if expires_delta:
        expires_delta = datetime.utcnow() + timedelta(minutes=expires_delta)  # type: ignore[assignment]
    else:
        expires_delta = datetime.utcnow() + timedelta(  # type: ignore[assignment]
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        )

    to_encode = {'exp': expires_delta, 'sub': str(subject)}
    encoded_jwt = jost_jwt.encode(to_encode, settings.SECRET_KEY, settings.ALOGRITHM)
    return encoded_jwt


def create_refresh_token(subject: Union[str, Any], expires_delta: Optional[int] = None) -> str:
    if expires_delta:
        expires_delta = datetime.utcnow() + timedelta(minutes=expires_delta)  # type: ignore[assignment]
    else:
        expires_delta = datetime.utcnow() + timedelta(  # type: ignore[assignment]
            minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES,
        )

    to_encode = {'exp': expires_delta, 'sub': str(subject)}
    encoded_jwt = jost_jwt.encode(to_encode, settings.REFERSH_SECRET_KEY, settings.ALOGRITHM)
    return encoded_jwt


def decodeJWT(jwtoken: str) -> Optional[collections.abc.Mapping[Any, Any]]:
    try:
        payload = jost_jwt.decode(jwtoken, settings.SECRET_KEY, settings.ALOGRITHM)
        return payload
    except InvalidTokenError:
        return None


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:  # type: ignore[override]
        credentials: Optional[HTTPAuthorizationCredentials] = await super().__call__(request)
        if credentials:
            if not credentials.scheme == 'Bearer':
                raise HTTPException(status_code=403, detail='Invalid authentication scheme.')
            token = credentials.credentials
            if not self.verify_jwt(token):
                raise HTTPException(status_code=403, detail='Invalid token or expired token.')
            return token
        raise HTTPException(status_code=403, detail='Invalid authorization code.')

    def verify_jwt(self, jwtoken: str) -> bool:
        try:
            decodeJWT(jwtoken)
            return True
        except jost_jwt.ExpiredSignatureError:
            return False
        except jost_jwt.JWTError:
            return False
