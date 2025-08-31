import sys
import tempfile
import zipfile

MAX_SIZE = 10 * 1024 * 1024  # 10 MB


def create_zip():
    with tempfile.SpooledTemporaryFile(MAX_SIZE, 'wb') as buffer:
        z = zipfile.ZipFile(buffer, 'w', compression=zipfile.ZIP_DEFLATED)
        amount = int(sys.stdin.buffer.read(1))
        sys.stdin.buffer.seek(1)
        data = sys.stdin.buffer.read().strip().split(b'\x00')
        for _ in range(amount):
            file_bytes = data.pop()
            filename = data.pop().decode()
            z.writestr(filename, file_bytes)
        z.close()
        for chunk in buffer:
            sys.stdout.buffer.write(chunk)


if __name__ == '__main__':
    create_zip()
