import uuid
from datetime import datetime

from pydantic import BaseModel


class CurrentUser(BaseModel):
    uid: uuid.UUID
    username: str
    created_at: datetime


class UserCreate(BaseModel):
    username: str
    password: str
