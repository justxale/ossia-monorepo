import sys

from granian import Granian
from granian.constants import Interfaces, Loops

from pulsola.sync.config import SyncServiceConfig
from pulsola.sync.core import server


def main():
    loop = Loops.asyncio if sys.platform == 'win32' else Loops.uvloop
    config = SyncServiceConfig()
    Granian(
        target=f"{server.__name__}:app", address='0.0.0.0', port=config.service_port,
        interface=Interfaces.ASGI, workers=config.service_workers, loop=loop
    ).serve()


if __name__ == '__main__':
    main()
