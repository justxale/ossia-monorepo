import asyncio
import enum
import io
from typing import BinaryIO

from PIL import Image

from ossia.tracks.services.s3 import Buckets, S3Service


class CoverFormats(enum.StrEnum):
    PNG = 'PNG'
    JPEG = 'JPEG'


SIZES = (256, 512, 1024, 2048, 3000)


def _crop(img: Image.Image) -> Image.Image:
    crop_len = min(img.size)
    return img.crop(
        (
            (img.width - crop_len) // 2,
            (img.height - crop_len) // 2,
            (img.width + crop_len) // 2,
            (img.height + crop_len) // 2,
        )
    )


async def _upload_cover(file: BinaryIO, key: str) -> None:
    async with S3Service() as s3:
        await s3.upload_fileobj(file, Bucket=Buckets.COVERS, Key=key)


def probe_cover(file: BinaryIO) -> str | None:
    img = Image.open(file)
    res = img.format
    img.close()
    return res


async def process_cover(file: str, track_id: str) -> None:
    img = Image.open(file, formats=(CoverFormats.PNG, CoverFormats.JPEG))
    img = _crop(img)  # type: ignore[assignment]
    async with asyncio.TaskGroup() as tg:
        for size in SIZES:
            key = f'{track_id}/cover{size}.jpg'
            out_file = io.BytesIO()
            img.resize((size, size)).save(out_file, format=CoverFormats.JPEG)
            tg.create_task(_upload_cover(out_file, key=key))
    img.close()
