"""Event publishing abstraction. Swap MockKafkaPublisher for a real
kafka-python/confluent-kafka producer behind the same EventPublisher
interface; callers never depend on the concrete type.
"""
import logging
from typing import Protocol

logger = logging.getLogger("sandbox.events")


class EventPublisher(Protocol):
    def publish(self, topic: str, event: dict) -> None: ...


class MockKafkaPublisher:
    def publish(self, topic: str, event: dict) -> None:
        logger.info("Publishing event to topic '%s': %s", topic, event)
