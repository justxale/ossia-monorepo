from faststream.rabbit import RabbitBroker

from pulsola.sync.routes.broker import router


def get_broker() -> RabbitBroker:
    return router.broker
