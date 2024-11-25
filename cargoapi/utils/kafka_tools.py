import asyncio
import json
from typing import Any

from aiokafka import AIOKafkaProducer

from cargoapi.core.config import settings


class KafkaProducerService:
    def __init__(self, bootstrap_servers: str):
        self._producer = AIOKafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        )

    async def start(self) -> None:
        """Start the Kafka producer."""
        # Ensure we are using the correct event loop
        asyncio.get_event_loop()
        await self._producer.start()

    async def stop(self) -> None:
        """Stop the Kafka producer."""
        await self._producer.stop()

    async def send_message(self, topic: str, message: dict[str, Any]) -> None:
        """Send a message to a Kafka topic."""
        await self._producer.send_and_wait(topic, message)


kafka_producer = KafkaProducerService(bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS)
