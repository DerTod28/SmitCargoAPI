import collections
import datetime
import json
import uuid
from typing import Any, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from cargoapi.core.config import settings
from cargoapi.database import get_session
from cargoapi.models.api.v1.cargos import CargoTariff
from cargoapi.schemas.cargos import CargoCalculateRate, CargoTariffResponse, CargoTariffUpdate
from cargoapi.services.cargos_service import CargoService
from cargoapi.services.users_service import UserService
from cargoapi.utils.exceptions import ApiExceptionsError

router = APIRouter(
    prefix='/cargos',
    tags=['cargo'],
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')
cargo_service = CargoService()
user_service = UserService()


# /api/v1/cargos/ - Получение всех тарифов страхования
@router.get('/', response_model=list[CargoTariffResponse], description='Получение всех тарифов страхования')
async def get_all_cargos(
    session: AsyncSession = Depends(get_session),
) -> collections.abc.Sequence[Any]:
    cargos_tariff = await cargo_service.get_all_cargos_tariff(session)
    return cargos_tariff


# /api/v1/cargos/<uuid:UUID>/ - Получение подробной информации о тарифе
@router.get(
    '/{cargo_uid}',
    response_model=CargoTariffResponse,
    description='Получение подробной информации о тарифе по UUID',
)
async def get_cargo(
    cargo_uid: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> Optional[CargoTariff]:
    cargo_tariff = await cargo_service.get_cargo_tariff(cargo_uid, session)
    if not cargo_tariff:
        raise ApiExceptionsError.not_found_404(detail='Cargo tariff not found')
    return cargo_tariff


# /api/v1/cargos/<uuid:UUID>/ - Обновление тарифа
@router.put(
    '/{cargo_uid}',
    response_model=CargoTariffResponse,
    description='Обновление тарифа по UUID',
)
async def update_cargo(
    cargo_uid: uuid.UUID,
    cargo_update_data: CargoTariffUpdate,
    current_user_uid: uuid.UUID = Depends(user_service.get_current_user_uid),
    session: AsyncSession = Depends(get_session),
) -> Optional[CargoTariff]:
    existing_cargo_tariff = await cargo_service.get_cargo_tariff(cargo_uid, session)
    if not existing_cargo_tariff:
        raise ApiExceptionsError.not_found_404(detail='Cargo tariff not found')

    updated_cargo_tariff = await cargo_service.update_cargo_tariff(cargo_uid, cargo_update_data, session)
    try:
        from cargoapi.utils.kafka_tools import kafka_producer

        await kafka_producer.send_message(
            settings.KAFKA_TOPIC,
            {
                'message': {
                    'user_uid': str(current_user_uid),
                    'action': 'UPDATE',
                    'timestamp': str(datetime.datetime.now()),
                },
            },
        )
    except Exception as e:  # noqa: B902
        raise HTTPException(status_code=500, detail=f'Error sending message: {str(e)}')

    return updated_cargo_tariff


# # /api/v1/cargos/<uuid:UUID>/ - Удаление тарифа
@router.delete(
    '/{cargo_uid}',
    response_model=dict,
    description='Удаление тарифа по UUID',
)
async def delete_cargo(
    cargo_uid: uuid.UUID,
    current_user_uid: uuid.UUID = Depends(user_service.get_current_user_uid),
    session: AsyncSession = Depends(get_session),
) -> Optional[dict[str, Any]]:
    cargo_tariff = await cargo_service.get_cargo_tariff(cargo_uid, session)
    if not cargo_tariff:
        raise ApiExceptionsError.not_found_404(detail='Cargo tariff not found')

    await cargo_service.delete_cargo_tariff(cargo_uid, session)
    try:
        from cargoapi.utils.kafka_tools import kafka_producer

        await kafka_producer.send_message(
            settings.KAFKA_TOPIC,
            {
                'message': {
                    'user_uid': str(current_user_uid),
                    'action': 'DELETE',
                    'timestamp': str(datetime.datetime.now()),
                },
            },
        )
    except Exception as e:  # noqa: B902
        raise HTTPException(status_code=500, detail=f'Error sending message: {str(e)}')
    return {
        'detail': 'Cargo tariff deleted successfully.',
        'error': None,
        'result': None,
    }


# /api/v1/cargos/load/ - Загрузка тарифов из json файла
@router.post('/load', description='Загрузка тарифов JSON файлом')
async def load_cargos(
    upload_file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    cargo_tariffs_json_data = json.load(upload_file.file)
    cargo_tariff_upload_result = await cargo_service.upload_json_cargo_tariffs(cargo_tariffs_json_data, session)
    if not cargo_tariff_upload_result:
        return {
            'detail': 'Upload was failed.',
            'error': 'During the upload some error was occurred',
            'result': None,
        }
    return {
        'detail': 'Cargo tariffs successfully uploaded.',
        'error': None,
        'result': cargo_tariff_upload_result,
    }


# /api/v1/cargos/calculate/ - Расчет стоимости страхования по заданным данным
@router.post('/calculate', description='Загрузка тарифов')
async def calculate_cargos(
    cargo_calculate_data: CargoCalculateRate,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    cargo_tariff = await cargo_service.get_cargo_tariff_by_date_and_type(cargo_calculate_data, session)
    if not cargo_tariff:
        raise ApiExceptionsError.not_found_404(detail='Cargo tariff was not found')
    cargo_calculate_result = await cargo_service.calculate_summary_cargo_price(
        cargo_tariff.rate,
        cargo_calculate_data.total_price,
    )
    return {
        'detail': 'Cargo tariffs was successfully calculated.',
        'error': None,
        'result': cargo_calculate_result,
    }
