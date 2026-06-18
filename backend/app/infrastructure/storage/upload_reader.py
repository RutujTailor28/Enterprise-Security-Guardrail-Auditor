"""Upload streaming helpers."""

from fastapi import UploadFile

from app.api.exceptions import PayloadTooLargeError

CHUNK_SIZE = 64 * 1024


async def read_upload_with_limit(upload: UploadFile, max_bytes: int) -> bytes:
    """Read an upload in chunks, rejecting bodies larger than max_bytes."""
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = await upload.read(CHUNK_SIZE)
        if not chunk:
            break
        total += len(chunk)
        if total > max_bytes:
            raise PayloadTooLargeError(
                f"File exceeds maximum size of {max_bytes} bytes"
            )
        chunks.append(chunk)
    return b"".join(chunks)
