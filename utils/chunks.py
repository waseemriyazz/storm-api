def chunk_string(s: str, chunk_size: int = 1024):
    """
    Yield successive chunks of the string `s` of size `chunk_size`.
    """
    for i in range(0, len(s), chunk_size):
        yield s[i : i + chunk_size]
