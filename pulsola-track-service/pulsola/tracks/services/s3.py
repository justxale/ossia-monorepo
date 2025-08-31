import enum
from types import TracebackType

import aioboto3

try:
    from types_aiobotocore_s3 import S3Client
except ImportError:
    import typing

    # In prod env we don't install any types packages, so
    type S3Client = typing.Any  # type: ignore[no-redef]

from pulsola.tracks.config import TracksServiceConfig

config = TracksServiceConfig()


class Buckets(enum.StrEnum):
    COVERS = 'covers'
    BUFFER = 'buffer'
    RAW_TRACKS = 'flacraw'
    OGG_96 = 'ogg96'
    OGG_160 = 'ogg160'
    OGG_320 = 'ogg320'
    LOGS = 'logs'

    @classmethod
    def ogg_buckets(cls) -> tuple['Buckets', 'Buckets', 'Buckets']:
        return cls.OGG_96, cls.OGG_160, cls.OGG_320

    @classmethod
    def all_buckets(cls) -> tuple['Buckets', ...]:
        return (
            cls.COVERS,
            cls.BUFFER,
            cls.RAW_TRACKS,
            cls.OGG_96,
            cls.OGG_160,
            cls.OGG_320,
            cls.LOGS,
        )


class S3Service:
    client: S3Client | None = None

    def __init__(self) -> None:
        self.endpoint_url = config.s3_url
        self.session = aioboto3.Session(
            aws_access_key_id=config.s3_access_key,
            aws_secret_access_key=config.s3_secret_key,
        )

    async def __aenter__(self) -> S3Client:
        self.client: S3Client = self.session.client(
            's3', endpoint_url=self.endpoint_url
        )  # type: ignore[assignment]
        if not self.client:
            raise ConnectionError('Cannot connect to S3')
        return await self.client.__aenter__()

    async def __aexit__(
            self,
            exc_type: type[BaseException] | None,
            exc_val: BaseException | None,
            exc_tb: TracebackType | None,
    ) -> None:
        if self.client:
            await self.client.__aexit__(exc_type, exc_val, exc_tb)
            self.client = None
