import asyncio

from fastapi import FastAPI

from cargoapi.database import init_db
from cargoapi.router import api_router_v1

app = FastAPI(
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    redoc_url='/api/redoc',
)

app.include_router(api_router_v1)


@app.on_event('startup')
async def startup_event() -> None:
    from cargoapi.utils.kafka_tools import kafka_producer

    await init_db()
    asyncio.get_event_loop()
    await kafka_producer.start()


@app.on_event('shutdown')
async def shutdown_event() -> None:
    from cargoapi.utils.kafka_tools import kafka_producer

    """Shutdown Kafka producer when the application stops."""
    await kafka_producer.stop()
