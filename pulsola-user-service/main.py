import sys

from granian import Granian
from granian.constants import Interfaces, Loops

from pulsola.users.config import UserServiceConfig
from pulsola.users.core import server
from pulsola.users.core.server import app

if __name__ == '__main__':
    loop = Loops.asyncio if sys.platform == 'win32' else Loops.uvloop

    config = UserServiceConfig()
    Granian(
        target=f'{server.__name__}:app',
        address='0.0.0.0',
        port=config.service_port,
        interface=Interfaces.ASGI,
        # workers=config.service_workers,
        loop=loop,
        log_access=True,
    ).serve()
