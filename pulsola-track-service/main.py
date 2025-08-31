import sys

from granian import Granian
from granian.constants import Interfaces, Loops

from pulsola.tracks.config import TracksServiceConfig
from pulsola.tracks.core import server


def main() -> None:
    loop = Loops.asyncio if sys.platform == 'win32' else Loops.uvloop
    config = TracksServiceConfig()
    Granian(
        target=f'{server.__name__}:app',
        address='0.0.0.0',
        port=config.service_port,
        interface=Interfaces.ASGI,
        workers=config.service_workers,
        loop=loop,
        log_access=True,
    ).serve()


if __name__ == '__main__':
    main()
