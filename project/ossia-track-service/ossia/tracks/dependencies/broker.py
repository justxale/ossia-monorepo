from faststream.rabbit import RabbitBroker

from ossia.tracks.routes.broker import router


def get_broker() -> RabbitBroker:
    return router.broker
