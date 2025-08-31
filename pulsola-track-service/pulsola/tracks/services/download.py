import asyncio
import string
import sys
from collections.abc import AsyncGenerator

from aiobotocore.response import StreamingBody

VALID_CHARS = '-_.()' + string.ascii_letters + string.digits
CHUNK_SIZE = 512 * 1024  # 512 kb


async def create_files_zip(
        files_amount: int, streams_gen: AsyncGenerator[tuple[str, StreamingBody], None]
) -> AsyncGenerator[bytes, None]:
    proc = await asyncio.create_subprocess_shell(
        f'{sys.executable} -u zipper.py',
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
    )
    if not (proc.stdin and proc.stdout):
        return
    proc.stdin.write(f'{files_amount}'.encode())
    async for filename, body in streams_gen:
        proc.stdin.write(b'\x00')
        proc.stdin.write(filename.encode())
        proc.stdin.write(b'\x00')
        async for chunk in body.iter_chunks(CHUNK_SIZE):
            proc.stdin.write(chunk)
        await proc.stdin.drain()

    proc.stdin.write_eof()
    await proc.stdin.drain()
    proc.stdin.close()
    async for chunk in proc.stdout:
        yield chunk
    await proc.stdin.wait_closed()
