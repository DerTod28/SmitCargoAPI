import uuid
from datetime import date, datetime

from pydantic import BaseModel


class CargoType(BaseModel):
    uid: uuid.UUID
    name: str
    created_at: datetime
    updated_at: datetime


class CargoTariffResponse(BaseModel):
    uid: uuid.UUID
    tariff_date: date
    rate: float
    to_cargo_type_uid: uuid.UUID
    created_at: datetime
    updated_at: datetime


class CargoCalculateRate(BaseModel):
    tariff_date: date
    cargo_type_name: str
    total_price: int


class CargoTariffUpdate(BaseModel):
    rate: float
