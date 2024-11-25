import uuid
from datetime import date, datetime

import sqlalchemy.dialects.postgresql as pg
from sqlalchemy import Column, Date, Float, ForeignKey, String
from sqlmodel import Field, Relationship, SQLModel


class CargoType(SQLModel, table=True):
    __tablename__ = 'cargo_types'

    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4,
        ),
    )
    name: str = Field(
        sa_column=Column(
            String,
            nullable=False,
            unique=True,
        ),
    )
    tariffs: list['CargoTariff'] = Relationship(back_populates='cargo_type')
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))

    def __repr__(self) -> str:
        return f'<Cargo Type - {self.name}>'


class CargoTariff(SQLModel, table=True):
    __tablename__ = 'cargo_tariffs'

    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4,
        ),
    )
    tariff_date: date = Field(
        sa_column=Column(
            Date,
            nullable=False,
        ),
    )
    rate: float = Field(
        sa_column=Column(
            Float,
            nullable=False,
        ),
    )
    to_cargo_type_uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, ForeignKey('cargo_types.uid'), nullable=False),
    )
    cargo_type: CargoType = Relationship(back_populates='tariffs')
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))

    def __repr__(self) -> str:
        return f'<Cargo Tariff - {self.cargo_type.name, self.tariff_date, self.rate}>'
