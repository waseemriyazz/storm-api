def chunk_string(s: str, chunk_size: int = 1024):
    """
    Yield successive chunks of the string `s` of size `chunk_size`.
    """
    for i in range(0, len(s), chunk_size):
        yield s[i : i + chunk_size]


def iter_json(json_str: str):

    for chunk in chunk_string(json_str, 1024):
        yield chunk


import json
from typing import Iterator, Any


def iter_json_dict(data: dict) -> Iterator[bytes]:
    """
    Yields parts of a JSON dict as a streaming response.
    Sends the initial '{', then each key-value pair, and ends with '}'.
    This avoids building the full JSON string in memory.
    """
    yield b"{"

    total = len(data)
    for idx, (key, value) in enumerate(data.items()):
        chunk = json.dumps(key) + ": " + json.dumps(value)
        if idx < total - 1:
            chunk += ", "
        yield chunk.encode("utf-8")

    yield b"}"
