import collections
import uuid
from datetime import datetime
from typing import Any, Optional

from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import select

from cargoapi.models.api.v1.cargos import CargoTariff, CargoType
from cargoapi.schemas.cargos import CargoCalculateRate, CargoTariffUpdate
from cargoapi.utils.exceptions import ApiExceptionsError


class CargoService:
    @classmethod
    async def get_all_cargos_tariff(
        cls,
        session: AsyncSession,
    ) -> collections.abc.Sequence[CargoTariff]:
        statement = select(CargoTariff)
        result = await session.execute(statement)
        return result.scalars().all()

    @classmethod
    async def get_cargo_tariff(
        cls,
        cargo_uid: uuid.UUID,
        session: AsyncSession,
    ) -> Optional[CargoTariff]:
        statement = select(CargoTariff).where(CargoTariff.uid == cargo_uid)
        result = await session.execute(statement)
        return result.scalars().one_or_none()

    @classmethod
    async def get_cargo_tariff_by_date_and_type(
        cls,
        new_cargo_tariffs: CargoCalculateRate,
        session: AsyncSession,
    ) -> Optional[CargoTariff]:
        statement = (
            select(CargoTariff)
            .join(CargoType, CargoTariff.to_cargo_type_uid == CargoType.uid)  # type: ignore[arg-type]
            .where(
                CargoTariff.tariff_date == new_cargo_tariffs.tariff_date,
                CargoType.name == new_cargo_tariffs.cargo_type_name,
            )
        )
        result = await session.execute(statement)
        return result.scalars().one_or_none()

    @classmethod
    async def update_cargo_tariff(
        cls,
        cargo_uid: uuid.UUID,
        cargo_update_data: CargoTariffUpdate,
        session: AsyncSession,
    ) -> Optional[CargoTariff]:
        cargo_tariff = await cls.get_cargo_tariff(cargo_uid, session)
        if cargo_tariff:
            cargo_tariff.rate = cargo_update_data.rate
            cargo_tariff.updated_at = datetime.now()

            session.add(cargo_tariff)
            await session.commit()
            await session.refresh(cargo_tariff)

        return cargo_tariff

    @classmethod
    async def delete_cargo_tariff(
        cls,
        cargo_uid: uuid.UUID,
        session: AsyncSession,
    ) -> None:
        cargo_tariff = await cls.get_cargo_tariff(cargo_uid, session)
        if not cargo_tariff:
            raise ApiExceptionsError.not_found_404(detail='Cargo tariff not found')
        await session.delete(cargo_tariff)
        await session.commit()

    @classmethod
    async def upload_json_cargo_tariffs(
        cls,
        new_cargo_tariffs_json: dict[str, Any],
        session: AsyncSession,
    ) -> Any:
        """
        Uploads cargo tariffs from a JSON object, creating or updating CargoType and CargoTariff records.

        Args:
            new_cargo_tariffs_json (dict): JSON object containing cargo tariffs data.
            session (AsyncSession): Database session.

        Returns:
            dict: Summary of created and updated records.
        """
        try:
            created_types = 0
            updated_types = 0
            created_tariffs = 0
            updated_tariffs = 0

            for date_str, tariffs in new_cargo_tariffs_json.items():
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()

                for tariff in tariffs:
                    cargo_type_name = tariff['cargo_type']
                    rate = float(tariff['rate'])

                    cargo_type_query = await session.execute(
                        select(CargoType).where(CargoType.name == cargo_type_name),
                    )
                    cargo_type = cargo_type_query.scalars().first()

                    if not cargo_type:
                        cargo_type = CargoType(name=cargo_type_name)
                        session.add(cargo_type)
                        await session.flush()
                        created_types += 1
                    else:
                        updated_types += 1

                    tariff_query = await session.execute(
                        select(CargoTariff).where(
                            CargoTariff.tariff_date == date_obj,
                            CargoTariff.to_cargo_type_uid == cargo_type.uid,
                        ),
                    )
                    existing_tariff = tariff_query.scalars().first()

                    if not existing_tariff:
                        new_tariff = CargoTariff(
                            tariff_date=date_obj,
                            rate=rate,
                            to_cargo_type_uid=cargo_type.uid,
                        )
                        session.add(new_tariff)
                        created_tariffs += 1
                    else:
                        existing_tariff.rate = rate
                        existing_tariff.updated_at = datetime.now()
                        updated_tariffs += 1

            await session.commit()
            return {
                'created_types': created_types,
                'updated_types': updated_types,
                'created_tariffs': created_tariffs,
                'updated_tariffs': updated_tariffs,
            }
        except Exception as e:  # noqa: B902, F841
            await session.rollback()
            return None

    @classmethod
    async def calculate_summary_cargo_price(
        cls,
        cargo_rate: float,
        total_price: int,
    ) -> Any:
        cargo_calculated_result = total_price * cargo_rate
        return cargo_calculated_result
