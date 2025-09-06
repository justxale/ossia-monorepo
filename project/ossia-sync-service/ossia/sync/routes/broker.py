from faststream.rabbit import RabbitBroker
from faststream.rabbit.fastapi import RabbitRouter

from ossia.sync.config import SyncServiceConfig

router = RabbitRouter(SyncServiceConfig().rabbit_dsn)


def get_broker() -> RabbitBroker:
    return router.broker
